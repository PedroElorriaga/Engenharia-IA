from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


@tool(description="Save conversation logs")
def save_logs(logs: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("conversation_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {logs}\n" + "-" * 50 + "\n")


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY")
).bind_tools([save_logs])

prompt = PromptTemplate.from_template(
    """You are a helpful assistant that answers questions about the GTA V. 
    you can answer about map, characters, missions, easter eggs, and curiosities.
    if the question is not related to GTA V, say 'Sorry, I can only provide information about GTA V.'
    and provide the answer following this format: topico, respostas, fontes.

    Conversation history:
    {history}

    User question:
    {question}

    """
)

chain = prompt | llm

history = ""

print("Hi im Pedrinho IA, How can I help you? (type 'exit' to quit)\n")

while True:
    question = input("You: ")
    if question.lower() in ("exit", "quit", "sair"):
        break

    response = chain.invoke({
        "history": history,
        "question": question})
    answer = response.content[0]["text"]

    print("-" * 50)
    print(f"Pedrinho IA:\n{answer}\n")
    print("-" * 50)

    history += f"User: {question}\nAssistant: {answer}\n"
    save_logs.invoke({"logs": f"User: {question}\nAssistant: {answer}\n"})
