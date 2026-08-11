import os
import pytest
from fastapi.testclient import TestClient
from app.tools.registry import list_tools, get
from app.providers.chat import PROVIDERS, OllamaProvider
from app.settings.store import SettingsStore
from app.state.store import (
    init_state_db,
    get_or_create_session,
    append_message,
    get_messages,
    set_setting,
    get_setting,
    export_settings,
    import_settings,
)

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
    assert body["ollama"]["base"] == "http://localhost:11434"
    assert body["openrouter"]["key_set"] is True
    assert body["openai"]["key_set"] is True


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
