"""
Golden dataset, passo 2: gerar perguntas SINTÉTICAS a partir do documento.

    python generate_testset.py --size 10

Elas NÃO vão direto para o golden_dataset.jsonl. Vão para
evals/synthetic_candidates.jsonl com "revisado": false, porque
"pergunta sintética sem revisão vira gabarito errado" (passo 3).
Depois de revisar, copie as boas para o golden dataset e faça commit (passo 4).
"""
import argparse
import json

from langchain_core.documents import Document
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.testset import TestsetGenerator
from rich import print

from config import DOCUMENT_PATH, ROOT, embeddings, generator_llm


def load_sections() -> list[Document]:
    """Uma Document por seção '## ' do markdown: o gerador cria perguntas
    simples (1 seção) e multi-hop (cruzando seções)."""
    text = DOCUMENT_PATH.read_text(encoding="utf-8")
    sections = [s.strip() for s in text.split("\n## ") if s.strip()]
    return [Document(page_content=s, metadata={"source": DOCUMENT_PATH.name}) for s in sections]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=10)
    args = parser.parse_args()

    generator = TestsetGenerator(
        llm=LangchainLLMWrapper(generator_llm(temperature=0.7)),
        embedding_model=LangchainEmbeddingsWrapper(embeddings()),
    )
    testset = generator.generate_with_langchain_docs(load_sections(), testset_size=args.size)

    out = ROOT / "evals" / "synthetic_candidates.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(testset.to_pandas().to_dict("records"), 1):
            f.write(json.dumps({
                "id": f"syn{i:02d}",
                "category": "sintetica",
                "user_input": row["user_input"],
                "reference": row["reference"],
                "synthesizer": row.get("synthesizer_name"),
                "must_contain": [],
                "must_not_contain": [],
                "expect_refusal": False,
                "revisado": False,   # <- você muda para true depois de ler
            }, ensure_ascii=False) + "\n")
    print(f"{args.size} candidatas em {out.name}. Revise antes de usar!")


if __name__ == "__main__":
    main()
