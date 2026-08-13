import os
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from main import app, MTLSMiddleware
from app.observability.metrics import _rate_limit_store


class FakeApp:
    def __init__(self):
        self.calls = []

    async def __call__(self, scope, receive, send):
        self.calls.append(scope.get("type"))
        from starlette.responses import PlainTextResponse

        response = PlainTextResponse("ok")
        await response(scope, receive, send)


def _load_cert():
    from pathlib import Path

    cert_path = Path(__file__).resolve().parents[2] / "certs" / "cert.pem"
    pem = cert_path.read_bytes()
    return x509.load_pem_x509_certificate(pem, default_backend())


def test_mtls_middleware_blocks_without_client_cert(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    app_test = MTLSMiddleware(FakeApp())
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"false")]}

    received = []
    async def receive(): return {}
    async def send(message): received.append(message)

    __import__("asyncio").run(app_test(scope, receive, send))
    start = next(msg for msg in received if msg.get("type") == "http.response.start")
    assert start["status"] == 403


def test_mtls_middleware_allows_with_client_cert(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    app_test = MTLSMiddleware(FakeApp())
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"true"), (b"x-client-cert", b"CN=AgenticBrowser Test Client")]}

    received = []
    async def receive(): return {}
    async def send(message): received.append(message)

    __import__("asyncio").run(app_test(scope, receive, send))
    start = next(msg for msg in received if msg.get("type") == "http.response.start")
    assert start["status"] == 200


def test_client_certificate_subject_cn_is_localhost():
    cert = _load_cert()
    subject = cert.subject
    cn_attrs = [attr.value for attr in subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)]
    assert cn_attrs == ["localhost"]


def test_mtls_middleware_validates_client_cert_subject(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    monkeypatch.setenv("MTLS_CLIENT_SUBJECT_REGEX", "CN=AgenticBrowser Test Client")
    app_test = MTLSMiddleware(FakeApp())
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"true"), (b"x-client-cert", b"CN=AgenticBrowser Test Client")]}

    received = []
    async def receive(): return {}
    async def send(message): received.append(message)

    __import__("asyncio").run(app_test(scope, receive, send))
    start = next(msg for msg in received if msg.get("type") == "http.response.start")
    assert start["status"] == 200


def test_mtls_middleware_rejects_wrong_subject_regex():
    app_test = MTLSMiddleware(FakeApp(), expected_subject_regex="CN=other")
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"true"), (b"x-client-cert", b"CN=AgenticBrowser Test Client")]}

    received = []
    async def receive(): return {}
    async def send(message): received.append(message)

    __import__("asyncio").run(app_test(scope, receive, send))
    start = next(msg for msg in received if msg.get("type") == "http.response.start")
    assert start["status"] == 403
