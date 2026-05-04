import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from rich import print


# Usei TypedDict pq é mais rapido, leve e mais recomendado para LangGraph
class State(TypedDict):
    # Reducer para acumular o caminho dos nodes visitados
    node_path: Annotated[list[str], operator.add]


# Criando os Nodes
def node_a(state: State) -> State:
    output_node: State = {"node_path": ["A"]}
    return output_node


def node_b(state: State) -> State:
    output_node: State = {"node_path": ["B"]}
    return output_node


# Criando o builder do grafo
builder = StateGraph(State)

# Adicionando os nodes ao grafo
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)


# Adicionando os edges entre os nodes
builder.add_edge("__start__", "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "__end__")


# Compilando o grafo
graph = builder.compile()

# Gerando imagem do grafo
# graph.get_graph().draw_mermaid_png(output_file_path="grafo.png")

result = graph.invoke({"node_path": []})
print(f"{result=}")
