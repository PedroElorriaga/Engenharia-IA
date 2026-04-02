from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

history = [
    types.Content(
        role="model",
        parts=[types.Part(
            text="To connect to Wi-Fi: open settings, select Wi-Fi, choose network, enter password.")]
    )
]


def make_request(question: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history + [
            types.Content(role="user", parts=[types.Part(text=question)])
        ],
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a network specialist. Reply briefly. "
                "you need to be humble and educated. "
                "If not networking-related, reply: "
                "'Sorry, I can only provide information about networking.'"
            ),
            temperature=0.4,  # NAO MUITO BRISADO, PARA EVITAR RESPOSTAS MUITO CRIATIVAS E LONGAS
        )
    )
    return response.text or ""


print("Req 1: " + make_request("I need to connect to a wifi network, how can I do that?"))

print("Req 2: " + make_request("Thank you! Which is the best pizza flavor?"))


# DOCUMENTACAO DE TEXT-GENERATION: https://ai.google.dev/gemini-api/docs/text-generation
