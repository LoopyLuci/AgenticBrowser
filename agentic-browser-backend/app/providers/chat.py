from typing import Any, Dict, List
import httpx


class BaseProvider:
    key: str = ""

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    key = "ollama"

    def __init__(self, base: str = "http://localhost:11434"):
        self.base = base.rstrip("/")

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base}/api/chat",
                json={"model": model, "messages": messages, "stream": stream},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {})


class OpenRouterProvider(BaseProvider):
    key = "openrouter"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENROUTER_KEY missing")
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "stream": stream},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {})


class OpenAIProvider(BaseProvider):
    key = "openai"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_KEY missing")
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "stream": stream},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {})


PROVIDERS = {
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
}
