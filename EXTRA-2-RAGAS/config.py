"""
Configuração central dos evals.

Ponto-chave (armadilha de "auto-preferência"): o modelo que GERA a resposta
não deve ser o mesmo que JULGA. Aqui o RAG gera com Google (Gemma/Gemini) e
o juiz é, por padrão, um modelo de outra família (Llama 3.1 no Ollama).
Se o Ollama não estiver rodando, caímos para o Google e avisamos que o
resultado pode estar inflado.

Variáveis opcionais: GENERATOR_MODEL, JUDGE_PROVIDER (auto|ollama|gemini), JUDGE_OLLAMA_MODEL.
"""
import os
from dataclasses import dataclass
from pathlib import Path

import requests
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from rich import print

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / ".env")

DOCUMENT_PATH = ROOT.parent / "6-LLMOps-DEPLOYMENT" / "Projeto" / "regras-empresa-pedrinho.md"
GOLDEN_DATASET_PATH = ROOT / "evals" / "golden_dataset.jsonl"
HUMAN_LABELS_PATH = ROOT / "evals" / "human_labels.jsonl"
RESULTS_DIR = ROOT / "evals" / "results"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
JUDGE_OLLAMA_MODEL = os.getenv("JUDGE_OLLAMA_MODEL", "llama3.1")

# Um eval completo faz ~250 chamadas. O free tier do gemini-2.5-flash só dá 20/dia,
# então o gerador padrão é o Gemma (mesmo modelo do módulo 6, cota bem maior).
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "gemma-4-31b-it")

# ---------------------------------------------------------------------------
# Quality gate: o eval "passa" se a MÉDIA ficar acima do limite
# (diferente do pytest, onde cada assert é passa/falha exato).
# ---------------------------------------------------------------------------
THRESHOLDS = {
    "context_precision": 0.70,
    "context_recall": 0.70,
    "faithfulness": 0.80,
    "answer_relevancy": 0.70,
    "judge_score": 4.0,       # nota média do LLM-as-judge (escala 1-5)
    "code_checks": 0.90,      # % de checks determinísticos aprovados
}

# Tabela "nota baixa -> causa provável -> o que mexer" (do EvalsRAGAS.md)
ACTIONS = {
    "context_precision": ("Veio muito chunk irrelevante",
                          "Reranking, chunks mais focados, filtros de metadados"),
    "context_recall": ("A informação existe, mas não foi buscada",
                       "Aumentar n_results, melhorar chunking, trocar embedding, hybrid search"),
    "faithfulness": ("O LLM inventou além do contexto",
                     "Prompt mais restritivo, temperatura menor"),
    "answer_relevancy": ("A resposta foge do assunto",
                         "Ajustar o system prompt, pedir objetividade"),
    "judge_score": ("Resposta incompleta/inventada segundo a rubrica",
                    "Leia o 'raciocinio' do juiz nas piores notas"),
    "code_checks": ("Falhou em regra determinística (fato, recusa, segurança)",
                    "Veja quais checks falharam por categoria"),
}


def generator_llm(temperature: float = 0.4) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=GENERATOR_MODEL, api_key=GEMINI_API_KEY, temperature=temperature)


def _ollama_is_up() -> bool:
    try:
        return requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2).ok
    except requests.RequestException:
        return False


GEMINI_OPENAI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
EMBEDDING_MODEL = "gemini-embedding-001"


@dataclass(frozen=True)
class Judge:
    provider: str      # "ollama" | "gemini"
    model: str
    base_url: str      # endpoint compatível com OpenAI (o ragas 0.4 usa esse formato)
    api_key: str

    @property
    def name(self) -> str:
        return f"{self.provider}/{self.model}"

    def as_langchain(self) -> BaseChatModel:
        """Para o nosso LLM-as-judge com rubrica. Juiz SEMPRE com temperatura 0."""
        if self.provider == "ollama":
            from langchain_ollama import ChatOllama
            return ChatOllama(model=self.model, base_url=OLLAMA_BASE_URL, temperature=0)
        return ChatGoogleGenerativeAI(model=self.model, api_key=self.api_key, temperature=0)


def resolve_judge() -> Judge:
    provider = os.getenv("JUDGE_PROVIDER", "auto")

    if provider in ("auto", "ollama") and _ollama_is_up():
        return Judge("ollama", JUDGE_OLLAMA_MODEL, f"{OLLAMA_BASE_URL}/v1", "ollama")

    if provider == "ollama":
        raise RuntimeError(f"JUDGE_PROVIDER=ollama, mas o Ollama não respondeu em {OLLAMA_BASE_URL}")

    print("[yellow]AVISO: juiz = Gemini, mesma família do gerador -> risco de auto-preferência.[/yellow]")
    return Judge("gemini", GENERATOR_MODEL, GEMINI_OPENAI_URL, GEMINI_API_KEY)


def embeddings() -> GoogleGenerativeAIEmbeddings:
    """Embeddings LangChain (usado pelo TestsetGenerator)."""
    return GoogleGenerativeAIEmbeddings(model=f"models/{EMBEDDING_MODEL}", google_api_key=GEMINI_API_KEY)
