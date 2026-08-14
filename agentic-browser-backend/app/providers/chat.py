from typing import Any, Dict, List

import httpx

from app.providers.discord import DiscordProvider, DiscordWebhook
from app.providers.slack import SlackProvider
from app.providers.signal import SignalProvider
from app.providers.telegram_bot import TelegramBot


class BaseProvider:
    key: str = ""

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        raise NotImplementedError


async def _post_with_retry(
    client: httpx.AsyncClient,
    url: str,
    payload: dict,
    *,
    max_retries: int = 3,
    backoff_base: float = 0.5,
    headers: dict | None = None,
) -> httpx.Response:
    last_error: Exception | None = None
    response: httpx.Response | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"Retryable status {response.status_code}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            last_error = exc
            if attempt == max_retries or (response is not None and response.status_code < 500):
                break
            sleep = backoff_base * (2 ** (attempt - 1))
            import asyncio

            await asyncio.sleep(sleep)
    raise RuntimeError(f"HTTP request failed: {last_error}") from last_error


class OllamaProvider(BaseProvider):
    key = "ollama"

    def __init__(self, base: str = "http://localhost:11434", timeout: httpx.Timeout | None = None):
        self.base = base.rstrip("/")
        self.timeout = timeout or httpx.Timeout(connect=5.0, read=120.0, write=120.0, pool=5.0)

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await _post_with_retry(
                client,
                f"{self.base}/api/chat",
                {"model": model, "messages": messages, "stream": stream},
            )
            data = resp.json()
            return data.get("message", {})


class OpenRouterProvider(BaseProvider):
    key = "openrouter"

    def __init__(self, api_key: str, timeout: httpx.Timeout | None = None):
        self.api_key = api_key
        self.timeout = timeout or httpx.Timeout(connect=5.0, read=120.0, write=120.0, pool=5.0)

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENROUTER_KEY missing")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await _post_with_retry(
                client,
                "https://openrouter.ai/api/v1/chat/completions",
                {
                    "model": model,
                    "messages": messages,
                    "stream": stream,
                },
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {})


class OpenAIProvider(BaseProvider):
    key = "openai"

    def __init__(self, api_key: str, timeout: httpx.Timeout | None = None):
        self.api_key = api_key
        self.timeout = timeout or httpx.Timeout(connect=5.0, read=120.0, write=120.0, pool=5.0)

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_KEY missing")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await _post_with_retry(
                client,
                "https://api.openai.com/v1/chat/completions",
                {
                    "model": model,
                    "messages": messages,
                    "stream": stream,
                },
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {})


class FakeProvider(BaseProvider):
    key = "fake"

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if stream:

            async def _generator():
                yield {"message": {"content": "hello "}}
                yield {"message": {"content": "world"}}

            return _generator()
        return {"provider": self.key, "model": model, "message": {"content": "fake-response"}}


PROVIDERS = {
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
    "fake": FakeProvider,
    "discord": DiscordProvider,
    "slack": SlackProvider,
    "signal": SignalProvider,
    "telegram": TelegramBot,
}


def register_test_provider(key: str, factory):
    PROVIDERS[key] = factory


def unregister_test_provider(key: str):
    PROVIDERS.pop(key, None)
