"""
Roda o eval completo sobre o golden dataset e mostra os resultados.

    python run_evals.py                                   # config padrão (igual ao módulo 4)
    python run_evals.py --chunk-size 500 --k 5            # muda UMA coisa e compara
    python run_evals.py --prompt loose                    # prompt solto -> veja a Faithfulness cair
    python run_evals.py --limit 5 --skip-ragas            # rodada rápida/barata

Fluxo:  golden dataset -> RAG -> [código | LLM-judge | RAGAS] -> quality gate -> comparação com a rodada anterior
"""
import argparse
import json
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table

from config import ACTIONS, GOLDEN_DATASET_PATH, HUMAN_LABELS_PATH, RESULTS_DIR, THRESHOLDS, resolve_judge
from evaluators.code_evals import run_code_checks
from evaluators.llm_judge import calibrate, judge_answer, load_human_labels
from rag_system import RAGConfig, RAGSystem

console = Console()
RAGAS_METRICS = ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]


def load_dataset(limit: int | None, category: str | None) -> list[dict]:
    rows = [json.loads(line) for line in GOLDEN_DATASET_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if category:
        rows = [r for r in rows if r["category"] == category]
    return rows[:limit] if limit else rows


def mean(values) -> float | None:
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


# ---------------------------------------------------------------------------
# 1. Gerar respostas
# ---------------------------------------------------------------------------
def answer_with_retry(rag: RAGSystem, question: str, attempts: int = 4):
    """APIs gratuitas devolvem 503/429 de vez em quando; um erro não pode derrubar 20 perguntas."""
    for attempt in range(1, attempts + 1):
        try:
            return rag.answer(question)
        except Exception as exc:
            if attempt == attempts:
                raise
            wait = 15 * attempt
            print(f"[yellow]  {type(exc).__name__} (tentativa {attempt}/{attempts}), aguardando {wait}s[/yellow]")
            time.sleep(wait)


def generate_answers(rag: RAGSystem, dataset: list[dict]) -> list[dict]:
    rows = []
    with console.status("") as status:
        for i, sample in enumerate(dataset, 1):
            status.update(f"[cyan]RAG respondendo {i}/{len(dataset)}: {sample['user_input']}")
            result = answer_with_retry(rag, sample["user_input"])
            rows.append({**sample, "response": result.response, "retrieved_contexts": result.retrieved_contexts})
    return rows


# ---------------------------------------------------------------------------
# 2. Avaliar (os três tipos de avaliador, do mais barato ao mais caro)
# ---------------------------------------------------------------------------
def evaluate_rows(rows: list[dict], skip_judge: bool, skip_ragas: bool) -> str | None:
    # 2a. Código: grátis, roda sempre
    for row in rows:
        row["code_checks"] = run_code_checks(row, row["response"])
        row["code_pass_rate"] = mean(row["code_checks"].values())

    if skip_judge and skip_ragas:
        return None
    judge = resolve_judge()
    print(f"Juiz: [bold]{judge.name}[/bold] (temperatura 0)")

    # 2b. LLM-as-judge com rubrica
    if not skip_judge:
        judge_chat = judge.as_langchain()
        with console.status("") as status:
            for i, row in enumerate(rows, 1):
                status.update(f"[magenta]Juiz avaliando {i}/{len(rows)}")
                try:
                    verdict = judge_answer(judge_chat, row["user_input"], row["reference"],
                                           row["retrieved_contexts"], row["response"])
                    row["judge_score"], row["judge_reasoning"] = verdict.nota, verdict.raciocinio
                except Exception as exc:  # juiz local pequeno às vezes quebra o JSON
                    row["judge_score"], row["judge_reasoning"] = None, f"erro: {exc}"

    # 2c. RAGAS (importado aqui porque é a parte mais pesada)
    if not skip_ragas:
        from evaluators.ragas_metrics import run_ragas
        with console.status("[blue]RAGAS calculando as 4 métricas..."):
            for row, scores in zip(rows, run_ragas(rows, judge)):
                row.update(scores)

    return judge.name


# ---------------------------------------------------------------------------
# 3. Relatórios
# ---------------------------------------------------------------------------
def fmt(value, threshold=None) -> str:
    if value is None:
        return "[dim]-[/dim]"
    text = f"{value:.2f}"
    if threshold is None:
        return text
    return f"[green]{text}[/green]" if value >= threshold else f"[red]{text}[/red]"


def print_per_question(rows: list[dict]):
    table = Table(title="Resultado por pergunta", show_lines=False)
    for col in ["id", "categoria", "código", "juiz", "ctx_prec", "ctx_rec", "faith", "relev", "resposta"]:
        table.add_column(col, overflow="fold")
    for r in rows:
        failed = [k for k, ok in r["code_checks"].items() if not ok]
        code = "[green]ok[/green]" if not failed else "[red]" + ",".join(failed) + "[/red]"
        table.add_row(
            r["id"], r["category"], code,
            str(r.get("judge_score") or "-"),
            *(fmt(r.get(m), THRESHOLDS[m]) for m in RAGAS_METRICS),
            r["response"][:70].replace("\n", " "),
        )
    console.print(table)


def summarize(rows: list[dict]) -> dict:
    summary = {m: mean(r.get(m) for r in rows) for m in RAGAS_METRICS}
    summary["judge_score"] = mean(r.get("judge_score") for r in rows)
    summary["code_checks"] = mean(ok for r in rows for ok in r["code_checks"].values())
    return summary


def print_by_category(rows: list[dict]):
    """A média geral esconde problemas: 'sem_resposta' pode estar em 0 e o total em 0.8."""
    groups = defaultdict(list)
    for r in rows:
        groups[r["category"]].append(r)

    table = Table(title="Por categoria (onde o sistema quebra?)")
    for col in ["categoria", "n", "código", "juiz", *RAGAS_METRICS]:
        table.add_column(col)
    for cat, items in groups.items():
        s = summarize(items)
        table.add_row(cat, str(len(items)), fmt(s["code_checks"], THRESHOLDS["code_checks"]),
                      fmt(s["judge_score"], THRESHOLDS["judge_score"]),
                      *(fmt(s[m], THRESHOLDS[m]) for m in RAGAS_METRICS))
    console.print(table)


def quality_gate(summary: dict) -> bool:
    """Equivalente ao 'assert' do pytest, mas sobre a MÉDIA e com limite."""
    table = Table(title="Quality gate")
    for col in ["métrica", "média", "limite", "status"]:
        table.add_column(col)

    failures = []
    for metric, threshold in THRESHOLDS.items():
        value = summary.get(metric)
        if value is None:
            table.add_row(metric, "-", f"{threshold}", "[dim]não rodou[/dim]")
            continue
        ok = value >= threshold
        failures += [] if ok else [metric]
        table.add_row(metric, f"{value:.2f}", f"{threshold}", "[green]PASSOU[/green]" if ok else "[red]FALHOU[/red]")
    console.print(table)

    # Nota baixa -> ação (tabela "Como cada nota vira uma ação")
    for metric in failures:
        cause, action = ACTIONS[metric]
        print(f"[red]x {metric}[/red]: {cause}  ->  [bold]{action}[/bold]")
    return not failures


def compare_with_previous(current: dict, cfg_name: str):
    """'Melhorei uma pergunta e piorei outras 10 sem perceber' -> aqui você percebe."""
    previous_files = sorted(p for p in RESULTS_DIR.glob("*.json"))
    if not previous_files:
        return
    previous = json.loads(previous_files[-1].read_text(encoding="utf-8"))
    print(f"\n[bold]Comparando com a rodada anterior:[/bold] {previous['config']}  ->  {cfg_name}")

    for metric in THRESHOLDS:
        old, new = previous["summary"].get(metric), current["summary"].get(metric)
        if old is None or new is None:
            continue
        delta = new - old
        color = "green" if delta > 0.01 else "red" if delta < -0.01 else "dim"
        print(f"  {metric:<18} {old:.2f} -> {new:.2f}  [{color}]{delta:+.2f}[/{color}]")

    # Por pergunta: a média pode subir escondendo perguntas que pioraram.
    old_rows = {r["id"]: r for r in previous["rows"]}
    for r in current["rows"]:
        o = old_rows.get(r["id"])
        if not o:
            continue
        for key, label in [("judge_score", "juiz"), ("code_pass_rate", "código")]:
            old, new = o.get(key), r.get(key)
            if old is None or new is None or old == new:
                continue
            tag = "[green]melhorou[/green]" if new > old else "[red]REGRESSÃO[/red]"
            print(f"  {tag} {r['id']} ({r['user_input'][:50]}): {label} {old:.2f} -> {new:.2f}")


def handle_calibration(rows: list[dict]):
    judge_scores = {r["id"]: r["judge_score"] for r in rows if r.get("judge_score")}
    if not judge_scores:
        return
    human = load_human_labels(HUMAN_LABELS_PATH)
    if not human:
        template = HUMAN_LABELS_PATH.with_name("human_labels_template.jsonl")
        template.write_text("\n".join(json.dumps({
            "id": r["id"], "pergunta": r["user_input"], "resposta": r["response"],
            "nota_juiz": r.get("judge_score"), "nota_humana": None,
        }, ensure_ascii=False) for r in rows), encoding="utf-8")
        print(f"\n[yellow]Juiz ainda não calibrado.[/yellow] Preencha 'nota_humana' em {template.name} "
              f"e salve como {HUMAN_LABELS_PATH.name} (sem olhar a nota do juiz primeiro!).")
        return
    report = calibrate(judge_scores, human)
    if report:
        status = "[green]calibrado[/green]" if report["calibrado"] else "[red]NÃO calibrado: ajuste a rubrica[/red]"
        print(f"\nCalibração juiz x humano (n={report['n']}): exata {report['concordancia_exata']:.0%}, "
              f"±1 {report['concordancia_mais_menos_1']:.0%} -> {status}")
        for d in report["maiores_divergencias"]:
            print(f"  divergência {d['id']}: juiz {d['juiz']} x humano {d['humano']}")


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--k", type=int, default=3, help="n_results do retrieval")
    parser.add_argument("--prompt", choices=["strict", "loose"], default="strict")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--category")
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--skip-ragas", action="store_true")
    args = parser.parse_args()

    cfg = RAGConfig(chunk_size=args.chunk_size, n_results=args.k, prompt=args.prompt)
    dataset = load_dataset(args.limit, args.category)
    print(f"[bold]Config:[/bold] {cfg.name}  |  [bold]Perguntas:[/bold] {len(dataset)}")

    rows = generate_answers(RAGSystem(cfg), dataset)
    judge_name = evaluate_rows(rows, args.skip_judge, args.skip_ragas)

    print_per_question(rows)
    print_by_category(rows)
    summary = summarize(rows)
    passed = quality_gate(summary)

    result = {"config": cfg.name, "judge": judge_name, "timestamp": datetime.now().isoformat(),
              "summary": summary, "rows": rows}
    compare_with_previous(result, cfg.name)
    handle_calibration(rows)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{cfg.name}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResultados salvos em {out.relative_to(RESULTS_DIR.parent.parent)}")

    sys.exit(0 if passed else 1)  # exit code != 0 -> quebra o CI, igual a um teste falhando


if __name__ == "__main__":
    main()
