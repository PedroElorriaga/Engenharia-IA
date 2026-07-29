"""
tools.py — Ferramentas personalizadas para o Crew.

O CrewAI usa o decorator @tool para transformar uma função Python
em uma ferramenta que os agentes podem invocar autonomamente.
"""

import requests
from crewai.tools import tool


# Mapeamento: nome amigável → slug usado na URL do Reclame Aqui
EMPRESAS_ALVO = {
    "Claro": "claro",
    "Vivo": "vivo",
    "NET": "net",
}


def _buscar_reclamacoes(nome: str, slug: str) -> str:
    """Faz o scraping de reclamações de uma empresa no Reclame Aqui."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.reclameaqui.com.br/",
    }

    # API pública do Reclame Aqui — retorna as reclamações mais recentes
    url = (
        f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-api"
        f"/query/companyComplains/10/0?company={slug.upper()}"
    )

    resposta = requests.get(url, headers=headers, timeout=15)
    resposta.raise_for_status()
    dados = resposta.json()

    reclamacoes = (
        dados.get("hits", {}).get("hits", [])
        or dados.get("complains", {}).get("data", [])
        or []
    )

    if not reclamacoes:
        return f"[{nome}] Nenhuma reclamação encontrada via API."

    linhas = [f"{'='*50}", f"EMPRESA: {nome}",
              f"Total de reclamações recentes: {len(reclamacoes)}", ""]
    for i, r in enumerate(reclamacoes[:5], start=1):
        # Os campos variam conforme o endpoint retornado
        source = r.get("_source", r)
        titulo = source.get("title", source.get("titulo", "Sem título"))
        descricao = source.get(
            "description", source.get("descricao", ""))[:300]
        status = source.get("status", "N/A")

        linhas.append(f"Reclamação #{i}")
        linhas.append(f"  Título  : {titulo}")
        linhas.append(f"  Trecho  : {descricao}...")
        linhas.append(f"  Status  : {status}")
        linhas.append("")

    return "\n".join(linhas)


@tool("Coletar Reclamações do Reclame Aqui")
def coletar_reclamacoes(_: str = "") -> str:
    """
    Coleta as reclamações mais recentes das empresas Claro, Vivo e NET
    no site Reclame Aqui. Retorna os dados brutos para análise.
    Não requer nenhum parâmetro de entrada.
    """
    resultados = []
    for nome, slug in EMPRESAS_ALVO.items():
        try:
            resultados.append(_buscar_reclamacoes(nome, slug))
        except requests.HTTPError as exc:
            resultados.append(
                f"[{nome}] Erro HTTP {exc.response.status_code}: {exc}")
        except requests.RequestException as exc:
            resultados.append(f"[{nome}] Erro de conexão: {exc}")
        except Exception as exc:  # noqa: BLE001
            resultados.append(f"[{nome}] Erro inesperado: {exc}")

    return "\n\n".join(resultados)
