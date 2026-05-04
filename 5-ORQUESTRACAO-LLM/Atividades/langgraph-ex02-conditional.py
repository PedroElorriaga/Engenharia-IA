import operator
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph
from rich import print


# Usei TypedDict pq é mais rapido, leve e mais recomendado para LangGraph
class State(TypedDict):
    # Reducer para acumular o caminho dos nodes visitados
    node_path: Annotated[list[str], operator.add]
    conditional_number: int


# Criando os Nodes
def node_a(state: State) -> State:
    output_node: State = {"node_path": ["A"]}
    return output_node


def node_b(state: State) -> State:
    output_node: State = {"node_path": ["B"]}
    return output_node


def node_c(state: State) -> State:
    output_node: State = {"node_path": ["C"]}
    return output_node


def the_conditional(state: State) -> Literal["goes_to_b", "goes_to_c"]:
    if state["conditional_number"] > 10:
        return "goes_to_c"

    return "goes_to_b"


# Criando o builder do grafo
builder = StateGraph(State)

# Adicionando os nodes ao grafo
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

# Adicionando os edges entre os nodes
builder.add_edge("__start__", "node_a")
builder.add_conditional_edges("node_a", the_conditional, {
    "goes_to_b": "node_b",
    "goes_to_c": "node_c"
})
builder.add_edge("node_b", "__end__")
builder.add_edge("node_c", "__end__")


# Compilando o grafo
graph = builder.compile()

# Gerando imagem do grafo
graph.get_graph().draw_mermaid_png(output_file_path="grafo-conditional.png")

result = graph.invoke({"node_path": [], "conditional_number": 0})
print(f"{result=}")
