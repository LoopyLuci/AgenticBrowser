from fastapi.testclient import TestClient

from main import app
from app.observability.metrics import REQUEST_COUNTS, _rate_limit_store


def test_metrics_endpoint_reports_route_counts():
    _rate_limit_store.clear()
    client = TestClient(app)
    client.get("/health")
    client.get("/providers")
    client.get("/v1/tools")

    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()["requests"]
    assert "/health" in body
    assert "/providers" in body
    assert "/v1/tools" in body
    assert body["/health"]["count"] >= 1
    assert body["/providers"]["count"] >= 1
    assert body["/v1/tools"]["count"] >= 1
