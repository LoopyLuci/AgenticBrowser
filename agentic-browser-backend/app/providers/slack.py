from typing import Any, Dict, List

from fastapi import FastAPI
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
        return {
            "content": f"Slack bridge: {text}",
            "provider": self.key,
            "model": model,
            "webhook": self.webhook_url,
        }


def create_app() -> FastAPI:
    app = FastAPI(title="Slack Adapter")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/webhook/chat")
    async def webhook_chat(message: SlackMessage):
        provider = SlackProvider(webhook_url="slack-webhook")
        return await provider.chat("webhook-model", [{"role": "user", "content": message.text}], False)

    return app
