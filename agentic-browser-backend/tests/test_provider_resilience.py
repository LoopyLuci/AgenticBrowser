import pytest
from unittest.mock import patch

import httpx
from app.providers.discord import DiscordProvider, DiscordWebhook
from app.providers.slack import SlackProvider
from app.providers.signal import SignalProvider


class FakeDiscordClient:
    def __init__(self, *args, **kwargs):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        raise httpx.RemoteProtocolError("server error")


class FakeDiscordRecoveringClient:
    def __init__(self, *args, **kwargs):
        self.calls = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        self.calls += 1
        if self.calls < 3:
            class _Resp:
                status_code = 500
                def raise_for_status(self):
                    pass
                request = None
            return _Resp()
        class _Resp:
            status_code = 200
            def raise_for_status(self):
                pass
            request = None
        return _Resp()


@pytest.mark.asyncio
async def test_discord_retries_then_succeeds():
    provider = DiscordProvider(DiscordWebhook(id="123", token="abc"))
    client = FakeDiscordRecoveringClient()

    with patch("app.providers.discord.httpx.AsyncClient", new=lambda **kwargs: client):
        response = await provider.chat("model", [{"role": "user", "content": "hi"}])
    assert "Discord webhook 123 routed" in response["content"]
    assert client.calls == 3


@pytest.mark.asyncio
async def test_discord_surfaces_delivery_failure():
    provider = DiscordProvider(DiscordWebhook(id="123", token="abc"))

    with patch("app.providers.discord.httpx.AsyncClient", new=FakeDiscordClient):
        with pytest.raises(RuntimeError, match="Discord webhook delivery failed"):
            await provider.chat("model", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_slack_handles_timeout():
    provider = SlackProvider(webhook_url="http://example.com")

    class FakeSlackClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, **kwargs):
            raise httpx.RemoteProtocolError("server error")

    with patch("app.providers.slack.httpx.AsyncClient", new=FakeSlackClient):
        with pytest.raises(RuntimeError, match="Slack webhook delivery failed"):
            await provider.chat("model", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_signal_returns_bridge_payload():
    provider = SignalProvider()
    response = await provider.chat("model", [{"role": "user", "content": "hello"}])
    assert response["provider"] == "signal"
    assert response["content"] == "Signal bridge: hello"
