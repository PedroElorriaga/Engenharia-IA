import os
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("OLLAMA_RETRIES", "2"))

SYSTEM_PROMPT = (
    "You are an expert software engineer and code reviewer. "
    "Answer programming questions clearly and concisely. "
    "When reviewing code, point out bugs, suggest improvements, and explain your reasoning. "
    "When writing code, follow best practices and add brief inline comments where helpful."
)

app = FastAPI(title="Programming Assistant API")


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class AskResponse(BaseModel):
    answer: str
    latency_ms: int
    model: str


def _build_messages(question: str, history: list[ChatMessage]) -> list:
    messages: list = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    messages.append(HumanMessage(content=question))
    return messages


def _call_model_with_retry(
    question: str,
    history: list[ChatMessage],
    timeout_seconds: float = TIMEOUT_SECONDS,
    retries: int = MAX_RETRIES,
) -> tuple[str, str]:
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
        timeout=int(timeout_seconds),
    )
    messages = _build_messages(question, history)
    last_error: Optional[Exception] = None

    for attempt in range(retries + 1):
        start = time.perf_counter()
        try:
            response = llm.invoke(messages)
            elapsed = time.perf_counter() - start
            if elapsed > timeout_seconds:
                raise TimeoutError(
                    f"Model took {elapsed:.1f}s, limit is {timeout_seconds}s")
            return str(response.content), OLLAMA_MODEL
        except TimeoutError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise

    if last_error is not None:
        raise last_error
    raise RuntimeError("Unexpected failure after retries")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    started = time.perf_counter()
    try:
        answer, model_name = _call_model_with_retry(
            payload.question, payload.history)
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    latency_ms = int((time.perf_counter() - started) * 1000)
    return AskResponse(answer=answer, latency_ms=latency_ms, model=model_name)
