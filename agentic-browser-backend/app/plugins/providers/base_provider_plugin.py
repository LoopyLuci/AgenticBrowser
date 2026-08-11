from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class BaseProviderPlugin(ABC):
    key: str = ""
    description: str = ""

    @abstractmethod
    async def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        raise NotImplementedError
