import os
import socket
import ssl
from pathlib import Path

import pytest
import uvicorn

from main import app as backend_app
from app.observability.metrics import _rate_limit_store

MTLS_PORT = 18432


@pytest.fixture(scope="module")
def live_mtls_server():
    os.environ["MTLS_ENABLED"] = "true"
    os.environ["MTLS_CLIENT_SUBJECT_REGEX"] = r"CN\s*=\s*localhost"
    cert_path = Path(__file__).resolve().parents[2] / "certs" / "cert.pem"
    key_path = Path(__file__).resolve().parents[2] / "certs" / "key.pem"

    if not cert_path.exists() or not key_path.exists():
        pytest.skip("mTLS certs missing")

    config = uvicorn.Config(
        backend_app,
        host="127.0.0.1",
        port=MTLS_PORT,
        ssl_certfile=str(cert_path),
        ssl_keyfile=str(key_path),
        log_level="error",
    )
    server = uvicorn.Server(config)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.bind(("127.0.0.1", MTLS_PORT))
        except OSError:
            pytest.skip(f"Port {MTLS_PORT} busy")

    import threading

    thread = threading.Thread(target=server.run)
    thread.start()
    try:
        import time

        for _ in range(50):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                try:
                    sock.connect(("127.0.0.1", MTLS_PORT))
                    break
                except OSError:
                    time.sleep(0.1)
        yield server
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        os.environ.pop("MTLS_ENABLED", None)
        os.environ.pop("MTLS_CLIENT_SUBJECT_REGEX", None)


def test_mtls_server_rejects_without_client_cert(live_mtls_server):
    import http.client

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    conn = http.client.HTTPSConnection("127.0.0.1", MTLS_PORT, timeout=5, context=context)
    try:
        conn.request("GET", "/health", headers={"x-client-cert-present": "false"})
        response = conn.getresponse()
        assert response.status == 403
    finally:
        conn.close()


def test_mtls_server_allows_with_client_cert(live_mtls_server):
    import http.client
    import json

    cert_path = Path(__file__).resolve().parents[2] / "certs" / "cert.pem"
    key_path = Path(__file__).resolve().parents[2] / "certs" / "key.pem"

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(str(cert_path), str(key_path))
    context.load_verify_locations(str(cert_path))
    context.check_hostname = False

    conn = http.client.HTTPSConnection("127.0.0.1", MTLS_PORT, timeout=5, context=context)
    try:
        conn.request("GET", "/health", headers={"x-client-cert-present": "true", "x-client-cert": "CN=localhost"})
        response = conn.getresponse()
        body = response.read().decode("utf-8", errors="replace")
        print("RESPONSE BODY:", body)
        assert response.status == 200
    finally:
        conn.close()
