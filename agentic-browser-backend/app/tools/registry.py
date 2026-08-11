from typing import Any, Dict, Optional
import importlib
import pkgutil


class ToolContext:
    page_text: Optional[str] = None
    selection: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None


class BaseTool:
    name: str
    description: str
    arguments: Dict[str, Any]
    requires_confirm: bool = False

    async def execute(self, arguments: Dict[str, Any], ctx: ToolContext, confirm: bool = False) -> Dict[str, Any]:
        raise NotImplementedError


REGISTRY: Dict[str, BaseTool] = {}


def register(tool: BaseTool):
    REGISTRY[tool.name] = tool


def get(name: str) -> BaseTool | None:
    return REGISTRY.get(name)


def _serialize_args(args: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in (args or {}).items():
        if isinstance(v, type):
            out[k] = getattr(v, "__name__", str(v))
        else:
            out[k] = v
    return out


def list_tools() -> Dict[str, Dict[str, Any]]:
    out = {}
    for name, tool in REGISTRY.items():
        args = {}
        for k, v in (tool.arguments or {}).items():
            if isinstance(v, type):
                args[k] = getattr(v, "__name__", str(v))
            else:
                args[k] = v
        out[name] = {
            "description": tool.description,
            "arguments": args,
            "requires_confirm": tool.requires_confirm,
        }
    return out


def _iter_module_classes(mod):
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseTool) and obj is not BaseTool:
            yield obj


def autoload(package_name: str = "app.plugins.tools"):
    try:
        pkg = importlib.import_module(package_name)
    except Exception:
        return
    for finder, name, is_pkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        try:
            mod = importlib.import_module(name)
        except Exception:
            continue
        for cls in _iter_module_classes(mod):
            try:
                register(cls())
            except Exception:
                continue


class GetPageTool(BaseTool):
    name = "get_page"
    description = "Get current page text from the active tab"
    arguments = {}
    requires_confirm = False

    async def execute(self, arguments: Dict[str, Any], ctx: ToolContext, confirm: bool = False) -> Dict[str, Any]:
        return {
            "tool": self.name,
            "result": ctx.page_text or "",
            "meta": {"title": ctx.title, "url": ctx.url},
        }


class GetSelectionTool(BaseTool):
    name = "get_selection"
    description = "Get user selection from the active tab"
    arguments = {}
    requires_confirm = False

    async def execute(self, arguments: Dict[str, Any], ctx: ToolContext, confirm: bool = False) -> Dict[str, Any]:
        return {"tool": self.name, "result": ctx.selection or ""}


class SearchTool(BaseTool):
    name = "search"
    description = "Search the web"
    arguments = {"query": str}
    requires_confirm = False

    async def execute(self, arguments: Dict[str, Any], ctx: ToolContext, confirm: bool = False) -> Dict[str, Any]:
        query = arguments.get("query", "")
        return {"tool": self.name, "result": f"Search placeholder for: {query}"}


class SummarizeTool(BaseTool):
    name = "summarize"
    description = "Summarize text using the active provider"
    arguments = {"text": str, "provider": str, "model": str}
    requires_confirm = False

    async def execute(self, arguments: Dict[str, Any], ctx: ToolContext, confirm: bool = False) -> Dict[str, Any]:
        text = arguments.get("text", "") or ctx.page_text or ctx.selection or ""
        provider = arguments.get("provider", "ollama")
        model = arguments.get("model", "llama3")
        base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        if provider == "ollama":
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{base}/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "Summarize the following text accurately and concisely."},
                            {"role": "user", "content": text},
                        ],
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return {"tool": self.name, "result": data.get("message", {}).get("content", "")}
        return {"tool": self.name, "result": f"Summarization provider '{provider}' is not implemented yet."}


register(GetPageTool())
register(GetSelectionTool())
register(SearchTool())
register(SummarizeTool())
