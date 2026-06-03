from mcp.server.fastmcp import FastMCP

mcp = FastMCP("servidor-produtos")

PRODUTOS = {
    "001": {"nome": "Teclado", "preco": 150.0, "estoque": 10},
    "002": {"nome": "Mouse",   "preco": 80.0,  "estoque": 5},
    "003": {"nome": "Monitor", "preco": 900.0, "estoque": 2},
}

# Ferramenta 1 — Buscar produto por ID


@mcp.tool()
def buscar_produto(produto_id: str) -> dict:
    """Busca informações de um produto pelo ID."""
    produto = PRODUTOS.get(produto_id)
    if not produto:
        return {"erro": f"Produto {produto_id} não encontrado"}
    return produto

# Ferramenta 2 — Listar todos os produtos


@mcp.tool()
def listar_produtos() -> list:
    """Lista todos os produtos disponíveis."""
    return [
        {"id": pid, **info}
        for pid, info in PRODUTOS.items()
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
