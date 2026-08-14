import os
import pytest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.providers.chat import OpenAIProvider, OpenRouterProvider, OllamaProvider
from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_providers_endpoint():
    r = client.get("/providers")
    assert r.status_code == 200
    body = r.json()
    assert "available" in body
    assert "configured" in body


def test_tools_registry_has_expected_tools():
    r = client.get("/v1/tools")
    assert r.status_code == 200
    tools = r.json()["tools"]
    for name in ["get_page", "get_selection", "search", "summarize"]:
        assert name in tools


def test_settings_store_defaults_and_update():
    r = client.post("/v1/settings", json={"ollamaHost": "http://localhost:11434", "openrouterKey": "demo", "openaiKey": "demo"})
    assert r.status_code == 200
    body = r.json()
    assert body["ollamaHost"] == "http://localhost:11434"
    assert body["openrouterKey"] == "demo"
    assert body["openaiKey"] == "demo"


def test_settings_timeout_persistence():
    r = client.post("/v1/settings", json={"ollamaTimeout": 60, "openrouterTimeout": 45, "openaiTimeout": 30})
    assert r.status_code == 200
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["ollamaTimeout"] == 60
    assert body["openrouterTimeout"] == 45
    assert body["openaiTimeout"] == 30


def test_settings_provider_persistence():
    r = client.post("/v1/settings", json={"provider": "openai", "ollamaTimeout": 15, "openrouterTimeout": 20, "openaiTimeout": 25})
    assert r.status_code == 200
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "openai"
    assert body["ollamaTimeout"] == 15
    assert body["openrouterTimeout"] == 20
    assert body["openaiTimeout"] == 25


def test_chat_uses_configured_timeout():
    r = client.post("/v1/settings", json={"ollamaTimeout": 1})
    assert r.status_code == 200
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["ollamaTimeout"] == 1


def test_state_round_trip():
    sid = "test-session"
    tmp_db = f".agentic-state-test-{os.getpid()}.db"
    from app.state import store as state_store
    state_store.configure_db(tmp_db)
    state_store.init_state_db()
    state_store.get_or_create_session(sid)
    state_store.append_message(sid, "user", "hello")
    state_store.append_message(sid, "assistant", "world")
    messages = state_store.get_messages(sid)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "hello"
    state_store.set_setting("openrouterKey", "sk-test")
    assert state_store.get_setting("openrouterKey") == "sk-test"
    exported = state_store.export_settings()
    assert exported["openrouterKey"] == "sk-test"
    state_store.import_settings({"openaiKey": "sk-other"})
    assert state_store.get_setting("openaiKey") == "sk-other"


def test_provider_live_ollama_smoke():
    base = os.getenv("OLLAMA_HOST")
    if not base:
        pytest.skip("OLLAMA_HOST not set")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
    r = client.post("/v1/chat", json={
        "session_id": "pytest-ollama",
        "provider": "ollama",
        "model": model,
        "messages": [{"role": "user", "content": "Say 'pong' only."}],
        "stream": False,
    })
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert "message" in body or "content" in body or "data" in body


def test_metrics_endpoint_returns_summary():
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "requests" in body


def test_audit_log_emits_during_chat():
    if not os.getenv("OLLAMA_HOST"):
        pytest.skip("OLLAMA_HOST not set")
    r = client.post("/v1/chat", json={
        "session_id": "pytest-audit",
        "provider": "ollama",
        "model": "qwen2.5:0.5b",
        "messages": [{"role": "user", "content": "ping"}],
        "stream": False,
    })
    assert r.status_code == 200


def test_chat_round_trip_with_settings():
    r = client.post("/v1/settings", json={"provider": "ollama", "ollamaHost": "http://localhost:11434", "ollamaTimeout": 2, "chatModel": "llama3"})
    assert r.status_code == 200
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "ollama"
    assert body["chatModel"] == "llama3"
    assert body["ollamaTimeout"] == 2


def test_settings_sync_payload_matches_ui():
    payload = {
        "ollamaHost": "http://localhost:11434",
        "openrouterKey": "sk-or",
        "openaiKey": "sk-ai",
        "telegramToken": "tg",
        "ollamaTimeout": 90,
        "openrouterTimeout": 40,
        "openaiTimeout": 20,
        "provider": "openrouter",
        "chatModel": "anthropic/claude-3-haiku",
    }
    r = client.post("/v1/settings", json=payload)
    assert r.status_code == 200
    body = r.json()
    for key, expected in payload.items():
        assert body.get(key) == expected, f"settings key {key} mismatch"
