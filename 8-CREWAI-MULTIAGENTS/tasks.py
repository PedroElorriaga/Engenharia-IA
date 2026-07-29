"""
tasks.py — Definição das tarefas que cada agente deve executar.

Uma Task no CrewAI define:
  - description : o que precisa ser feito (o "briefing" da tarefa)
  - expected_output: o formato/conteúdo esperado no resultado
  - agent       : qual agente é responsável pela tarefa
  - context     : lista de Tasks anteriores cujo output alimenta esta tarefa
                  (isso cria a cadeia de dependências entre agentes)
"""

from crewai import Task
from agents import agente_pesquisador, agente_redator, agente_revisor


# ── Tarefa 1 — Coleta de dados ───────────────────────────────────────────────
tarefa_coleta = Task(
    description=(
        "Use a ferramenta disponível para coletar as reclamações mais recentes "
        "das empresas Claro, Vivo e NET no Reclame Aqui. "
        "Após coletar os dados brutos, organize-os identificando:\n"
        "1. Os tipos de problemas mais frequentes por empresa\n"
        "2. O tom geral das reclamações (urgente, frustrado, resignado, etc.)\n"
        "3. Quais problemas parecem sistêmicos (aparecem em múltiplas reclamações)\n"
        "Responda em português."
    ),
    expected_output=(
        "Um relatório estruturado com os dados coletados de cada empresa, "
        "incluindo os principais problemas identificados e padrões de reclamação. "
        "Deve estar em português e conter dados concretos das reclamações."
    ),
    agent=agente_pesquisador,
)


# ── Tarefa 2 — Redação do resumo executivo ───────────────────────────────────
tarefa_redacao = Task(
    description=(
        "Com base nos dados coletados pelo pesquisador, escreva um Resumo Executivo "
        "profissional sobre a reputação das empresas Claro, Vivo e NET no Reclame Aqui. "
        "O resumo deve conter:\n\n"
        "1. **Visão Geral**: comparativo rápido das três empresas\n"
        "2. **Análise por Empresa** (para cada uma):\n"
        "   - Principais problemas reclamados\n"
        "   - Padrões identificados\n"
        "   - Nível de gravidade percebido\n"
        "3. **Pontos de Melhoria**: pelo menos 3 recomendações práticas e específicas "
        "   para cada empresa, baseadas diretamente nas reclamações\n"
        "4. **Conclusão**: qual empresa tem o pior cenário e por quê\n\n"
        "Tom: profissional, direto, sem jargões desnecessários. Em português."
    ),
    expected_output=(
        "Um Resumo Executivo completo em português, com seções bem definidas, "
        "linguagem profissional e recomendações práticas baseadas nos dados reais."
    ),
    agent=agente_redator,
    context=[tarefa_coleta],  # O redator usa o output do pesquisador
)


# ── Tarefa 3 — Revisão e refinamento ────────────────────────────────────────
tarefa_revisao = Task(
    description=(
        "Revise o Resumo Executivo produzido pelo redator e faça os ajustes necessários. "
        "Verifique especificamente:\n\n"
        "1. **Consistência de dados**: as afirmações estão alinhadas com os dados coletados?\n"
        "2. **Clareza**: cada ponto está explicado de forma objetiva e sem ambiguidade?\n"
        "3. **Qualidade das recomendações**: são específicas e acionáveis, ou genéricas demais?\n"
        "4. **Tom profissional**: o texto é adequado para ser apresentado a executivos?\n"
        "5. **Estrutura**: o relatório flui bem e é fácil de navegar?\n\n"
        "Entregue a versão final revisada e aprimorada. Em português."
    ),
    expected_output=(
        "A versão final e aprimorada do Resumo Executivo em português, "
        "com todos os ajustes feitos, pronta para ser apresentada a stakeholders. "
        "Inclua uma nota curta no final listando as principais melhorias realizadas na revisão."
    ),
    agent=agente_revisor,
    context=[tarefa_coleta, tarefa_redacao],  # O revisor vê tudo
)
