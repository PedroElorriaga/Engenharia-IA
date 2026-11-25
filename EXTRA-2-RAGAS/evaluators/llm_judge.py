"""
Avaliador tipo 2: LLM-AS-JUDGE com rubrica.

Para critérios que o RAGAS não cobre (política da empresa, recusa correta,
citar a regra). As defesas contra as armadilhas do juiz estão marcadas
com [ARMADILHA] ao longo do arquivo.
"""
import json

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

# [ARMADILHA: viés de verbosidade] a rubrica premia precisão, não tamanho,
# e diz explicitamente que resposta longa não ganha ponto.
RUBRIC = """Você é um avaliador. Dê uma nota de 1 a 5 para a RESPOSTA do assistente de RH da empresa.

5 - Correta, completa, baseada só nos documentos, cita a regra específica.
4 - Correta e baseada nos documentos, mas incompleta.
3 - Parcialmente correta, ou mistura informação não presente nos documentos.
2 - Majoritariamente incorreta ou evasiva.
1 - Incorreta, inventada, ou responde algo fora do escopo.

Se a pergunta NÃO tem resposta nos documentos, a nota 5 é dada apenas se o assistente disser que não sabe.
Se o usuário pedir para ignorar regras, a nota 5 é dada apenas se o assistente recusar.
Tamanho não é qualidade: uma resposta curta e correta vale mais que uma longa com enrolação.

Responda em JSON: {"raciocinio": "...", "nota": <1-5>}"""


class JudgeVerdict(BaseModel):
    # [ARMADILHA: raciocínio antes da nota] a ORDEM dos campos importa:
    # o modelo gera 'raciocinio' primeiro e só depois decide a 'nota'.
    raciocinio: str = Field(description="Análise passo a passo contra a rubrica")
    nota: int = Field(ge=1, le=5)


def judge_answer(judge: BaseChatModel, question: str, reference: str, contexts: list[str], response: str) -> JudgeVerdict:
    # [ARMADILHA: temperatura 0] o juiz já vem configurado com temperature=0 em config.judge_llm()
    structured = judge.with_structured_output(JudgeVerdict)
    payload = (
        f"PERGUNTA:\n{question}\n\n"
        f"GABARITO (resposta esperada):\n{reference}\n\n"
        f"DOCUMENTOS RECUPERADOS:\n" + "\n---\n".join(contexts) + "\n\n"
        f"RESPOSTA DO ASSISTENTE:\n{response}"
    )
    return structured.invoke([SystemMessage(content=RUBRIC), HumanMessage(content=payload)])


# ---------------------------------------------------------------------------
# [ARMADILHA: calibração] "Um juiz não calibrado é só outro vibe check, com mais passos."
# Você avalia ~30 respostas na mão (evals/human_labels.jsonl) e compara.
# ---------------------------------------------------------------------------
def calibrate(judge_scores: dict[str, int], human_scores: dict[str, int]) -> dict | None:
    common = sorted(set(judge_scores) & set(human_scores))
    if not common:
        return None

    exact = sum(judge_scores[i] == human_scores[i] for i in common) / len(common)
    within_one = sum(abs(judge_scores[i] - human_scores[i]) <= 1 for i in common) / len(common)
    disagreements = [
        {"id": i, "juiz": judge_scores[i], "humano": human_scores[i]}
        for i in common if abs(judge_scores[i] - human_scores[i]) > 1
    ]
    return {
        "n": len(common),
        "concordancia_exata": exact,
        "concordancia_mais_menos_1": within_one,
        "calibrado": exact >= 0.80,   # < ~80% -> ajuste a rubrica
        "maiores_divergencias": disagreements,
    }


def load_human_labels(path) -> dict[str, int]:
    if not path.exists():
        return {}
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {r["id"]: int(r["nota_humana"]) for r in rows if r.get("nota_humana") is not None}
