import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_SCRIPT = REPO_ROOT / "scripts" / "hermes_control.py"

# Import the wrapper logic directly to avoid pytest subprocess behavior differences.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from hermes_control import call  # noqa: E402


class MockControlHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        body = self.rfile.read(length)
        if self.path == "/v1/control/chat":
            payload = json.loads(body.decode("utf-8") or "{}")
            signature = self.headers.get("x-signature", "")
            if not signature:
                self.send_response(401)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Missing signature"}).encode())
                return
            expected = self.server.expected_signature
            if expected and signature != expected:
                self.send_response(401)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Invalid signature"}).encode())
                return
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "ok": True,
                        "sessionId": payload.get("sessionId"),
                        "provider": payload.get("provider"),
                        "model": payload.get("model"),
                        "data": {"provider": "mock", "model": "mock", "message": {"content": "mocked"}},
                    }
                ).encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture()
def mock_control_server():
    port = 8769
    server = HTTPServer(("127.0.0.1", port), MockControlHandler)
    server.expected_signature = None
    thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)
    yield server
    server.shutdown()


def test_health_live(monkeypatch, mock_control_server):
    monkeypatch.setenv("AGENTIC_CONTROL_BASE", "http://127.0.0.1:8769")
    result = call("http://127.0.0.1:8769", "/health")
    assert result.get("status") == "ok"


def test_chat_with_signature(monkeypatch, mock_control_server):
    monkeypatch.setenv("AGENTIC_CONTROL_BASE", "http://127.0.0.1:8769")
    monkeypatch.setenv("AGENTIC_CONTROL_SECRET", "test-secret")

    import hashlib
    import hmac
    payload = {
        "sessionId": "cli",
        "provider": "ollama",
        "model": "llama3",
        "messages": [{"role": "user", "content": "ping"}],
    }
    body = json.dumps(payload).encode()
    expected = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
    mock_control_server.expected_signature = expected

    result = call("http://127.0.0.1:8769", "/v1/control/chat", payload)
    assert result.get("ok") is True
    assert result.get("data", {}).get("message", {}).get("content") == "mocked"


def test_chat_without_signature_rejected(monkeypatch, mock_control_server):
    monkeypatch.setenv("AGENTIC_CONTROL_BASE", "http://127.0.0.1:8769")
    monkeypatch.setenv("AGENTIC_CONTROL_SECRET", "test-secret")
    mock_control_server.expected_signature = "bad-signature"

    result = call("http://127.0.0.1:8769", "/v1/control/chat", {"messages": []})
    assert result.get("ok") is False
    assert "Invalid signature" in result.get("error", "")
