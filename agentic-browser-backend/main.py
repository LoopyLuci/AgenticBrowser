from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import json
import os

from app.providers.chat import PROVIDERS
from app.tools.registry import list_tools, get, ToolContext, autoload
from app.plugins.providers import autoload as autoload_providers
from app.settings.store import SettingsStore
from app.resilience.logging import setup_logging
from app.resilience.queue import init_db
from app.observability.metrics import MetricsMiddleware, RateLimitMiddleware, audit, register_routes
from app.state.store import (
    init_state_db,
    get_or_create_session,
    append_message,
    get_messages,
    set_setting,
    get_setting,
    export_settings,
    import_settings,
)
from sse_starlette import EventSourceResponse

setup_logging()
init_db()
init_state_db()
autoload("app.plugins.tools")
autoload_providers()

app = FastAPI(title="AgenticBrowser Backend")
app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimitMiddleware)


class MTLSMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        header_key = b"x-client-cert-present"
        if headers.get(header_key, b"").lower() != b"true":
            from fastapi.responses import JSONResponse

            response = JSONResponse(
                status_code=403, content={"detail": "Missing client certificate"}
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


if os.getenv("MTLS_ENABLED") == "true":
    app.add_middleware(MTLSMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_routes(app)
settings = SettingsStore()


class ChatRequest(BaseModel):
    session_id: str
    messages: list[dict[str, Any]]
    provider: str
    model: str
    stream: bool = False
    tools: Optional[list[dict[str, Any]]] = None


class SettingsRequest(BaseModel):
    ollamaHost: Optional[str] = None
    openrouterKey: Optional[str] = None
    openaiKey: Optional[str] = None


class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]
    confirm: bool = False
    context: Optional[Dict[str, Any]] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/providers")
def providers():
    return {
        "available": list(PROVIDERS.keys()),
        "configured": settings.to_dict(),
    }


@app.post("/v1/settings")
def update_settings(req: SettingsRequest):
    if req.ollamaHost:
        settings.update(req.ollamaHost, settings.openrouter_key, settings.openai_key)
        set_setting("ollamaHost", req.ollamaHost)
    if req.openrouterKey:
        settings.update(settings.ollama_host, req.openrouterKey, settings.openai_key)
        set_setting("openrouterKey", req.openrouterKey)
    if req.openaiKey:
        settings.update(settings.ollama_host, settings.openrouter_key, req.openaiKey)
        set_setting("openaiKey", req.openaiKey)
    audit("settings_update", {"provider_state": settings.to_dict()})
    return settings.to_dict()


@app.get("/v1/settings")
def read_settings():
    return {
        "ollamaHost": get_setting("ollamaHost") or settings.ollama_host,
        "openrouterKey": get_setting("openrouterKey") or settings.openrouter_key,
        "openaiKey": get_setting("openaiKey") or settings.openai_key,
    }


@app.get("/v1/tools")
def tool_list():
    return {"tools": list_tools()}


@app.post("/v1/tools")
def tool_execute(req: ToolRequest):
    tool = get(req.name)
    if not tool:
        raise HTTPException(status_code=400, detail="Unsupported tool")
    ctx = ToolContext()
    if req.context:
        ctx.page_text = req.context.get("pageText")
        ctx.selection = req.context.get("selection")
        ctx.title = req.context.get("title")
        ctx.url = req.context.get("url")
    try:
        import asyncio

        result = asyncio.run(tool.execute(req.arguments, ctx, confirm=req.confirm))
        audit("tool_execute", {"tool": req.name, "arguments": req.arguments, "result": result})
        return result
    except Exception as e:
        audit("tool_error", {"tool": req.name, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat")
async def chat(req: ChatRequest):
    provider_cls = PROVIDERS.get(req.provider)
    if not provider_cls:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {req.provider}")

    get_or_create_session(req.session_id)
    for msg in req.messages:
        append_message(req.session_id, msg["role"], msg["content"])

    if req.provider == "ollama":
        provider = provider_cls(settings.ollama_host)
    elif req.provider == "openrouter":
        provider = provider_cls(settings.openrouter_key)
    elif req.provider == "openai":
        provider = provider_cls(settings.openai_key)
    else:
        provider = provider_cls()

    try:
        start = time.time()
        message = await provider.chat(req.model, req.messages, req.stream)
        latency = time.time() - start
        append_message(req.session_id, "assistant", message.get("content", ""))
        audit("chat_complete", {"provider": req.provider, "model": req.model, "latency_s": latency, "session_id": req.session_id})
        return {"provider": req.provider, "model": req.model, "message": message, "session_id": req.session_id}
    except ValueError as e:
        audit("chat_error", {"provider": req.provider, "model": req.model, "error": str(e), "session_id": req.session_id})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        audit("chat_error", {"provider": req.provider, "model": req.model, "error": str(e), "session_id": req.session_id})
        raise HTTPException(status_code=500, detail=str(e))


async def _sse_chat(req: ChatRequest):
    provider_cls = PROVIDERS.get(req.provider)
    if not provider_cls:
        yield {"event": "error", "data": json.dumps({"detail": f"Unsupported provider: {req.provider}"})}
        return

    get_or_create_session(req.session_id)
    for msg in req.messages:
        append_message(req.session_id, msg["role"], msg["content"])

    if req.provider == "ollama":
        provider = provider_cls(settings.ollama_host)
    elif req.provider == "openrouter":
        provider = provider_cls(settings.openrouter_key)
    elif req.provider == "openai":
        provider = provider_cls(settings.openai_key)
    else:
        provider = provider_cls()

    start = time.time()
    full = []
    try:
        stream = provider.chat(req.model, req.messages, True)
        async for chunk in stream:
            token = chunk.get("message", {}).get("content", "")
            if token:
                full.append(token)
                yield {"event": "token", "data": json.dumps({"token": token})}
        latency = time.time() - start
        content = "".join(full)
        append_message(req.session_id, "assistant", content)
        audit("chat_stream_complete", {"provider": req.provider, "model": req.model, "latency_s": latency, "session_id": req.session_id})
        yield {"event": "done", "data": json.dumps({"content": content, "session_id": req.session_id})}
    except Exception as e:
        audit("chat_stream_error", {"provider": req.provider, "model": req.model, "error": str(e), "session_id": req.session_id})
        yield {"event": "error", "data": json.dumps({"detail": str(e)})}


@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    return EventSourceResponse(_sse_chat(req))


@app.get("/v1/state/history")
def history(session_id: str, limit: int = 200):
    get_or_create_session(session_id)
    return {"session_id": session_id, "messages": get_messages(session_id, limit)}


@app.post("/v1/state/export")
def state_export():
    return {
        "settings": export_settings(),
        "note": "History export requires session_id enumeration; use /v1/state/history per session.",
    }


@app.post("/v1/state/import")
def state_import(payload: Dict[str, Optional[str]]):
    import_settings(payload or {})
    return {"ok": True, "count": len(payload or {})}
