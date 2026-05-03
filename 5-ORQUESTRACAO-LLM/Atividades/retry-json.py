import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from rich import print

load_dotenv()

llm_principal = GoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.3, api_key=os.getenv("GEMINI_API_KEY"))


messages = [
    {"role": "system", "content": "Responda a pergunta do usuario e retorne a reposta em formato de texto simples."},
    {"role": "user", "content": "Quem é o jogador de futebol mais famoso do mundo?"}
]

parser_json = JsonOutputParser()

prompt = ChatPromptTemplate.from_template("""
Responda a pergunta do usuario e retorne a reposta em formato de texto simples.
Pergunta: {Pergunta}
                                          
retorne apenas um JSON valido com esse formato:
{{"resposta": "a resposta do LLM aqui"}}
""")

chain = (prompt
         | llm_principal.with_retry(
             retry_if_exception_type=(ValueError,),
             stop_after_attempt=3
         )
         | parser_json
         )


try:
    resultado = chain.invoke(
        {"Pergunta": "Quem é o jogador de futebol mais famoso do mundo?"})
    print(resultado)
except Exception as e:
    print(f"Erro ao chamar o LLM: {e}")
