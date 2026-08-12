import pytest

from app.providers.discord import DiscordProvider, DiscordWebhook


def test_discord_adapter_loads():
    provider = DiscordProvider()
    assert provider.key == "discord"


def test_discord_adapter_stub_response():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    message = __import__("asyncio").run(provider.chat("stub-model", [], False))
    assert message["provider"] == "discord"
    assert message["model"] == "stub-model"
    assert "content" in message["message"]


def test_discord_adapter_requires_webhook():
    provider = DiscordProvider()
    with pytest.raises(RuntimeError, match="Missing webhook config"):
        __import__("asyncio").run(provider.chat("model", [], False))


def test_discord_webhook_returns_route_id():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    message = __import__("asyncio").run(provider.chat("model", [], False))
    assert message["webhook"] == "wh-1"
    assert message["message"]["content"].endswith("routed")
