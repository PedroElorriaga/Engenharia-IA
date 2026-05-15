import os
from langgraph.graph import StateGraph, add_messages
from langchain_google_genai import GoogleGenerativeAI
from rich import print
from rich.markdown import Markdown
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

load_dotenv()

llm = GoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview", 
        temperature=0.3,
        api_key=os.getenv("GEMINI_API_KEY")
    )

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def call_llm(state: State) -> State:
    llm_result = llm.invoke(state["messages"])
    return {"messages": [llm_result]}


# Creating the graph builder
builder = StateGraph(State)

# Adding Nodes
builder.add_node("call_llm", call_llm)

# Adding Edges
builder.add_edge("__start__", "call_llm")
builder.add_edge("call_llm", "__end__")

graph = builder.compile()

if __name__ == "__main__":
    new_messages: Sequence[BaseMessage] = []

    while True:
        user_input = input("User: ")
        print(Markdown("---"))

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        
        new_messages = [*new_messages, HumanMessage(user_input)]
        result = graph.invoke({"messages": new_messages})
        new_messages = result["messages"]

        print(Markdown(str(result["messages"][-1].content)))
        print(Markdown("---"))