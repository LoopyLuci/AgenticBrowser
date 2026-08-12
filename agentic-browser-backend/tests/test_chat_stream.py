from typing import Any

import pytest

from app.providers.chat import PROVIDERS, register_test_provider, unregister_test_provider


class FakeProvider:
    key = "fake"

    async def chat(self, model: str, messages: list[dict[str, Any]], stream: bool = False) -> dict[str, Any]:
        if stream:

            async def _generator():
                yield {"message": {"content": "hello "}}
                yield {"message": {"content": "world"}}

            return _generator()
        return {"provider": self.key, "model": model, "message": {"content": "fake-response"}}


@pytest.fixture()
def fake_provider():
    register_test_provider("fake", lambda *args, **kwargs: FakeProvider())
    yield
    unregister_test_provider("fake")


def test_chat_stream_returns_events(client, fake_provider):
    response = client.post(
        "/v1/chat/stream",
        json={"session_id": "s1", "messages": [], "provider": "fake", "model": "m", "stream": True},
        headers={"accept": "text/event-stream"},
    )
    assert response.status_code == 200
    text = response.text
    assert "token" in text
    assert "done" in text


def test_fake_provider_not_registered_by_default():
    assert "fake" not in PROVIDERS
