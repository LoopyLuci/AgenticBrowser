from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class SlackMessage(BaseModel):
    channel: str
    text: str


class SlackProvider:
    key = "slack"
    description = "Slack adapter with incoming webhook and basic chat bridge"

    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.webhook_url:
            raise RuntimeError("Missing Slack webhook URL")
        text = messages[-1].get("content", "") if messages else ""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=15.0, write=15.0, pool=5.0)) as client:
                await client.post(
                    self.webhook_url,
                    json={"channel": self.webhook_url, "text": text},
                    headers={"Content-Type": "application/json"},
                )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Slack webhook delivery failed: {exc}") from exc
        return {
            "content": f"Slack bridge: {text}",
            "provider": self.key,
            "model": model,
            "webhook": self.webhook_url,
        }


def create_app() -> FastAPI:
    app = FastAPI(title="Slack Adapter")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhook/chat")
    async def webhook_chat(message: SlackMessage) -> Dict[str, Any]:
        provider = SlackProvider(webhook_url="slack-webhook")
        return await provider.chat("webhook-model", [{"role": "user", "content": message.text}], False)

    return app
