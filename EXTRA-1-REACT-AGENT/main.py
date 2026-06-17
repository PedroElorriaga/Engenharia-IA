from graph import graph
from rich import print
from rich.markdown import Markdown
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.state import RunnableConfig
from prompts import SYSTEM_PROMPT


def main() -> None:
    agent = graph()
    config = RunnableConfig(configurable={"thread_id": 1})
    all_messages: list[BaseMessage] = []

    while True:
        user_input = input("Vc: ")
        print(Markdown(f"\n\n --- \n\n"))

        if user_input.lower() in {"exit", "quit"}:
            break

        human_message = HumanMessage(content=user_input)
        current_loop_messages = [human_message]

        if len(all_messages) == 0:
            current_loop_messages = [
                SystemMessage(SYSTEM_PROMPT), human_message]

        result = agent.invoke(
            {"messages": current_loop_messages}, config=config)

        print(Markdown(f"Agent: {result['messages'][-1].content}"))
        print(Markdown(f"\n\n --- \n\n"))

        all_messages = result["messages"]


if __name__ == "__main__":
    main()
