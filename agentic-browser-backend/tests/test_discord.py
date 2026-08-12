import asyncio

from app.providers.discord import DiscordProvider


def test_discord_adapter_loads():
    provider = DiscordProvider()
    assert provider.key == "discord"


def test_discord_adapter_stub_response():
    provider = DiscordProvider()
    message = asyncio.run(provider.chat("stub-model", [], False))
    assert message["provider"] == "discord"
    assert message["model"] == "stub-model"
    assert "content" in message["message"]
