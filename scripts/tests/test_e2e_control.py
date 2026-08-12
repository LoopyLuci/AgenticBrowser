import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "agentic-browser-backend"
CONTROL_ROOT = REPO_ROOT / "agentic-browser-control"


class FakeBackendHandler(BaseHTTPRequestHandler):
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
        if self.path == "/v1/chat":
            payload = json.loads(body.decode("utf-8") or "{}")
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "provider": payload.get("provider", "ollama"),
                        "model": payload.get("model", "llama3"),
                        "message": {"role": "assistant", "content": "backend result"},
                        "session_id": payload.get("session_id", "s1"),
                    }
                ).encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture()
def fake_backend_server():
    port = 8128
    server = HTTPServer(("127.0.0.1", port), FakeBackendHandler)
    thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)
    yield port
    server.shutdown()


def test_e2e_control_plane_to_backend(monkeypatch, fake_backend_server):
    backend_port = fake_backend_server
    control_port = 18876
    control_proc = subprocess.Popen(
        ["node", str(CONTROL_ROOT / "dist" / "server.js")],
        env={
            **os.environ,
            "AGENTIC_BACKEND": f"http://127.0.0.1:{backend_port}",
            "PORT": str(control_port),
            "AGENTIC_CONTROL_SECRET": "test-secret",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(CONTROL_ROOT),
    )
    try:
        for _ in range(20):
            time.sleep(0.25)
            try:
                url = f"http://127.0.0.1:{control_port}/health"
                with __import__("urllib.request").request.urlopen(url, timeout=2) as resp:
                    assert resp.status == 200
                    break
            except Exception:
                continue
        else:
            raise AssertionError("Control server did not become ready")

        payload = json.dumps(
            {
                "sessionId": "s1",
                "provider": "ollama",
                "model": "llama3",
                "messages": [{"role": "user", "content": "ping"}],
            }
        ).encode()
        req = __import__("urllib.request").request.Request(
            f"http://127.0.0.1:{control_port}/v1/control/chat",
            data=payload,
            headers={
                "content-type": "application/json",
                "x-signature": __import__("hmac").new(
                    b"test-secret", payload, __import__("hashlib").sha256
                ).hexdigest(),
            },
        )
        with __import__("urllib.request").request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            assert body.get("ok") is True
            assert body.get("data", {}).get("session_id") == "s1"
    finally:
        control_proc.terminate()
        try:
            control_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            control_proc.kill()
