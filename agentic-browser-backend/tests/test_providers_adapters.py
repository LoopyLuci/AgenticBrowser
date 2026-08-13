import pytest

from app.providers.chat import OpenRouterProvider, OpenAIProvider, OllamaProvider
from app.providers.telegram_bot import TelegramBot, TelegramUpdate


def test_openrouter_requires_api_key():
    with pytest.raises(ValueError, match="OPENROUTER_KEY missing"):
        __import__("asyncio").run(OpenRouterProvider("").chat("model", []))


def test_openai_requires_api_key():
    with pytest.raises(ValueError, match="OPENAI_KEY missing"):
        __import__("asyncio").run(OpenAIProvider("").chat("model", []))


def test_ollama_defaults_base_url():
    provider = OllamaProvider()
    assert provider.base == "http://localhost:11434"


def test_telegram_bot_reads_env_token(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "env-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "1,2,3")
    from app.settings.store import SettingsStore

    store = SettingsStore()
    assert store.telegram_token == "env-token"
    assert store.telegram_allowed_chat_ids == ["1", "2", "3"]
