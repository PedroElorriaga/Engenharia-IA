from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from rich import print

load_dotenv()

model = ChatOllama(
    model="llama3.1",
    temperature=0.5,
)

prompt = ChatPromptTemplate.from_template(
    "Você é um criador de poemas. Crie um poema sobre {tema}.")
chain = prompt | model

response = chain.invoke({"tema": "a beleza da natureza"})
print(response.content)
