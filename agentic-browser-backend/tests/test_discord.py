import pytest

from app.providers.discord import DiscordProvider, DiscordWebhook, create_app


def test_discord_adapter_loads():
    provider = DiscordProvider()
    assert provider.key == "discord"


def test_discord_adapter_stub_response():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    message = __import__("asyncio").run(provider.chat("stub-model", [], False))
    assert message["provider"] == "discord"
    assert message["model"] == "stub-model"
    assert "content" in message


def test_discord_adapter_requires_webhook():
    provider = DiscordProvider()
    with pytest.raises(RuntimeError, match="Missing webhook config"):
        __import__("asyncio").run(provider.chat("model", [], False))


def test_discord_webhook_returns_route_id():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    message = __import__("asyncio").run(provider.chat("model", [], False))
    assert message["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in message["content"]


def test_discord_webhook_endpoint():
    client = __import__("fastapi.testclient").testclient.TestClient(create_app())
    payload = {"id": "wh-1", "token": "abc", "default_channel": "general"}
    r = client.post("/webhook/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "discord"
    assert body["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in body["content"]
