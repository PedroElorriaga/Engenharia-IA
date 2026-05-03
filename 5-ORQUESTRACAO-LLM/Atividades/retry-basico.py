import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage
from rich import print

load_dotenv()

llm = GoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.3, api_key=os.getenv("GEMINI_API_KEY"))

messages = [SystemMessage(
    content="Responda a pergunta do usuario"),
    HumanMessage(content="Qual é a capital da França?")
]

# Vamos criar uma versão do LLM com retry para lidar com possíveis falhas na chamada à API.
llm_with_retry = llm.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

try:
    resposta = llm_with_retry.invoke(messages)
    print(resposta)
except Exception as e:
    print(f"Erro ao chamar o LLM: {e}")

print("-" * 100)

# Agora vamos tentar com uma chave de API inválida para ver o mecanismo de retry em ação.
llm_errado = GoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.3, api_key="CHAVE INVALIDA").with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

try:
    resposta_errada = llm_errado.invoke(messages)
    print(resposta_errada)
except Exception as e:
    print(f"Erro ao chamar o LLM: {e}")
