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
