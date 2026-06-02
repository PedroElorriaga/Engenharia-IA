import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from rich import print
from langsmith import Client
from rag.ingest import ingest
from redis_util.redis_client import SemanticCache
from utils.rate_limiting import RateLimiter

load_dotenv()


class Agent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.llm = self.__llm_connection()
        self.messages = []
        self.collection = ingest()
        self.smith_client = Client()
        self.redis_client = SemanticCache(threshold=0.85, ttl=60)
        self.rate_limit = RateLimiter()

    def __llm_connection(self) -> ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(
            model="gemma-4-31b-it",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.4
        )

        return llm

    def __save_message(self, message: HumanMessage | SystemMessage | AIMessage):
        self.messages.append(message)

    def __check_redis_cache(self, query: str):
        cached_response = self.redis_client.get(query)
        return cached_response if cached_response else None

    def query(self, query: str):
        if not self.rate_limit.allow_request(self.user_id):
            print("Rate limit exceeded. Please try again later.")
            return

        cached_response = self.__check_redis_cache(query)
        if cached_response:
            print("cache hit")
            return cached_response

        collection_response = self.collection.query(
            query_texts=[query],
            n_results=3
        )

        self.__save_message(SystemMessage(
            content=self.smith_client.pull_prompt("pedrinhos_company_assistant").format(
                documents=collection_response.get('documents')[0])
        ))
        self.__save_message(HumanMessage(content=query))

        llm_response = self.llm.invoke(self.messages)
        self.__save_message(llm_response)

        self.redis_client.set(
            query, self.messages[-1].content[-1].get("text"))

        return self.messages[-1].content[-1].get("text")


if __name__ == "__main__":
    agent = Agent("123")
    response = agent.query("Como funciona o banco de horas")
    response_cached = agent.query("Como funciona o banco de horas")
    print("response:", response)
    print("response_cached:", response_cached)
    agent.query("Como funciona o banco de horas?")
    agent.query("Informacoes sobre banco de horas")
    agent.query("como funciona o banco de horas na pedrinhos?")
    agent.query("Como funciona o banco de horas")
