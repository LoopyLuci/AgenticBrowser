from typing import Any, Dict, List

from app.plugins.providers.base_provider_plugin import BaseProviderPlugin


class DiscordProvider(BaseProviderPlugin):
    key = "discord"
    description = "Discord adapter placeholder"

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        return {
            "provider": self.key,
            "model": model,
            "message": {"content": "Discord adapter stub response"},
            "finish_reason": "stub",
        }
