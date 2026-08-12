import os
import subprocess
import sys
import time
from pathlib import Path

import http.client
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CERTS_DIR = REPO_ROOT / "certs"
KEY = str(CERTS_DIR / "key.pem")
CERT = str(CERTS_DIR / "cert.pem")
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8149


def _start_backend_ssl():
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            BACKEND_HOST,
            "--port",
            str(BACKEND_PORT),
            "--ssl-keyfile",
            KEY,
            "--ssl-certfile",
            CERT,
        ],
        cwd=str(REPO_ROOT / "agentic-browser-backend"),
        env={**os.environ, "MTLS_ENABLED": "false"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    for _ in range(60):
        try:
            with __import__("socket").create_connection((BACKEND_HOST, BACKEND_PORT), timeout=1):
                break
        except Exception:
            time.sleep(0.25)
    else:
        proc.kill()
        proc.wait()
        pytest.fail("Backend HTTPS server did not become ready")
    return proc


def test_backend_serves_https_with_self_signed_cert():
    if not Path(KEY).exists() or not Path(CERT).exists():
        pytest.skip("Missing generated SSL certs")

    proc = _start_backend_ssl()
    try:
        ctx = __import__("ssl").create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = __import__("ssl").CERT_NONE

        conn = http.client.HTTPSConnection(
            BACKEND_HOST, BACKEND_PORT, context=ctx, timeout=5
        )
        conn.request("GET", "/health")
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        text = data.decode("utf-8", errors="replace")
        assert resp.status == 200
        assert '"status":"ok"' in text or '"status": "ok"' in text
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
