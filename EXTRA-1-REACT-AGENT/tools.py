from langchain_core.tools import tool, BaseTool


@tool
def multiply(a: int, b: int) -> float:
    """Multiplies two numbers. Use this whenever multiplication is required."""
    return a * b


LLM_TOOLKIT: list[BaseTool] = [multiply]
LLM_TOOLKIT_NAMES: dict[str, BaseTool] = {
    tool.name: tool for tool in LLM_TOOLKIT}
