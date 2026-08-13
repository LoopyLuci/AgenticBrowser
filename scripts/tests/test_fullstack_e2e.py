import socket

import pytest
import requests


BACKEND = "http://localhost:8123"
CONTROL = "http://localhost:8766"


def _is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


@pytest.mark.skipif(not _is_open("localhost", 8123), reason="backend not running")
@pytest.mark.skipif(not _is_open("localhost", 8766), reason="control plane not running")
def test_backend_control_plane_round_trip():
    health = requests.get(f"{BACKEND}/health", timeout=5)
    assert health.status_code == 200

    control_health = requests.get(f"{CONTROL}/health", timeout=5)
    assert control_health.status_code == 200

    chat = requests.post(
        f"{BACKEND}/v1/chat",
        json={
            "session_id": "e2e-roundtrip",
            "messages": [{"role": "user", "content": "ping"}],
            "provider": "fake",
            "model": "fake-model",
            "stream": False,
        },
        timeout=10,
    )
    assert chat.status_code == 200
    body = chat.json()
    assert "message" in body or "data" in body
