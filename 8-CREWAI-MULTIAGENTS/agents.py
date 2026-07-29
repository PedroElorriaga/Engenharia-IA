"""
agents.py — Definição dos três agentes do Crew.

Cada agente tem:
  - role     : o "cargo" dele dentro do time
  - goal     : o objetivo principal
  - backstory: contexto/personalidade que guia o comportamento do LLM
  - llm      : modelo que o agente vai usar
  - tools    : lista de ferramentas que ele pode invocar
  - verbose  : imprime o raciocínio do agente no terminal (ótimo para aprender)
"""

import os
from crewai import Agent, LLM
from tools import coletar_reclamacoes

# ── Configuração do LLM (Ollama local) ──────────────────────────────────────
# O CrewAI usa LiteLLM internamente, então o formato do model é
# "ollama/<nome-do-modelo>".  Troque "llama3.2" pelo modelo que você tiver
# rodando no Ollama (ex.: "llama3", "mistral", "gemma3", etc.)
llm = LLM(
    # llm_type="llama3",
    model="ollama/" + os.getenv("OLLAMA_MODEL", "llama3.2"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)


# ── Agente 1 — Pesquisador / Scraper ────────────────────────────────────────
agente_pesquisador = Agent(
    role="Pesquisador de Reclamações",
    goal=(
        "Coletar e organizar as reclamações mais recentes das empresas "
        "Claro, Vivo e NET no Reclame Aqui, identificando os principais "
        "problemas e padrões de insatisfação dos consumidores."
    ),
    backstory=(
        "Você é um analista de dados especializado em monitoramento de "
        "reputação de marcas. Seu trabalho é vasculhar plataformas de "
        "reclamação e extrair informações relevantes de forma estruturada, "
        "garantindo que nenhum problema recorrente passe despercebido."
    ),
    tools=[coletar_reclamacoes],  # Única ferramenta: o scraper
    llm=llm,
    verbose=True,
)


# ── Agente 2 — Redator ──────────────────────────────────────────────────────
agente_redator = Agent(
    role="Redator de Relatórios Executivos",
    goal=(
        "Transformar os dados brutos de reclamações em um resumo executivo "
        "claro, objetivo e bem estruturado, com pontos de melhoria "
        "específicos para cada empresa."
    ),
    backstory=(
        "Você é um consultor sênior de experiência do cliente (CX) com "
        "quinze anos de experiência. Você tem o dom de pegar montanhas de "
        "dados e transformá-los em insights acionáveis que executivos "
        "entendem em minutos. Seus relatórios sempre incluem: contexto, "
        "principais problemas, padrões identificados e recomendações claras."
    ),
    tools=[],  # O redator não precisa de ferramentas externas
    llm=llm,
    verbose=True,
)


# ── Agente 3 — Revisor / Tuner ───────────────────────────────────────────────
agente_revisor = Agent(
    role="Revisor e Especialista em Qualidade",
    goal=(
        "Revisar o relatório do redator, garantindo precisão, clareza, "
        "tom profissional e que todas as recomendações sejam práticas "
        "e bem fundamentadas nas reclamações coletadas."
    ),
    backstory=(
        "Você é um editor sênior com experiência em jornalismo investigativo "
        "e consultoria empresarial. Você tem olho crítico para inconsistências, "
        "linguagem vaga ou recomendações genéricas. Seu padrão de qualidade "
        "é alto: cada afirmação precisa ter base nos dados, cada recomendação "
        "deve ser específica e aplicável. Você também ajusta o tom para que "
        "o texto seja profissional mas acessível."
    ),
    tools=[],  # O revisor trabalha apenas com o texto recebido
    llm=llm,
    verbose=True,
)
