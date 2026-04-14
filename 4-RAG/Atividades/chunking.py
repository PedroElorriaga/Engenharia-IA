from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich import print
import os

with open(os.path.join(os.path.dirname(__file__), "texto.txt"), "r") as f:
    texto = f.read()

# overlap é a quantidade de caracteres que vão se repetir entre um chunk e outro, para manter o contexto
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, chunk_overlap=20)
chunks = text_splitter.create_documents([texto])
print(chunks)
