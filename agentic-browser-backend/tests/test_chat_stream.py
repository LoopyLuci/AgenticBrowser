from fastapi.testclient import TestClient

from main import app


def test_chat_stream_returns_events():
    client = TestClient(app)
    response = client.post(
        "/v1/chat/stream",
        json={"session_id": "s1", "messages": [], "provider": "fake", "model": "m", "stream": True},
        headers={"accept": "text/event-stream"},
    )
    assert response.status_code == 200
    text = response.text
    assert "token" in text
    assert "done" in text
