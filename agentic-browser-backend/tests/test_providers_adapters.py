import asyncio

import pytest
from unittest.mock import patch

from app.providers.chat import (
    OpenRouterProvider,
    OpenAIProvider,
    OllamaProvider,
    register_test_provider,
    unregister_test_provider,
)
from app.providers.telegram_bot import TelegramBot, TelegramUpdate, TelegramBotError
from app.providers.discord import DiscordProvider, DiscordWebhook
from app.providers.slack import SlackProvider
from app.providers.signal import SignalProvider
from app.settings.store import SettingsStore


def test_openrouter_requires_api_key():
    with pytest.raises(ValueError, match="OPENROUTER_KEY missing"):
        asyncio.run(OpenRouterProvider("").chat("model", []))


def test_openai_requires_api_key():
    with pytest.raises(ValueError, match="OPENAI_KEY missing"):
        asyncio.run(OpenAIProvider("").chat("model", []))


def test_ollama_defaults_base_url():
    provider = OllamaProvider()
    assert provider.base == "http://localhost:11434"


def test_discord_adapter_loads():
    provider = DiscordProvider(DiscordWebhook(id="1", token="t"))
    assert provider.key == "discord"


def test_discord_adapter_stub_response():
    provider = DiscordProvider(DiscordWebhook(id="1", token="t"))

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

    with patch("app.providers.discord.httpx.AsyncClient", new=lambda **kwargs: FakeClient()):
        coro = provider.chat("model", [])
        result = asyncio.run(coro)
    assert "Discord webhook 1 routed" in result["content"]


def test_discord_adapter_requires_webhook():
    provider = DiscordProvider()
    with pytest.raises(RuntimeError, match="Missing webhook config"):
        asyncio.run(provider.chat("model", []))


def test_slack_adapter_stub_response():
    provider = SlackProvider(webhook_url="http://example.com")
    result = asyncio.run(provider.chat("model", [{"role": "user", "content": "hi"}]))
    assert result["provider"] == "slack"
    assert "Slack bridge" in result["content"]


def test_signal_adapter_stub_response():
    provider = SignalProvider(api_url="http://localhost:8080")
    result = asyncio.run(provider.chat("model", [{"role": "user", "content": "hi"}]))
    assert result["provider"] == "signal"
    assert "Signal bridge" in result["content"]
