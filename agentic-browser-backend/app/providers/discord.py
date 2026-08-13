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
    MAX_RETRIES = 3
    BACKOFF_BASE = 0.5

    def __init__(self, webhook: DiscordWebhook | None = None):
        self.webhook = webhook

    async def _post_with_retry(self, client: httpx.AsyncClient, url: str, payload: dict) -> None:
        last_error: Exception | None = None
        response: httpx.Response | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await client.post(url, json=payload)
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"Retryable status {response.status_code}", request=response.request, response=response
                    )
                response.raise_for_status()
                return
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt == self.MAX_RETRIES or (response is not None and response.status_code < 500):
                    break
                sleep = self.BACKOFF_BASE * (2 ** (attempt - 1))
                import asyncio
                await asyncio.sleep(sleep)
        raise RuntimeError(f"Discord webhook delivery failed: {last_error}") from last_error

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.webhook:
            raise RuntimeError("Missing webhook config")
        text = messages[-1].get("content", "") if messages else ""
        payload = {"content": text, "allowed_mentions": {"parse": []}}
        url = f"https://discord.com/api/webhooks/{self.webhook.id}/{self.webhook.token}"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=15.0, write=15.0, pool=5.0)) as client:
                await self._post_with_retry(client, url, payload)
        except RuntimeError:
            raise
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
