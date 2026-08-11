from typing import Any, Dict, List
from app.plugins.providers.base_provider_plugin import BaseProviderPlugin

REGISTRY: Dict[str, BaseProviderPlugin] = {}


def register(plugin: BaseProviderPlugin) -> None:
    if not plugin.key:
        return
    REGISTRY[plugin.key] = plugin


def autoload(package_name: str = "app.plugins.providers"):
    try:
        pkg = __import__(package_name, fromlist=["*"])
    except Exception:
        return
    for attr in dir(pkg):
        mod = getattr(pkg, attr)
        if not hasattr(mod, "__file__"):
            continue
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type) and issubclass(obj, BaseProviderPlugin) and obj is not BaseProviderPlugin:
                try:
                    register(obj())
                except Exception:
                    pass


def list_provider_plugins() -> List[Dict[str, Any]]:
    out = []
    for key, plugin in REGISTRY.items():
        out.append({
            "key": plugin.key,
            "description": plugin.description,
        })
    return out
