from fastapi.testclient import TestClient

from main import app
from app.observability.metrics import _rate_limit_store


def test_rate_limit_concurrency_rejects_121st_request():
    _rate_limit_store.clear()
    client = TestClient(app)
    for _ in range(120):
        r = client.get("/health")
        assert r.status_code == 200

    r = client.get("/health")
    assert r.status_code == 429
