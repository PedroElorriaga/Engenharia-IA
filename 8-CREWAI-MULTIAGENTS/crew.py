"""
crew.py — Montagem e configuração do Crew (o "time" de agentes).

O Crew é quem:
  - Agrupa os agentes e as tarefas
  - Define o Process (como as tarefas são executadas)
  - Controla memória, cache e logging

Process.sequential → tarefas executadas uma após a outra, em ordem.
Process.hierarchical → um agente-gerente distribui e delega tarefas
                        (requer um manager_llm configurado).

Para aprender, usamos Process.sequential — mais fácil de seguir o fluxo.
"""

from crewai import Crew, Process
from agents import agente_pesquisador, agente_redator, agente_revisor
from tasks import tarefa_coleta, tarefa_redacao, tarefa_revisao


crew = Crew(
    # A ordem aqui é apenas informativa; quem define a ordem de execução
    # são as tarefas (e o campo `context` delas).
    agents=[agente_pesquisador, agente_redator, agente_revisor],

    # As tarefas serão executadas nesta ordem exata.
    tasks=[tarefa_coleta, tarefa_redacao, tarefa_revisao],

    # Process.sequential: tarefa 1 → tarefa 2 → tarefa 3
    process=Process.sequential,

    # verbose=True: imprime o raciocínio de cada agente no terminal.
    # Ótimo para aprender o que está acontecendo internamente.
    verbose=True,
)
