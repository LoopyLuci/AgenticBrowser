from __future__ import annotations

import os
from typing import Any

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.providers.chat import PROVIDERS
from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_settings_and_chat_round_trip(client: TestClient):
    payload = {
        "provider": "openrouter",
        "chatModel": "openai/gpt-4o-mini",
        "ollamaHost": "http://localhost:11434",
        "openrouterKey": "sk-or",
        "openaiKey": "sk-ai",
        "telegramToken": "tg",
        "ollamaTimeout": 90,
        "openrouterTimeout": 40,
        "openaiTimeout": 20,
    }

    r = client.post("/v1/settings", json=payload)
    assert r.status_code == 200
    body = r.json()
    for key, expected in payload.items():
        assert body.get(key) == expected, f"settings key {key} mismatch"

    r = client.get("/v1/settings")
    assert r.status_code == 200
    assert r.json() == body


def test_providers_list_reflects_configured(client: TestClient):
    client.post("/v1/settings", json={"provider": "openai", "openaiKey": "sk-ai"})
    r = client.get("/providers")
    assert r.status_code == 200
    body = r.json()
    assert "available" in body
    assert "configured" in body
    assert body["configured"].get("provider") == "openai"


def test_chat_schema_accepts_full_payload(client: TestClient):
    r = client.post("/v1/settings", json={"provider": "ollama", "ollamaHost": "http://localhost:11434", "chatModel": "llama3", "ollamaTimeout": 5})
    assert r.status_code == 200

    fake_msg = {"content": "pong"}

    with patch("app.providers.chat.OllamaProvider.chat", return_value=fake_msg):
        r = client.post(
            "/v1/chat",
            json={
                "session_id": "integration-test",
                "provider": "ollama",
                "model": "llama3",
                "messages": [{"role": "user", "content": "Say 'pong' only."}],
                "stream": False,
            },
        )
    assert r.status_code == 200
    body = r.json()
    assert "message" in body or "provider" in body or "content" in body


def test_history_endpoint_returns_messages(client: TestClient):
    sid = "integration-history"
    fake_msg = {"content": "ok"}
    with patch("app.providers.chat.OllamaProvider.chat", return_value=fake_msg):
        r = client.post("/v1/chat", json={"session_id": sid, "provider": "ollama", "model": "llama3", "messages": [{"role": "user", "content": "hi"}], "stream": False})
    assert r.status_code == 200
    r = client.get(f"/v1/state/history?session_id={sid}&limit=10")
    assert r.status_code == 200
    body = r.json()
    assert body["session_id"] == sid
    assert isinstance(body["messages"], list)


def test_stream_chat_endpoint_returns_event_source(client: TestClient):
    fake_stream = iter([{"message": {"content": "tok1"}}, {"message": {"content": "tok2"}}])
    with patch("app.providers.chat.OllamaProvider.chat", return_value=fake_stream):
        r = client.post(
            "/v1/chat/stream",
            json={
                "session_id": "integration-stream",
                "provider": "ollama",
                "model": "llama3",
                "messages": [{"role": "user", "content": "Say 'pong' only."}],
                "stream": True,
            },
        )
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("text/event-stream")


def test_provider_router_returns_400_for_unsupported(client: TestClient):
    r = client.post("/v1/chat", json={"session_id": "x", "provider": "unknown", "model": "m", "messages": [], "stream": False})
    assert r.status_code == 400


def test_extension_settings_payload_accepted(client: TestClient):
    payload = {
        "provider": "openrouter",
        "chatModel": "anthropic/claude-3-haiku",
        "ollamaHost": "http://localhost:11434",
        "openrouterKey": "sk-or",
        "openaiKey": "sk-ai",
        "ollamaTimeout": 12,
        "openrouterTimeout": 8,
        "openaiTimeout": 4,
    }
    r = client.post("/v1/settings", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "openrouter"
    assert body["chatModel"] == "anthropic/claude-3-haiku"
    assert body["ollamaTimeout"] == 12


def test_available_providers_include_expected(client: TestClient):
    r = client.get("/providers")
    assert r.status_code == 200
    available = r.json()["available"]
    for expected in ["ollama", "openrouter", "openai"]:
        assert expected in available
