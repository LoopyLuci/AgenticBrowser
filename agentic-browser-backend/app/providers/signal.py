from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel


class SignalMessage(BaseModel):
    recipient: str
    text: str


class SignalProvider:
    key = "signal"
    description = "Signal adapter with basic message bridge"

    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url.rstrip("/")

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        text = messages[-1].get("content", "") if messages else ""
        return {
            "provider": self.key,
            "model": model,
            "message": {"content": f"Signal bridge: {text}"},
            "finish_reason": "ok",
            "api_url": self.api_url,
        }


def create_app() -> FastAPI:
    app = FastAPI(title="Signal Adapter")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/webhook/chat")
    async def webhook_chat(message: SignalMessage):
        provider = SignalProvider()
        return await provider.chat("webhook-model", [{"role": "user", "content": message.text}], False)

    return app
