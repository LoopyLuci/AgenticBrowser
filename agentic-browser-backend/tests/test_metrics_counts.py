from fastapi.testclient import TestClient

from app.observability.metrics import REQUEST_COUNTS
from main import app


def test_metrics_endpoint_reports_route_counts():
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
