import os
from typing import Optional


class SettingsStore:
    ollama_host: str = "http://localhost:11434"
    openrouter_key: str = ""
    openai_key: str = ""
    telegram_token: str = ""
    telegram_allowed_chat_ids: list[str] = []

    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", self.ollama_host)
        self.openrouter_key = os.getenv("OPENROUTER_KEY", self.openrouter_key)
        self.openai_key = os.getenv("OPENAI_KEY", self.openai_key)
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", self.telegram_token)
        raw = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")
        if raw:
            self.telegram_allowed_chat_ids = [part.strip() for part in raw.split(",") if part.strip()]

    def to_dict(self):
        return {
            "ollama": {"base": self.ollama_host},
            "openrouter": {"key_set": bool(self.openrouter_key)},
            "openai": {"key_set": bool(self.openai_key)},
            "telegram": {
                "token_set": bool(self.telegram_token),
                "allowed_chat_ids": self.telegram_allowed_chat_ids,
            },
        }

    def update(self, ollama_host: Optional[str] = None, openrouter_key: Optional[str] = None, openai_key: Optional[str] = None, telegram_token: Optional[str] = None):
        if ollama_host:
            self.ollama_host = ollama_host
        if openrouter_key:
            self.openrouter_key = openrouter_key
        if openai_key:
            self.openai_key = openai_key
        if telegram_token:
            self.telegram_token = telegram_token
