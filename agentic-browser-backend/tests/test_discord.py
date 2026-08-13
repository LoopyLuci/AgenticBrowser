import asyncio
import pytest
from unittest.mock import patch

from app.providers.discord import DiscordProvider, DiscordWebhook, create_app
from app.providers.chat import PROVIDERS
from app.state.store import init_state_db


init_state_db()


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


def test_discord_adapter_loads():
    provider = DiscordProvider()
    assert provider.key == "discord"


def test_discord_adapter_stub_response():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    with patch("app.providers.discord.httpx.AsyncClient", new=lambda **kwargs: FakeClient()):
        coro = provider.chat("stub-model", [], False)
        message = asyncio.run(coro)
    assert message["provider"] == "discord"
    assert message["model"] == "stub-model"
    assert "content" in message


def test_discord_adapter_requires_webhook():
    provider = DiscordProvider()
    with pytest.raises(RuntimeError, match="Missing webhook config"):
        asyncio.run(provider.chat("model", [], False))


def test_discord_webhook_returns_route_id():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    with patch("app.providers.discord.httpx.AsyncClient", new=lambda **kwargs: FakeClient()):
        coro = provider.chat("model", [], False)
        message = asyncio.run(coro)
    assert message["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in message["content"]


def test_discord_webhook_endpoint():
    with patch("app.providers.discord.httpx.AsyncClient", new=lambda **kwargs: FakeClient()):
        client = __import__("fastapi.testclient").testclient.TestClient(create_app())
        payload = {"id": "wh-1", "token": "abc", "default_channel": "general"}
        r = client.post("/webhook/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "discord"
    assert body["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in body["content"]
