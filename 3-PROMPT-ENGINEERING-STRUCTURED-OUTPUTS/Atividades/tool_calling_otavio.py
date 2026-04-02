import os
from dotenv import load_dotenv
from rich import print
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv()


@tool
def sum_numbers(a: int, b: int) -> int:
    """
    This tool sums two numbers a + b and returns the result.
    """
    return a + b


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.5
)

system_message = SystemMessage(
    content="You are a helpful assistant, that answers questions about math"
    "use tools to answer questions about math"
)

human_message = HumanMessage(content="How much is 2 + 2?")

messages = [system_message, human_message]
tools = [sum_numbers]
tools_by_name = {tool.name: tool for tool in tools}

llm_with_tools = llm.bind_tools(tools)
llm_response = llm_with_tools.invoke(messages)
messages.append(llm_response)

if isinstance(llm_response, AIMessage) and getattr(llm_response, "tool_calls", None):
    call = llm_response.tool_calls[-1]
    name, args, id_ = call["name"], call["args"], call["id"]

    try:
        content = tools_by_name[name].invoke(args)
    except (KeyError, TypeError) as e:
        content = f"Please fix your mistakes {str(e)}"

    tool_message = ToolMessage(content=content, tool_call_id=id_)
    messages.append(tool_message)

    llm_response = llm_with_tools.invoke(messages)
    messages.append(llm_response)

print(messages)
