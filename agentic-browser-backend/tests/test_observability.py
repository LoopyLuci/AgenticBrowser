from fastapi.testclient import TestClient
import json
import logging
from io import StringIO

from main import app


def test_metrics_summary_records_request():
    client = TestClient(app)
    first = client.get("/metrics")
    assert first.status_code == 200
    body = first.json()
    assert "requests" in body

    client.get("/health")

    second = client.get("/metrics")
    assert second.status_code == 200
    body = second.json()
    assert "/health" in body["requests"]
    assert body["requests"]["/health"]["count"] >= 1
    assert body["requests"]["/health"]["avg_latency_s"] >= 0


def test_metrics_summary_non_empty_after_multiple_routes():
    client = TestClient(app)
    client.get("/health")
    client.get("/providers")
    client.get("/v1/tools")

    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "requests" in body
    assert "/health" in body["requests"]
    assert "/providers" in body["requests"]
    assert "/v1/tools" in body["requests"]


def test_audit_log_emits_during_tool_execution(caplog):
    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="agentic.audit"):
        r = client.post("/v1/tools", json={"name": "search", "arguments": {"query": "audit-test"}})
    assert r.status_code == 200
    audit_messages = [m for m in caplog.messages if m.startswith('{"event"')]
    assert any('"event"' in m and '"tool_execute"' in m for m in audit_messages), audit_messages
