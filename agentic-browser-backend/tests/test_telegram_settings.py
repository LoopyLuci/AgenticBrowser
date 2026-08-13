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
    assert "telegramToken" in body
    assert "telegram_allowed_chat_ids" in body


def test_telegram_settings_update_via_env(monkeypatch):
    _rate_limit_store.clear()
    client = TestClient(app)
    r = client.post(
        "/v1/settings",
        json={"telegramToken": "env-token", "telegram_allowed_chat_ids": ["1", "2"]},
    )
    assert r.status_code == 200
    assert r.json().get("telegramToken") == "env-token"
