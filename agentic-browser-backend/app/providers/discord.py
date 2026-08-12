from typing import Any, Dict, List

from fastapi import FastAPI
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
        return {
            "provider": self.key,
            "model": model,
            "message": {
                "content": f"Discord webhook {self.webhook.id} routed"
            },
            "finish_reason": "ok",
            "webhook": self.webhook.id,
        }


def create_app() -> FastAPI:
    app = FastAPI(title="Discord Adapter")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/webhook/chat")
    async def webhook_chat(webhook: DiscordWebhook):
        provider = DiscordProvider(webhook)
        return await provider.chat("webhook-model", [], False)

    return app
