from fastapi.testclient import TestClient
import time

from main import app


def test_rate_limit_returns_429_under_load():
    client = TestClient(app)
    sent = 0
    failed = False
    start = time.time()
    while time.time() - start < 2:
        r = client.get("/health")
        sent += 1
        if r.status_code == 429:
            failed = True
            break
    assert failed is True
    assert sent > 0
