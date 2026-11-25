"""
As 4 métricas principais do RAGAS (API nova: ragas.metrics.collections, v0.4+).

    Retrieval -> Context Precision : os chunks relevantes vieram no TOPO?          (usa gabarito)
              -> Context Recall    : veio TUDO que era necessário?                 (usa gabarito)
    Geração   -> Faithfulness      : tudo que a resposta afirma está nos chunks?   (sem gabarito)
              -> Answer Relevancy  : a resposta responde à pergunta, ou enrola?    (sem gabarito)

Todas são "LLM-as-judge por baixo dos panos": o RAGAS quebra a tarefa em
passos pequenos (extrair afirmações, verificar cada uma...) e calcula um
número de 0 a 1. Por isso usamos o mesmo juiz de outra família (config.resolve_judge).
"""
import asyncio

from openai import AsyncOpenAI
from ragas.embeddings import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    AnswerRelevancy,
    ContextPrecisionWithReference,
    ContextRecall,
    Faithfulness,
)

from config import EMBEDDING_MODEL, GEMINI_API_KEY, GEMINI_OPENAI_URL, Judge

MAX_CONCURRENCY = 3  # plano gratuito do Gemini tem limite de requisições por minuto


def build_metrics(judge: Judge) -> dict:
    # Gemini e Ollama expõem endpoints compatíveis com OpenAI: um único caminho para os dois.
    llm = llm_factory(judge.model, provider="openai",
                      client=AsyncOpenAI(base_url=judge.base_url, api_key=judge.api_key), temperature=0)
    emb = embedding_factory("openai", model=EMBEDDING_MODEL,
                            client=AsyncOpenAI(base_url=GEMINI_OPENAI_URL, api_key=GEMINI_API_KEY))
    return {
        "context_precision": ContextPrecisionWithReference(llm=llm),
        "context_recall": ContextRecall(llm=llm),
        "faithfulness": Faithfulness(llm=llm),
        # Gera N perguntas a partir da RESPOSTA e mede a similaridade com a pergunta original.
        # Resposta evasiva ("não sei") tende a receber nota baixa aqui -> por isso olhamos por categoria.
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=emb, strictness=3),
    }


async def _score_row(metrics: dict, row: dict, sem: asyncio.Semaphore) -> dict[str, float | None]:
    # Cada métrica recebe só os campos de que precisa:
    inputs = {
        "context_precision": dict(user_input=row["user_input"], reference=row["reference"],
                                  retrieved_contexts=row["retrieved_contexts"]),
        "context_recall": dict(user_input=row["user_input"], reference=row["reference"],
                               retrieved_contexts=row["retrieved_contexts"]),
        "faithfulness": dict(user_input=row["user_input"], response=row["response"],
                             retrieved_contexts=row["retrieved_contexts"]),
        "answer_relevancy": dict(user_input=row["user_input"], response=row["response"]),
    }
    scores = {}
    for name, metric in metrics.items():
        async with sem:
            try:
                scores[name] = float((await metric.ascore(**inputs[name])).value)
            except Exception as exc:  # uma métrica falhar não derruba o eval inteiro
                print(f"  [{row['id']}] {name} falhou: {type(exc).__name__}: {str(exc)[:120]}")
                scores[name] = None
    return scores


async def _run(rows: list[dict], judge: Judge) -> list[dict]:
    metrics = build_metrics(judge)
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    return await asyncio.gather(*(_score_row(metrics, r, sem) for r in rows))


def run_ragas(rows: list[dict], judge: Judge) -> list[dict[str, float | None]]:
    return asyncio.run(_run(rows, judge))
