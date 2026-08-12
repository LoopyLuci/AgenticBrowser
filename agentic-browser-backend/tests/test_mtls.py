import os

from main import MTLSMiddleware


class FakeApp:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, scope, receive, send):
        self.calls.append((scope, receive, send))
        await send({
            "type": "http.response.start",
            "status": self.response["status"],
            "headers": [(b"content-type", b"application/json")],
        })
        await send({
            "type": "http.response.body",
            "body": self.response.get("body", b""),
        })


class FakeSend:
    def __init__(self):
        self.events = []

    async def __call__(self, event):
        self.events.append(event)


def test_mtls_middleware_blocks_without_client_cert(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    fake_app = FakeApp({"status": 200})
    middleware = MTLSMiddleware(fake_app)
    send = FakeSend()
    scope = {
        "type": "http",
        "headers": [(b"x-client-cert-present", b"false")],
    }
    import asyncio

    asyncio.run(middleware(scope, lambda: None, send))
    response_events = [event for event in send.events if event["type"] == "http.response.start"]
    assert response_events[0]["status"] == 403


def test_mtls_middleware_allows_with_client_cert(monkeypatch):
    monkeypatch.setenv("MTLS_ENABLED", "true")
    fake_app = FakeApp({"status": 200, "body": b'{"status":"ok"}'})
    middleware = MTLSMiddleware(fake_app)
    send = FakeSend()
    scope = {
        "type": "http",
        "headers": [(b"x-client-cert-present", b"true")],
    }
    import asyncio

    asyncio.run(middleware(scope, lambda: None, send))
    response_events = [event for event in send.events if event["type"] == "http.response.start"]
    assert response_events[0]["status"] == 200
    assert len(fake_app.calls) == 1
