from fastapi.testclient import TestClient

from main import app


def test_rate_limit_store_does_not_crash_on_first_request():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200


def test_metrics_reflects_rate_limited_requests():
    client = TestClient(app)
    for _ in range(5):
        client.get("/health")

    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "/health" in body["requests"]
    assert body["requests"]["/health"]["count"] >= 5
