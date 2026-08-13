import pytest

from fastapi.testclient import TestClient

from main import app
from app.observability.metrics import _rate_limit_store


def test_telegram_settings_endpoint_exposes_telegram_config():
    _rate_limit_store.clear()
    client = TestClient(app)
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert "telegram" in body
    assert "token_set" in body["telegram"]
    assert "allowed_chat_ids" in body["telegram"]


def test_telegram_settings_update_via_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "env-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "1,2")
    _rate_limit_store.clear()
    client = TestClient(app)
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["telegram"]["token_set"] is True
    assert body["telegram"]["allowed_chat_ids"] == ["1", "2"]
