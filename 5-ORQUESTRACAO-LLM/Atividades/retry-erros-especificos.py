import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage
from google.genai.errors import ServerError
from rich import print

load_dotenv()

llm = GoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.3, api_key=os.getenv("GEMINI_API_KEY"))

messages = [SystemMessage(
    content="Responda a pergunta do usuario"),
    HumanMessage(content="Qual é a capital da França?")
]

# Vamos criar uma versão do LLM com retry para lidar com possíveis falhas na chamada à API, mas agora vamos configurar para que ele só tente novamente em casos de erros específicos, como erros de servidor ou timeout.
llm_with_retry = llm.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
    retry_if_exception_type=(
        ServerError,  # Erro de servidor
        TimeoutError  # Erro de timeout
    )
)

try:
    resposta = llm_with_retry.invoke(messages)
    print(resposta)
except Exception as e:
    print(f"Erro ao chamar o LLM: {e}")
