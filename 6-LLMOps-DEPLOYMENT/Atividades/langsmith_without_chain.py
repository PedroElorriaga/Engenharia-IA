from google import genai
from dotenv import load_dotenv
from rich import print
from langsmith import wrappers
import os

load_dotenv()

client = wrappers.wrap_gemini(genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")))

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Escreva um poema sobre a beleza da natureza.",
    config={"temperature": 0.7}
)

print(response.text)
