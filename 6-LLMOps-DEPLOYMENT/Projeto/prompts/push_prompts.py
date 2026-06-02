from langsmith import Client
from dotenv import load_dotenv
from templates import prompt
from rich import print

load_dotenv()

client = Client()

print("Salvando o prompt no LangSmith...")
client.push_prompt(
    "pedrinhos_company_assistant",
    object=prompt
)
print("Prompt salvo com sucesso!")
