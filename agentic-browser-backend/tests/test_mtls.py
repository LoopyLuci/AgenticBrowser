import os
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from main import MTLSMiddleware


class FakeApp:
    def __init__(self):
        self.calls = []

    async def __call__(self, scope, receive, send):
        self.calls.append(scope)
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": b'{"status":"ok"}'})


class FakeSend:
    def __init__(self):
        self.events = []

    async def __call__(self, event):
        self.events.append(event)


def _build_middleware(expected_regex: str | None = None):
    regex = expected_regex if expected_regex is not None else os.getenv("MTLS_CLIENT_SUBJECT_REGEX")
    return MTLSMiddleware(FakeApp(), expected_subject_regex=regex)


def test_mtls_middleware_blocks_without_client_cert(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    middleware = _build_middleware()
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"false")]}
    send = FakeSend()
    import asyncio

    asyncio.run(middleware(scope, lambda: None, send))
    response_events = [event for event in send.events if event["type"] == "http.response.start"]
    assert response_events[0]["status"] == 403


def test_mtls_middleware_allows_with_client_cert(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    middleware = _build_middleware()
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"true")]}
    send = FakeSend()
    import asyncio

    asyncio.run(middleware(scope, lambda: None, send))
    response_events = [event for event in send.events if event["type"] == "http.response.start"]
    assert response_events[0]["status"] == 200
    assert len(FakeApp().calls) == 0


def _load_cert():
    data = (Path(__file__).resolve().parents[2] / "certs" / "cert.pem").read_bytes()
    return x509.load_pem_x509_certificate(data, default_backend())


def test_client_certificate_subject_cn_is_localhost():
    cert = _load_cert()
    subject = cert.subject
    cn = subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
    assert cn, "Missing CN in certificate subject"
    assert cn[0].value == "localhost"


def test_mtls_middleware_validates_client_cert_subject(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    monkeypatch.setenv("MTLS_CLIENT_SUBJECT_REGEX", "")
    fake_pem = b"-----BEGIN CERTIFICATE-----\nSubject: CN = localhost\n-----END CERTIFICATE-----\n"
    middleware = MTLSMiddleware(FakeApp(), expected_subject_regex=r"CN\s*=\s*localhost")
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"true"), (b"x-client-cert", fake_pem)]}
    send = FakeSend()
    import asyncio

    asyncio.run(middleware(scope, lambda: None, send))
    response_events = [event for event in send.events if event["type"] == "http.response.start"]
    assert response_events[0]["status"] == 200


def test_mtls_middleware_rejects_wrong_subject_regex(monkeypatch):
    cert = _load_cert()
    pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    encoded = pem.encode("utf-8")
    monkeypatch.setenv("MTLS_ENABLED", "true")
    monkeypatch.setenv("MTLS_CLIENT_SUBJECT_REGEX", "")
    middleware = MTLSMiddleware(FakeApp(), expected_subject_regex=r"CN\s*=\s*bad")
    scope = {"type": "http", "headers": [(b"x-client-cert-present", b"true"), (b"x-client-cert", encoded)]}
    send = FakeSend()
    import asyncio

    asyncio.run(middleware(scope, lambda: None, send))
    response_events = [event for event in send.events if event["type"] == "http.response.start"]
    assert response_events[0]["status"] == 403
