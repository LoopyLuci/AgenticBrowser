import pytest
from unittest.mock import AsyncMock, patch, Mock

from app.providers.discord import DiscordProvider, DiscordWebhook
from app.providers.slack import SlackProvider
from app.providers.signal import SignalProvider
from app.providers.chat import register_test_provider, unregister_test_provider
from app.observability.metrics import _rate_limit_store


@pytest.fixture(autouse=True)
def clear_rate_limit():
    _rate_limit_store.clear()
    yield


def test_discord_adapter_sends_webhook():
    webhook = DiscordWebhook(id="wh-1", token="token")
    provider = DiscordProvider(webhook)
    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    with patch("app.providers.discord.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.post = AsyncMock(return_value=response)
        client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
        client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        result = __import__("asyncio").run(provider.chat("model", [{"role": "user", "content": "hi"}], False))
    assert result["provider"] == "discord"
    assert result["webhook"] == "wh-1"
    assert "Discord webhook wh-1 routed" in result["content"]


def test_slack_adapter_sends_webhook():
    provider = SlackProvider(webhook_url="http://example.com")
    response = Mock()
    response.status_code = 200
    response.raise_for_status = Mock()
    with patch("app.providers.slack.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.post = AsyncMock(return_value=response)
        client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
        client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        result = __import__("asyncio").run(provider.chat("model", [{"role": "user", "content": "hello"}], False))
    assert result["provider"] == "slack"
    assert "Slack bridge" in result["content"]


def test_signal_adapter_sends_webhook():
    provider = SignalProvider(api_url="http://localhost:8080")
    with patch("httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
        client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        result = __import__("asyncio").run(provider.chat("model", [{"role": "user", "content": "hello"}], False))
    assert result["provider"] == "signal"
    assert "Signal bridge" in result["content"]
