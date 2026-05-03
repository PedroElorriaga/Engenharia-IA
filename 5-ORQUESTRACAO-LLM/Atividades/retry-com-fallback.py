import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI

load_dotenv()

llm_principal = GoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.3, api_key=os.getenv("GEMINI_API_KEY"))

llm_fallback = GoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview", temperature=0.5, api_key=os.getenv("GEMINI_API_KEY"))

# Criamos um LLM com retry e fallback para garantir que, mesmo que o modelo principal falhe, teremos uma resposta do modelo de fallback.
llm_with_fallback = llm_principal.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
).with_fallbacks([llm_fallback])

messages = [
    {"role": "system", "content": "Responda a pergunta do usuario e retorne a reposta em formato de texto simples."},
    {"role": "user", "content": "Quem é o jogador de futebol mais famoso do mundo?"}
]

try:
    resposta = llm_with_fallback.invoke(messages)
    print(resposta)
except Exception as e:
    print(f"Erro ao chamar o LLM: {e}")
