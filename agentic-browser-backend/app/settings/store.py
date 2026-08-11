import os
from typing import Optional


class SettingsStore:
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    openrouter_key: str = os.getenv("OPENROUTER_KEY", "")
    openai_key: str = os.getenv("OPENAI_KEY", "")

    def to_dict(self):
        return {
            "ollama": {"base": self.ollama_host},
            "openrouter": {"key_set": bool(self.openrouter_key)},
            "openai": {"key_set": bool(self.openai_key)},
        }

    def update(self, ollama_host: Optional[str] = None, openrouter_key: Optional[str] = None, openai_key: Optional[str] = None):
        if ollama_host:
            self.ollama_host = ollama_host
        if openrouter_key:
            self.openrouter_key = openrouter_key
        if openai_key:
            self.openai_key = openai_key
