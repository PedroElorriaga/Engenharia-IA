import os
from dotenv import load_dotenv
import speech_recognition as sr
from rich import print
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

load_dotenv()


class ItemCompra(BaseModel):
    nome_produto: str
    quantidade: int
    categoria: str


class ListaCompras(BaseModel):
    itens: list[ItemCompra]


messages = []
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.5
)

messages.append(SystemMessage(
    content="""
    Você é um assistente que ajuda a criar uma lista de compras.
    Você ajustara a lista de compras com base no que o usuario disser
    Caso o usuario dizer algo fora do contexto de compras, como pedir uma receira, ou perguntar sobre o clima, você respondera 'Desculpe, não posso ajudar com isso.'

    -- few shot examples --
    Entrada: Eu preciso comprar pão e leite
    Saida: ItemCompra(nome_produto='pão', quantidade=1, categoria='alimentos')

    Entrada: Eu quero comprar 3 litros de leite
    Saida: ItemCompra(nome_produto='leite', quantidade=3, categoria='laticínios')

    Entrada: Me fale uma receita de bolo
    Saida: Desculpe, não posso ajudar com isso.
    """
))

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Diga algo:")
    audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='pt-BR')
        print("Você disse: " + text)
        messages.append(HumanMessage(content=text))
    except sr.UnknownValueError:
        print("Não entendi o que você disse.")
    except sr.RequestError as e:
        print(
            "Erro ao se conectar ao serviço de reconhecimento de fala; {0}".format(e))

structured_model = llm.with_structured_output(
    ListaCompras,
    method="json_schema"
)

result = structured_model.invoke(messages)

print(result)

if result is not None and len(result.itens) > 0:
    print(result.itens[0].nome_produto)

# PEDRINHO OLHAR DEPOIS
# while True:
#     with sr.Microphone() as source:
#         print("Diga algo:")
#         audio = r.listen(source)
#     try:
#         text = r.recognize_google(audio, language='pt-BR')

#         if text.lower() in ("sair do programa"):
#             print("Encerrando o programa.")
#             break

#         print("Você disse: " + text)
#     except sr.UnknownValueError:
#         print("Não entendi o que você disse.")
#     except sr.RequestError as e:
#         print(
#             "Erro ao se conectar ao serviço de reconhecimento de fala; {0}".format(e))
