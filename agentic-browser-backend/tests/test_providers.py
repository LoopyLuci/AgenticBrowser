import os
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_providers_endpoint(client: TestClient):
    r = client.get("/providers")
    assert r.status_code == 200
    body = r.json()
    assert "available" in body
    assert "configured" in body


@pytest.mark.skipif(not os.getenv("AGENTIC_TEST_OLLAMA"), reason="Ollama not configured")
def test_ollama_live(client: TestClient):
    r = client.get("/providers")
    assert r.status_code == 200
    assert "ollama" in r.json()["available"]


@pytest.mark.skipif(not os.getenv("AGENTIC_TEST_OPENROUTER"), reason="OpenRouter not configured")
def test_openrouter_live(client: TestClient):
    r = client.get("/providers")
    assert r.status_code == 200
    assert "openrouter" in r.json()["available"]


@pytest.mark.skipif(not os.getenv("AGENTIC_TEST_OPENAI"), reason="OpenAI not configured")
def test_openai_live(client: TestClient):
    r = client.get("/providers")
    assert r.status_code == 200
    assert "openai" in r.json()["available"]
