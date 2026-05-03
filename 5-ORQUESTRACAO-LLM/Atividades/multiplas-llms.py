from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
import os
from dotenv import load_dotenv
from rich import print

load_dotenv()


def tap(label):
    def _tap(x):
        print(f"[bold green]{label}:[/bold green] {x}")
        return x

    return RunnableLambda(_tap)


parser = StrOutputParser()

extrator_prompt = ChatPromptTemplate.from_template("""
Voce é um extrator de noticias.
Extraia os fatos da noticias abaixo
                                                   
Notícia: {Notícia}
                                                   
e retorne os fatos em formato de lista, sem incluir nada além dos fatos.
""")


analisador_prompt = ChatPromptTemplate.from_template("""
Voce é um analista de noticias.
Analise cada fato na lista abaixo e verifique se há algo tendencioso, falso ou enganoso.
                                                     
Fatos: {Fatos}

e retorne uma lista dos fatos tendenciosos, falsos ou enganosos, sem incluir nada além dessa lista.                      
""")

resumidor_prompt = ChatPromptTemplate.from_template("""
Voce é um resumidor de noticias.
Analise os fatos que sao tendenciosos, falsos ou enganosos e resuma o impacto que eles podem ter na sociedade, que estao abaixo
                                                    
Fatos tendenciosos, falsos ou enganosos: {Fatos}
                                                    
e reescreva a noticia de forma neutra e objetiva
""")


llm_extracao = GoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.3, api_key=os.getenv("GEMINI_API_KEY"))

llm_analisador = GoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview", temperature=0.5, api_key=os.getenv("GEMINI_API_KEY"))

llm_resumidor = GoogleGenerativeAI(
    model="gemini-2.5-flash-lite", temperature=0.4, api_key=os.getenv("GEMINI_API_KEY"))

print("chamando a cadeia...")

chain = (
    extrator_prompt | llm_extracao | parser
    | tap("Fatos extraídos: ")
    | analisador_prompt | llm_analisador | parser
    | tap("Fatos tendenciosos, falsos ou enganosos: ")
    | resumidor_prompt | llm_resumidor | parser
)

resultado = chain.invoke({
    "Notícia": "O presidente do Brasil, Jair Bolsonaro, afirmou que a "
    "Terra é plana durante um discurso na Câmara dos Deputados. Especialistas "
    "em geografia e ciência refutaram imediatamente a declaração, destacando evidências "
    "científicas que comprovam a esfericidade da Terra. A comunidade científica expressou "
    "preocupação com a disseminação de informações falsas por parte de figuras públicas."
})

print(resultado)
