import pytest

from fastapi.testclient import TestClient

from app.providers.discord import create_app


def test_discord_webhook_receives_payload():
    client = TestClient(create_app())
    payload = {"id": "wh-1", "token": "abc", "default_channel": "general"}
    r = client.post("/webhook/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "discord"
    assert body["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in body["content"]
