import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from app.providers.telegram_bot import TelegramBot
from app.observability.metrics import _rate_limit_store


@pytest.fixture(autouse=True)
def clear_rate_limit():
    _rate_limit_store.clear()
    yield


def test_telegram_chat_endpoint_returns_reply():
    client = TestClient(app)
    with patch.object(TelegramBot, "handle_update", new_callable=AsyncMock, return_value="Echo: hi"):
        response = client.post(
            "/v1/chat",
            json={
                "session_id": "telegram-test",
                "messages": [{"role": "user", "content": "hi"}],
                "provider": "telegram",
                "model": "telegram-model",
                "stream": False,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "telegram"
    assert body["message"]["content"] == "Echo: hi"


def test_telegram_settings_endpoint_exposes_telegram_config():
    client = TestClient(app)
    r = client.get("/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert "telegram" in body
    assert "token_set" in body["telegram"]
    assert "allowed_chat_ids" in body["telegram"]


def test_telegram_settings_update_sets_token():
    client = TestClient(app)
    r = client.post(
        "/v1/settings",
        json={"telegramToken": "secret-token"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["telegram"]["token_set"] is True
