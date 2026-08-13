import pytest
from fastapi.testclient import TestClient

from main import app


def test_telegram_webhook_route_processes_update():
    client = TestClient(app)
    payload = {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "text": "hello",
            "from": {"username": "user1"},
        },
    }
    r = client.post("/v1/telegram/webhook/missing-token", json=payload)
    assert r.status_code == 404


def test_telegram_webhook_route_rejects_wrong_token():
    client = TestClient(app)
    payload = {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "text": "hello",
            "from": {"username": "user1"},
        },
    }
    r = client.post("/v1/telegram/webhook/wrong-token", json=payload)
    assert r.status_code == 404
