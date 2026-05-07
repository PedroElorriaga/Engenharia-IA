from pydantic import BaseModel
from typing import Literal, TypedDict, Annotated, Sequence
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, add_messages
from rich import print
from rich.markdown import Markdown
import os

load_dotenv()


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class ExtratorSchema(BaseModel):
    titulo: str
    sentimento: Literal["positivo", "negativo", "neutro"]
    palavras_chave: list[str]



llm_extrator = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)

llm_redator = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.6
)

extractor_prompt = ChatPromptTemplate.from_template("""
Você é um extrator de informações. 
Dada a notícia abaixo, extraia título, sentimento e palavras-chave:

{noticia}
""")

redator_prompt = ChatPromptTemplate.from_template("""
Você é um redator jornalístico. Com base nas informações extraídas abaixo,
escreva um resumo em português com exatamente 2 frases:

{extracted_info}
""")

def information_extractor(state: State) -> State:
    chain = extractor_prompt | llm_extrator.with_structured_output(ExtratorSchema)
    result = chain.with_retry(
        stop_after_attempt=3,
        wait_exponential_jitter=True
    ).invoke({"noticia": state["messages"]})

    extracted_text = (
        f"Título: {result.titulo}\n"
        f"Sentimento: {result.sentimento}\n"
        f"Palavras-chave: {', '.join(result.palavras_chave)}"
    )
    return {"messages": [HumanMessage(content=extracted_text)]}

def redator(state: State) -> State:
    chain = redator_prompt | llm_redator.with_retry(
        stop_after_attempt=3,
        wait_exponential_jitter=True
    )
    llm_result = chain.invoke({"extracted_info": state["messages"][-1].content})

    return {"messages": [llm_result]}

builder = StateGraph(State)

builder.add_node("information_extractor", information_extractor)
builder.add_node("redator", redator)

builder.add_edge("__start__", "information_extractor")
builder.add_edge("information_extractor", "redator")    
builder.add_edge("redator", "__end__")

graph = builder.compile()

if __name__ == "__main__":
    noticia = "Corinthians secured a stunning 3-0 victory against Palmeiras in the Paulista derby last Sunday. Goals from Yuri Alberto (2) and Memphis Depay sealed the win in front of 47,000 fans at Neo Química Arena. The result puts Corinthians 5 points clear at the top of the table."

    result = graph.invoke({"messages": noticia})
    print("Resultado: ",Markdown(str(result["messages"][-1].content)))