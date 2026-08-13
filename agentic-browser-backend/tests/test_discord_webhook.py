import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.providers.discord import create_app


class FakeClient:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        class _Resp:
            status_code = 200
            def raise_for_status(self):
                pass
            request = None
        return _Resp()


def test_discord_webhook_receives_payload():
    with patch("app.providers.discord.httpx.AsyncClient", new=lambda **kwargs: FakeClient()):
        client = TestClient(create_app())
        payload = {"id": "wh-1", "token": "abc", "default_channel": "general"}
        r = client.post("/webhook/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "discord"
    assert body["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in body["content"]
