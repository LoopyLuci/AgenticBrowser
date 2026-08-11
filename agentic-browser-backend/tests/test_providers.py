import os
import pytest
import httpx


def _client(base=None):
    return httpx.Client(base_url=base or os.getenv("AGENTIC_BACKEND", "http://127.0.0.1:8123"), timeout=15)


def test_health():
    with _client() as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_providers_endpoint():
    with _client() as c:
        r = c.get("/providers")
        assert r.status_code == 200
        body = r.json()
        assert "available" in body
        assert "configured" in body


@pytest.mark.skipif(not os.getenv("AGENTIC_TEST_OLLAMA"), reason="Ollama not configured")
def test_ollama_live():
    host = os.getenv("AGENTIC_TEST_OLLAMA_HOST", "http://localhost:11434")
    with _client() as c:
        r = c.get("/providers")
        assert r.status_code == 200
        assert "ollama" in r.json()["available"]


@pytest.mark.skipif(not os.getenv("AGENTIC_TEST_OPENROUTER"), reason="OpenRouter not configured")
def test_openrouter_live():
    with _client() as c:
        r = c.get("/providers")
        assert r.status_code == 200
        assert "openrouter" in r.json()["available"]


@pytest.mark.skipif(not os.getenv("AGENTIC_TEST_OPENAI"), reason="OpenAI not configured")
def test_openai_live():
    with _client() as c:
        r = c.get("/providers")
        assert r.status_code == 200
        assert "openai" in r.json()["available"]
