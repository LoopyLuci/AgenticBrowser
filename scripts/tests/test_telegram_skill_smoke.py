import os

import pytest
import requests


@pytest.mark.skipif(
    not os.getenv("TELEGRAM_BOT_TOKEN"),
    reason="TELEGRAM_BOT_TOKEN not set; skip live Hermes skill test",
)
def test_telegram_bot_skill_live_smoke():
    backend = os.getenv("AGENTIC_BACKEND", "http://localhost:8123")
    r = requests.get(f"{backend}/v1/settings", timeout=5)
    assert r.status_code == 200
    body = r.json()
    assert body.get("telegram", {}).get("token_set") is True
