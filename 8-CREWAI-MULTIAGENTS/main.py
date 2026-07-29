"""
main.py — Ponto de entrada do projeto CrewAI.

Execute com:
    python main.py

Pré-requisitos:
    1. Ollama rodando localmente: https://ollama.com/
    2. Modelo baixado: ollama pull llama3.2
       (ou altere o model em agents.py para o que você tiver)
    3. Pacotes instalados: pip install crewai requests beautifulsoup4
"""

import time
from pathlib import Path
from crew import crew


def salvar_resultado(texto: str) -> Path:
    """Salva o relatório final em um arquivo .md com timestamp."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    caminho = Path(__file__).parent / f"relatorio_{timestamp}.md"
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def main() -> None:
    print("\n" + "=" * 60)
    print("  ANÁLISE DE RECLAMAÇÕES — RECLAME AQUI")
    print("  Empresas: Claro | Vivo | NET")
    print("=" * 60 + "\n")

    print("Iniciando o Crew... (isso pode levar alguns minutos)\n")

    # kickoff() dispara a execução de todas as tarefas em sequência.
    # O retorno é um objeto CrewOutput com o resultado final.
    resultado = crew.kickoff()

    print("\n" + "=" * 60)
    print("  RESULTADO FINAL")
    print("=" * 60 + "\n")
    print(resultado)

    # Salva o relatório em arquivo
    caminho = salvar_resultado(str(resultado))
    print(f"\n✓ Relatório salvo em: {caminho}")


if __name__ == "__main__":
    main()
