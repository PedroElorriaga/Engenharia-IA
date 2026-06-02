from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from rich import print

load_dotenv()

client = Client()

model = ChatOllama(
    model="llama3.1",
    temperature=0.5,
)

prompt = ChatPromptTemplate.from_template(
    "Você é um criador de poemas. Crie um poema sobre {tema}.")

prompt_v2 = ChatPromptTemplate.from_template(
    "Você é um criador de poemas de superação. Crie um poema sobre o {tema} e inspire os leitores a nunca desistirem. "
    "Use uma linguagem motivadora e encorajadora, destacando a importância da resiliência e da perseverança diante dos desafios. "
    "Seja criativo e envolvente, transmitindo uma mensagem de esperança e força interior.")

# Salvar o prompt no LangSmith
client.push_prompt(
    "prompt_poema",
    object=prompt_v2
)

prompt_recente = client.pull_prompt("prompt_poema")
print(prompt_recente)
print("-" * 10)

prompt_v1 = client.pull_prompt("prompt_poema:513f5a07")
print(prompt_v1)


# chain = prompt_recente | model

# response = chain.invoke({"tema": "a beleza da natureza"})
# print(response.content)
