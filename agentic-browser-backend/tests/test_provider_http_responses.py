import pytest
from unittest.mock import patch

from app.providers.chat import OpenRouterProvider, OpenAIProvider, OllamaProvider


def test_openrouter_chat_returns_assistant_message():
    provider = OpenRouterProvider("fake-key")
    response_payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello from OpenRouter",
                }
            }
        ]
    }
    with patch("httpx.AsyncClient.post", return_value=type("Resp", (), {"raise_for_status": lambda self: None, "json": lambda self: response_payload})()):
        import asyncio

        result = asyncio.run(provider.chat("model", [{"role": "user", "content": "hi"}]))
    assert result["content"] == "Hello from OpenRouter"


def test_openai_chat_returns_assistant_message():
    provider = OpenAIProvider("fake-key")
    response_payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello from OpenAI",
                }
            }
        ]
    }
    with patch("httpx.AsyncClient.post", return_value=type("Resp", (), {"raise_for_status": lambda self: None, "json": lambda self: response_payload})()):
        import asyncio

        result = asyncio.run(provider.chat("model", [{"role": "user", "content": "hi"}]))
    assert result["content"] == "Hello from OpenAI"


def test_ollama_chat_returns_message_field():
    provider = OllamaProvider("http://localhost:11434")
    response_payload = {
        "message": {
            "role": "assistant",
            "content": "Hello from Ollama",
        }
    }
    with patch("httpx.AsyncClient.post", return_value=type("Resp", (), {"raise_for_status": lambda self: None, "json": lambda self: response_payload})()):
        import asyncio

        result = asyncio.run(provider.chat("model", [{"role": "user", "content": "hi"}]))
    assert result["content"] == "Hello from Ollama"
