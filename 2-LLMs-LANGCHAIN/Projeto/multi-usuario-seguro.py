from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]


users = [
    {"usuario_id": 1,
     "historicos": {
         1: [
             HumanMessage(
                 content="Who is the best player in Corinthians history?"),
             AIMessage(
                 content="Cassio was the best player in Corinthians history.")
         ]
     }},
    {"usuario_id": 2,
     "historicos": {
         1: [
             HumanMessage(
                 content="When Corinthians won the last Mundial?"),
             AIMessage(
                 content="Corinthians won the last Mundial in 2012.")
         ]
     }},
]

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.4,
    api_key=os.getenv("GENAI_API_KEY")
)
parser = PydanticOutputParser(pydantic_object=ResearchResponse)
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are a Corinthians specialist.
        You know everything about Corinthians history, players, titles, and curiosities.
        Reply briefly and in a humble way.
        If the question is not related to Corinthians, reply: 'Sorry, I can only provide information about Corinthians.'
        Your response must be in English.
        Wrap the output in this format and provide no other text\n{format_instructions}
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
]).partial(format_instructions=parser.get_format_instructions())

# LCEL - prompt + llm + parser
chain = prompt | llm | parser


def chat_service(usuario_id: int, query: str):
    # PEGA O HISTÓRICO DO USUÁRIO, PEGANDO O ÚLTIMO HISTÓRICO DE CADA USUÁRIO
    user_history = next(user["historicos"][max(user["historicos"].keys())]
                        for user in users if user["usuario_id"] == usuario_id)

    try:
        response = chain.invoke({
            "query": query,
            "chat_history": user_history
        })

        next(user["historicos"].update({max(user["historicos"].keys()) + 1: user_history + [HumanMessage(content=query), AIMessage(content=response.summary)]})
             for user in users if user["usuario_id"] == usuario_id)

        return response
    except Exception as e:
        print("Failed to parse response:", e)


user_1 = chat_service(1, "Tell me where he team he is now?")
user_2 = chat_service(2, "and when was the first ?")

print("User 1 response:", user_1)
print("User 2 response:", user_2)
print("Updated users data:", users)
