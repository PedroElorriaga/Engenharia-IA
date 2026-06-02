from rag.vector_store import get_chroma_client
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os


EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
chroma_client = get_chroma_client()


def ingest() -> chromadb.Collection:
    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL)

    with open(os.path.join(os.path.dirname(__file__), "../regras-empresa-pedrinho.md"), "r", encoding="utf-8") as f:
        document = f.read()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.create_documents([document])

    collection = chroma_client.create_collection(
        name="pedrinhos_collection",
        embedding_function=embedding_function
    )
    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=[chunk.page_content for chunk in chunks],
    )

    return collection
