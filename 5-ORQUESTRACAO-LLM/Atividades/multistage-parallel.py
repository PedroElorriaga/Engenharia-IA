import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = GoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0.3,
    api_key=os.getenv("GEMINI_API_KEY"))

noticia = "O Brasil venceu a Argentina por 2 a 0 na final da Copa América de 2021, conquistando o título pela nona vez na história do torneio."

# Rodamos os três processos em paralelo para obter o resumo, sentimento e entidades da notícia ao mesmo tempo.
pipeline_paralelo = RunnableParallel({
    "resumo": ChatPromptTemplate.from_template("Resuma a seguinte notícia: {noticia}") | llm | StrOutputParser(),
    "sentimento": ChatPromptTemplate.from_template("Qual é o sentimento predominante na seguinte notícia: {noticia}?") | llm | StrOutputParser(),
    "entidades": ChatPromptTemplate.from_template("Quais são as entidades mencionadas na seguinte notícia: {noticia}?") | llm | StrOutputParser()
})

resposta = pipeline_paralelo.invoke({"noticia": noticia})
print("resumo:", resposta["resumo"], "\n")
print("sentimento:", resposta["sentimento"], "\n")
print("entidades:", resposta["entidades"], "\n")
