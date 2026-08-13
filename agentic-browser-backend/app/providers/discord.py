from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class DiscordWebhook(BaseModel):
    id: str
    token: str
    default_channel: str = ""


class DiscordProvider:
    key = "discord"
    description = "Discord adapter with webhook routing"

    def __init__(self, webhook: DiscordWebhook | None = None):
        self.webhook = webhook

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.webhook:
            raise RuntimeError("Missing webhook config")
        text = messages[-1].get("content", "") if messages else ""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=15.0, write=15.0, pool=5.0)) as client:
                await client.post(
                    f"https://discord.com/api/webhooks/{self.webhook.id}/{self.webhook.token}",
                    json={"content": text, "allowed_mentions": {"parse": []}},
                )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Discord webhook delivery failed: {exc}") from exc
        return {
            "content": f"Discord webhook {self.webhook.id} routed: {text}",
            "provider": self.key,
            "model": model,
            "webhook": self.webhook.id,
        }


def create_app() -> FastAPI:
    app = FastAPI(title="Discord Adapter")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhook/chat")
    async def webhook_chat(webhook: DiscordWebhook) -> Dict[str, Any]:
        provider = DiscordProvider(webhook)
        return await provider.chat("webhook-model", [], False)

    return app
