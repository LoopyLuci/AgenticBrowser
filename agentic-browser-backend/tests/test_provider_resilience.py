import pytest
from unittest.mock import patch

import httpx
from app.providers.chat import OpenAIProvider, OpenRouterProvider, OllamaProvider


class FakeOpenAIClient:
    def __init__(self, *args, **kwargs):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        raise httpx.RemoteProtocolError("openai network error")


class FakeOpenRouterClient:
    def __init__(self, *args, **kwargs):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        raise httpx.RemoteProtocolError("openrouter network error")


class FakeOllamaClient:
    def __init__(self, *args, **kwargs):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        raise httpx.RemoteProtocolError("ollama network error")


class FakeTimeoutClient:
    def __init__(self, *args, **kwargs):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def post(self, url, **kwargs):
        raise httpx.TimeoutException("provider request timed out")


@pytest.mark.asyncio
async def test_openai_surfaces_http_error():
    provider = OpenAIProvider(api_key="test-key")
    with patch("app.providers.chat.httpx.AsyncClient", new=FakeOpenAIClient):
        with pytest.raises(RuntimeError, match="openai network error"):
            await provider.chat("gpt-4", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_openrouter_surfaces_http_error():
    provider = OpenRouterProvider(api_key="test-key")
    with patch("app.providers.chat.httpx.AsyncClient", new=FakeOpenRouterClient):
        with pytest.raises(RuntimeError, match="openrouter network error"):
            await provider.chat("openrouter/model", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_ollama_surfaces_http_error():
    provider = OllamaProvider(base="http://localhost:11434")
    with patch("app.providers.chat.httpx.AsyncClient", new=FakeOllamaClient):
        with pytest.raises(RuntimeError, match="ollama network error"):
            await provider.chat("llama3", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_openai_surfaces_timeout():
    provider = OpenAIProvider(api_key="test-key")
    with patch("app.providers.chat.httpx.AsyncClient", new=FakeTimeoutClient):
        with pytest.raises(RuntimeError, match="provider request timed out"):
            await provider.chat("gpt-4", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_openrouter_surfaces_timeout():
    provider = OpenRouterProvider(api_key="test-key")
    with patch("app.providers.chat.httpx.AsyncClient", new=FakeTimeoutClient):
        with pytest.raises(RuntimeError, match="provider request timed out"):
            await provider.chat("openrouter/model", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_ollama_surfaces_timeout():
    provider = OllamaProvider(base="http://localhost:11434")
    with patch("app.providers.chat.httpx.AsyncClient", new=FakeTimeoutClient):
        with pytest.raises(RuntimeError, match="provider request timed out"):
            await provider.chat("llama3", [{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_openai_returns_message_on_success():
    provider = OpenAIProvider(api_key="test-key")

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, **kwargs):
            class _Resp:
                status_code = 200
                def raise_for_status(self):
                    pass
                request = None
                def json(self):
                    return {"choices": [{"message": {"content": "ok"}}]}
            return _Resp()

    with patch("app.providers.chat.httpx.AsyncClient", new=FakeClient):
        result = await provider.chat("gpt-4", [{"role": "user", "content": "hi"}])
    assert result["content"] == "ok"
