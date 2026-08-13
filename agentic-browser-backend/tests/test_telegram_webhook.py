import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.providers.telegram_bot import TelegramBot, TelegramUpdate, create_app


def test_telegram_webhook_processes_message():
    client = TestClient(create_app())
    payload = {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "text": "hello",
            "from": {"username": "user1"},
        },
    }
    with patch.object(TelegramBot, "_send", new_callable=AsyncMock, return_value={"ok": True}):
        r = client.post("/webhook/token123", json=payload)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_telegram_webhook_rejects_empty_token():
    client = TestClient(create_app())
    payload = {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "text": "hello",
            "from": {"username": "user1"},
        },
    }
    r = client.post("/webhook/", json=payload)
    assert r.status_code == 404
