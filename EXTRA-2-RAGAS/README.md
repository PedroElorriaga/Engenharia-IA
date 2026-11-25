# EXTRA 2 — Evals de RAG com RAGAS

Código que implementa o que está em [EvalsRAGAS.md](EvalsRAGAS.md), testando o RAG do módulo 4
sobre o documento `6-LLMOps-DEPLOYMENT/Projeto/regras-empresa-pedrinho.md`.

```
golden_dataset.jsonl ──> RAG (Chroma + Gemma) ──> resposta + chunks recuperados
                                                        │
                    ┌───────────────────────────────────┼──────────────────────────────┐
                    ▼                                   ▼                              ▼
            código (grátis)              LLM-as-judge com rubrica (Llama)      RAGAS: 4 métricas
                    └───────────────────────────────────┼──────────────────────────────┘
                                                        ▼
                         quality gate (média >= limite) ──> ação sugerida ──> comparação com a rodada anterior
```

## Onde está cada conceito

| Conceito do EvalsRAGAS.md | Arquivo |
| :--- | :--- |
| Eval = teste com **nota**, passa se a **média** passar do limite | `config.py` (`THRESHOLDS`) e `run_evals.py` (`quality_gate`, `sys.exit(1)` quebra o CI) |
| Avaliador **baseado em código** | `evaluators/code_evals.py`: fatos esperados, recusa correta, texto proibido, tamanho |
| Avaliador **LLM-as-judge** com rubrica | `evaluators/llm_judge.py`: a rubrica do .md, um `[ARMADILHA]` por cuidado |
| Avaliador **humano** / calibração | `llm_judge.calibrate()`: você preenche `evals/human_labels.jsonl` e mede a concordância (>= 80%) |
| As **4 métricas** do RAGAS | `evaluators/ragas_metrics.py` (API nova `ragas.metrics.collections`, v0.4) |
| **Nota baixa -> ação** | `config.ACTIONS`, impresso pelo `quality_gate` |
| **Golden dataset** com mistura de categorias | `evals/golden_dataset.jsonl`: 8 simples, 4 multi-chunk, 3 sem resposta, 3 com erro de digitação, 2 adversariais |
| Gerar o resto com **TestsetGenerator** | `generate_testset.py` -> `synthetic_candidates.jsonl` com `"revisado": false` |
| **Auto-preferência**: julgar com outra família | `config.resolve_judge()`: gera com Google (Gemma), julga com Meta (Llama 3.1 no Ollama) |
| Temperatura 0 / raciocínio antes da nota | `Judge.as_langchain()` / ordem dos campos em `JudgeVerdict` |
| "Melhorei uma e piorei 10 sem perceber" | `run_evals.compare_with_previous()`: deltas por métrica **e por pergunta** |

## Resultados reais (23/11/2026)

**Rodada 1: config do módulo 4** (`chunk_size=100`, `n_results=3`), só os checks de código:

| categoria | código |
| :--- | :--- |
| simples | 0.92 |
| **multi_chunk** | **0.42** |
| sem_resposta | 1.00 |
| reformulada | 0.89 |
| adversarial | 1.00 |
| **total** | **0.82: FALHOU** (limite 0.90) |

Chunks de 100 caracteres cortam as regras no meio. O modelo recebe pedaços soltos e responde
*"Não encontrei essa informação"* para perguntas que **têm** resposta (s06, m02, m03, m04).
A tabela de ações aponta: *melhorar o chunking / aumentar n_results*.

**Rodada 2: mudando só isso** (`--chunk-size 500 --k 5`):

```
code_checks        0.82 -> 1.00  +0.18
melhorou s06 (Em que dia o salário é pago?): código 0.33 -> 1.00
melhorou m02 (Quem trabalha remoto recebe qual auxílio...): código 0.33 -> 1.00
melhorou m03, m04, m01, r01 ...
```

**Amostra com juiz + RAGAS** (3 perguntas, juiz Llama 3.1): faithfulness 1.00, answer relevancy 0.85,
context precision 0.83, **context recall 0.67 (FALHOU)**. Detalhe que vale para entrevista: no `s02` o
Context Recall deu **1.00 com o Gemini como juiz e 0.50 com o Llama**. O mesmo dado com juízes
diferentes dá notas diferentes, e é por isso que a calibração com humano existe.

## Como rodar

```bash
cd EXTRA-2-RAGAS
python -m venv .venv && .venv\Scripts\activate    # venv separado: o ragas atualizaria
pip install -r requirements.txt                   # huggingface_hub/langchain do venv principal
ollama serve                                      # juiz local (ollama pull llama3.1)

python run_evals.py --skip-judge --skip-ragas            # só código: ~5 min, 20 chamadas
python run_evals.py --chunk-size 500 --k 5 --skip-judge --skip-ragas
python run_evals.py --limit 5                            # tudo, em amostra
python run_evals.py                                      # completo: ~70 min com o juiz local
python run_evals.py --prompt loose                       # prompt solto: veja faithfulness/adversarial
python generate_testset.py --size 10                     # candidatas sintéticas (revisar!)
```

Custos e limites: o free tier do `gemini-2.5-flash` dá só **20 requisições/dia**, e um eval completo
faz ~250 (juiz + 4 métricas x 20 perguntas). Por isso o gerador padrão é o `gemma-4-31b-it` e o juiz
roda local. Variáveis: `GENERATOR_MODEL`, `JUDGE_PROVIDER=auto|ollama|gemini`, `JUDGE_OLLAMA_MODEL`.
