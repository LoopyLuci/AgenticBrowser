from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import logging
import json
import os
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNTS = defaultdict(int)
REQUEST_LATENCY = defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 120
_rate_limit_store = defaultdict(list)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        route = request.url.path
        REQUEST_COUNTS[route] += 1
        REQUEST_LATENCY[route].append(duration)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.time()
        window = RATE_LIMIT_WINDOW
        timestamps = [t for t in _rate_limit_store[client] if now - t < window]
        _rate_limit_store[client] = timestamps
        if len(timestamps) >= RATE_LIMIT_MAX:
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        timestamps.append(now)
        return await call_next(request)


def register_routes(app: FastAPI):
    @app.get("/metrics")
    def metrics():
        summary = {}
        for route, count in REQUEST_COUNTS.items():
            latencies = REQUEST_LATENCY[route]
            avg = sum(latencies) / len(latencies) if latencies else 0
            summary[route] = {"count": count, "avg_latency_s": avg}
        return {"requests": summary}


def audit(event: str, payload: dict):
    record = {"event": event, **payload}
    logger = logging.getLogger("agentic.audit")
    logger.info(json.dumps(record))
