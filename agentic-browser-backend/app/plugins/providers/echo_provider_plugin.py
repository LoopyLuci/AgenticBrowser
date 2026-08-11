from typing import Any, Dict, List
from app.plugins.providers.base_provider_plugin import BaseProviderPlugin


class EchoProviderPlugin(BaseProviderPlugin):
    key = "echo"
    description = "Echo provider plugin for plugin loader verification"

    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        last = messages[-1]["content"] if messages else "ping"
        return {"content": f"echo:{last}"}
