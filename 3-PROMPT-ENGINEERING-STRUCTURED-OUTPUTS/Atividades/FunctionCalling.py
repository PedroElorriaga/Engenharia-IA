from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()


@tool
def get_weather_api(location: str) -> str:
    """
    get weather about the location provided by the user, 
    the response should be in this format: "The current temperature in {location} is 25°C with clear skies."

    """
    return f"The current temperature in {location} is 25°C with clear skies."


@tool
def fake_prize_draw(numbers: list[int]) -> int:
    """
    This is a fake prize draw that always returns the same number.

    """
    return 4


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

messages = [HumanMessage(content="Make a prize draw between 1 and 100")]
"""
Cada vez que você chama .invoke(), o modelo recebe tudo do zero. 
Ele não lembra o que aconteceu antes. Por isso você precisa construir 
manualmente o histórico da conversa na lista messages antes de cada chamada.

O LangChain usa typed messages para distinguir quem falou cada coisa na conversa:

HumanMessage → mensagem do usuário
AIMessage → resposta do modelo (isso é o que response_with_tool retorna)
ToolMessage → resultado de uma ferramenta

"""

llm_with_tool = llm.bind_tools([get_weather_api, fake_prize_draw])
response_with_tool = llm_with_tool.invoke(messages)
"""
A lista messages é o histórico completo da conversa. 
Você passa ela pro modelo para ele saber o contexto inteiro.

Nesse ponto o modelo respondeu com algo do tipo: 
"Preciso chamar a ferramenta get_weather_api com o argumento Barueri SP". 
Ele não respondeu ao usuário ainda — apenas sinalizou que quer usar uma tool.
"""
messages.append(response_with_tool)  # <-- isso é um AIMessage

for tool_call in response_with_tool.tool_calls:
    choose_function = {
        "get_weather_api": get_weather_api,
        "fake_prize_draw": fake_prize_draw,
    }[tool_call["name"]]
    print(tool_call)
    tool_result = choose_function.invoke(tool_call)
    messages.append(tool_result)

final_response = llm_with_tool.invoke(messages)

print("response: ", final_response)
