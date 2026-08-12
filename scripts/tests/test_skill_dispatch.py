import json
import os
import subprocess
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_SCRIPT = REPO_ROOT / "scripts" / "hermes_control.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from hermes_control import call  # noqa: E402


class MockSkillHandler(BaseHTTPRequestHandler):
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
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "ok": True,
                        "skill": "browser_search",
                        "query": payload.get("message") or payload.get("messages", [{}])[-1].get("content", ""),
                        "result": {"title": "mocked result", "url": "https://example.com"},
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
    port = 8771
    server = HTTPServer(("127.0.0.1", port), MockSkillHandler)
    thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)
    yield server
    server.shutdown()


def test_skill_dispatch_live(monkeypatch, mock_control_server):
    monkeypatch.setenv("AGENTIC_CONTROL_BASE", "http://127.0.0.1:8771")
    monkeypatch.setenv("AGENTIC_CONTROL_SECRET", "test-secret")
    result = call(
        "http://127.0.0.1:8771",
        "/v1/control/chat",
        {"sessionId": "cli", "provider": "ollama", "model": "llama3", "messages": [{"role": "user", "content": "search hermetic seals"}]},
    )
    assert result.get("ok") is True
    assert result.get("skill") == "browser_search"
    assert result.get("result", {}).get("url") == "https://example.com"
