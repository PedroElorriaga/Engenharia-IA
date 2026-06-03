import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from rich import print

load_dotenv()


async def main():
    # Conecta ao MCP Server
    client = MultiServerMCPClient(
        {
            "produtos": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )

    # Pega as ferramentas expostas pelo server
    tools = await client.get_tools()

    # Cria o agente com as ferramentas do MCP
    agente = create_agent(
        ChatGoogleGenerativeAI(
            model="gemma-4-31b-it", api_key=os.getenv("GEMINI_API_KEY")),
        tools
    )

    # Usa o agente normalmente
    resposta = await agente.ainvoke({
        "messages": "Quais produtos estão disponíveis? Me mostre os detalhes do produto 002 e poderia somar o valor de estoque desse produto"
    })

    print(resposta["messages"][-1].content[-1].get("text"))

if __name__ == "__main__":
    asyncio.run(main())
