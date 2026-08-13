import pytest
from fastapi.testclient import TestClient

from main import app
from app.providers.discord import DiscordProvider, DiscordWebhook
from app.providers.slack import SlackProvider
from app.providers.signal import SignalProvider
from app.providers.chat import register_test_provider, unregister_test_provider
from app.observability.metrics import _rate_limit_store


@pytest.fixture(autouse=True)
def clear_rate_limit():
    _rate_limit_store.clear()
    yield


def test_discord_webhook_endpoint_accepts_payload():
    webhook = DiscordWebhook(id="test-webhook", token="token")
    register_test_provider("discord", lambda *args, **kwargs: DiscordProvider(webhook))
    try:
        client = TestClient(app)
        response = client.post(
            "/v1/chat",
            json={
                "session_id": "discord-test",
                "messages": [{"role": "user", "content": "hi"}],
                "provider": "discord",
                "model": "webhook-model",
                "stream": False,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["provider"] == "discord"
        assert "webhook" in body["message"]
    finally:
        unregister_test_provider("discord")


def test_slack_chat_endpoint_bridges_message():
    register_test_provider("slack", lambda *args, **kwargs: SlackProvider(webhook_url="http://example.com"))
    try:
        client = TestClient(app)
        response = client.post(
            "/v1/chat",
            json={
                "session_id": "slack-test",
                "messages": [{"role": "user", "content": "hello"}],
                "provider": "slack",
                "model": "slack-model",
                "stream": False,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["provider"] == "slack"
        assert "Slack bridge" in body["message"]["content"]
    finally:
        unregister_test_provider("slack")


def test_signal_chat_endpoint_bridges_message():
    register_test_provider("signal", lambda *args, **kwargs: SignalProvider(api_url="http://localhost:8080"))
    try:
        client = TestClient(app)
        response = client.post(
            "/v1/chat",
            json={
                "session_id": "signal-test",
                "messages": [{"role": "user", "content": "hello"}],
                "provider": "signal",
                "model": "signal-model",
                "stream": False,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["provider"] == "signal"
        assert "Signal bridge" in body["message"]["content"]
    finally:
        unregister_test_provider("signal")
