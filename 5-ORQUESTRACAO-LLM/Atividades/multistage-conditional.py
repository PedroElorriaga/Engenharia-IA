import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableParallel, RunnableLambda
from rich import print

load_dotenv()

llm = GoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0.3,
    api_key=os.getenv("GEMINI_API_KEY"))

classificador_prompt = ChatPromptTemplate.from_template("""
Classifique a notícia abaixo em uma palavra: economia, politica ou esporte.
Retorne APENAS a categoria, sem mais nada.

Notícia: {noticia}
""")

classificar_chain = classificador_prompt | llm


chain_sobre_economia = ChatPromptTemplate.from_template(
    "A notícia '{noticia}' é sobre economia. Resuma os principais pontos relacionados à economia.") | llm

chain_sobre_politica = ChatPromptTemplate.from_template(
    "A notícia '{noticia}' é sobre política. Resuma os principais pontos relacionados à política.") | llm

chain_sobre_esporte = ChatPromptTemplate.from_template(
    "A notícia '{noticia}' é sobre esporte. Resuma os principais pontos relacionados ao esporte.") | llm

chain_padrao = ChatPromptTemplate.from_template(
    "Faça um resumo geral da notícia: {noticia}") | llm


branch = RunnableBranch(
    (lambda x: "economia" in x.get("categoria").lower(), chain_sobre_economia),
    (lambda x: "politica" in x.get("categoria").lower(), chain_sobre_politica),
    (lambda x: "esporte" in x.get("categoria").lower(), chain_sobre_esporte),
    chain_padrao
)

pipeline = (RunnableParallel({
    # Para garantir que a notícia seja passada para o classificador
    "noticia": RunnableLambda(lambda x: x["noticia"]),
    # Classificamos a notícia para obter a categoria
    "categoria": RunnableLambda(lambda x: x["noticia"]) | classificar_chain
}) | branch
)

resultado = pipeline.invoke(
    {"noticia": "O Brasil venceu uma copa em meio a uma crise econômica e política, trazendo esperança para o país."})
print(resultado)
