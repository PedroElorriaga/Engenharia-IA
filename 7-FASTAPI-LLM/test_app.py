# ==============================================================================
# Explicando os testes com minhas palavras (Exercício de fixação)
#
# A ideia geral dos testes aqui é validar o contrato da API sem precisar
# do Ollama de verdade rodando. Para isso usamos "mocks" — objetos falsos
# que imitam o comportamento do ChatOllama mas retornam respostas controladas.
#
# _FAKE_ANSWER: é a resposta falsa que o mock vai retornar. Assim sabemos
# exatamente o que esperar no payload de resposta.
#
# _make_llm_mock(): fabrica um ChatOllama falso. Criamos dois MagicMocks:
#   - mock_response: imita o objeto retornado pelo .invoke(), com um .content
#   - mock_llm: imita o próprio ChatOllama, onde .invoke() devolve o mock_response
#
# @patch("main.ChatOllama"): esse decorator intercepta a criação do ChatOllama
# dentro do main.py e substitui pela nossa versão falsa durante o teste.
# Assim o teste não precisa de internet, nem do Ollama instalado.
#
# Teste 1 - test_ask_returns_expected_payload:
#   Verifica que ao fazer um POST /ask com uma pergunta simples:
#   - o status code é 200
#   - o payload contém os três campos: answer, latency_ms e model
#   - cada campo tem o tipo correto (str, int, str)
#   - o answer não está vazio
#   - o latency_ms é >= 0 (nunca negativo)
#
# Teste 2 - test_ask_with_history:
#   Verifica que o endpoint aceita o campo history corretamente.
#   Passamos um histórico de conversa anterior (user + assistant) junto com
#   a nova pergunta. Confirmamos que a resposta ainda é o _FAKE_ANSWER,
#   ou seja, a history foi aceita sem quebrar nada.
#
# Teste 3 - test_ask_502_on_model_error:
#   Simula uma falha real do Ollama (ex: serviço fora do ar).
#   Fazemos o mock_llm.invoke() lançar um RuntimeError.
#   Esperamos que a API capture esse erro e devolva HTTP 502 (Bad Gateway),
#   que é o código correto para "o serviço de terceiro falhou".
# ==============================================================================

from main import app
from fastapi.testclient import TestClient
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))


_FAKE_ANSWER = "Use `with open(...) as f:` to avoid resource leaks."


def _make_llm_mock():
    mock_response = MagicMock()
    mock_response.content = _FAKE_ANSWER
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_response
    return mock_llm


class AskEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("main.ChatOllama")
    def test_ask_returns_expected_payload(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = _make_llm_mock()

        response = self.client.post(
            "/ask",
            json={
                "question": "Review this Python function for bugs and suggest improvements"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("answer", payload)
        self.assertIn("latency_ms", payload)
        self.assertIn("model", payload)
        self.assertIsInstance(payload["answer"], str)
        self.assertTrue(payload["answer"])
        self.assertIsInstance(payload["latency_ms"], int)
        self.assertGreaterEqual(payload["latency_ms"], 0)
        self.assertIsInstance(payload["model"], str)

    @patch("main.ChatOllama")
    def test_ask_with_history(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = _make_llm_mock()

        response = self.client.post(
            "/ask",
            json={
                "question": "What about using pathlib instead?",
                "history": [
                    {"role": "user", "content": "How do I read a file in Python?"},
                    {"role": "assistant", "content": "Use open() with a context manager."},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], _FAKE_ANSWER)

    @patch("main.ChatOllama")
    def test_ask_502_on_model_error(self, mock_cls: MagicMock) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = RuntimeError("Ollama unreachable")
        mock_cls.return_value = mock_llm

        response = self.client.post(
            "/ask",
            json={"question": "Why does my code crash?"},
        )

        self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
