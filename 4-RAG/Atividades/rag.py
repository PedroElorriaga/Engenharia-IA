from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from rich import print
import os


load_dotenv()

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


documents = [
    {"id": 1, "content": "Corinthians is one of the most traditional football clubs in Brazil."},
    {"id": 2, "content": "Founded in 1910, Corinthians has won numerous titles including three FIFA Club World Cups."},
    {"id": 3, "content": "The club plays at Neo Química Arena, located in São Paulo."},
    {"id": 4,
        "content": "Corinthians has a passionate fanbase known as 'Fiel' (Faithful)."}
]

messages = []
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.4
)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Aqui faço o embedding desses documentos
doc_embeddings = {doc["id"]: model.encode(
    doc["content"], convert_to_tensor=True) for doc in documents}


@app.post("/query")
def query_rag(request: QueryRequest):
    # Aqui faço o embedding da query
    query_embedding = model.encode(request.query, convert_to_tensor=True)
    best_doc = {}
    best_score = float("-inf")

    # Aqui calculo a similaridade entre a query e cada documento, retornando o mais relevante
    for doc in documents:
        score = util.cos_sim(query_embedding, doc_embeddings[doc["id"]])
        if score > best_score:
            best_score = score
            best_doc = doc

    # Aqui adiciono o conteúdo do documento mais relevante como contexto para o LLM, junto com a instrução de que ele só deve responder sobre esse documento
    messages.append(SystemMessage(
        content=f"""
        You are a helpful assistant that provides information about the Corinthians football club based on this document:
        {best_doc["content"]}

        If the user asks something that is not related to these documents, respond with 'Sorry, I can't help with that.'
        """
    ))

    messages.append(HumanMessage(content=request.query))
    llm_response = llm.invoke(messages)

    messages.append(llm_response)

    print(messages)

    return {"best_document": best_doc, "response": llm_response.content[0].get("text")}


'''
    O fluxo é o seguinte:
    
    1. O usuário faz uma pergunta via endpoint /query
    2. O sistema calcula o embedding da pergunta e compara com os embeddings dos documentos para encontrar o mais relevante
    3. O conteúdo do documento mais relevante é adicionado como contexto para o LLM
    4. O LLM é instruído a responder apenas com base nesse documento, e a resposta é retornada para o usuário

'''
