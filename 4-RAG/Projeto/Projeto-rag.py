import os
import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from rich import print

load_dotenv()


class RAGAgent:
    def __init__(self, document: str):
        self.llm = self.__llm_connection()
        self.messages = []
        self.chroma_client = chromadb.Client()
        self.collection = self.__ingest_document(document)

    def __llm_connection(self) -> ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.4
        )

        return llm

    def __save_message(self, message: HumanMessage | SystemMessage | AIMessage):
        self.messages.append(message)

    def __chunk_documents(self, document: str) -> list:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100, chunk_overlap=20)
        chunks = text_splitter.create_documents([document])

        return chunks

    def __ingest_document(self, document: str) -> chromadb.Collection:
        chunks = self.__chunk_documents(document)

        collection = self.chroma_client.create_collection(
            name="pedrinhos_collection"
        )
        collection.add(
            ids=[str(i) for i in range(len(chunks))],
            documents=[chunk.page_content for chunk in chunks],
        )

        return collection

    def query(self, query: str):
        collection_response = self.collection.query(
            query_texts=[query],
            n_results=3
        )

        self.__save_message(SystemMessage(
            content=f"You are a helpful Pedrinhos Company assistant that provides information based on this 3 documents chunk: {collection_response.get('documents')[0]}")
        )
        self.__save_message(HumanMessage(content=query))

        llm_response = self.llm.invoke(self.messages)
        self.__save_message(llm_response)

        print(self.messages[-1].content)


with open(os.path.join(os.path.dirname(__file__), "regras-empresa-pedrinho.txt"), "r", encoding="utf-8") as f:
    document = f.read()

agent = RAGAgent(document)
response = agent.query("Quando a empresa foi fundada?")
