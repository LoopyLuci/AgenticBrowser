#!/usr/bin/env python3
"""Hermes/CLI wrapper for AgenticBrowser control plane + backend."""
import argparse
import hashlib
import hmac
import json
import os
import sys
from urllib import request, error

CONTROL_BASE = os.getenv("AGENTIC_CONTROL_BASE", "http://localhost:8766")
BACKEND_BASE = os.getenv("AGENTIC_BACKEND_BASE", "http://127.0.0.1:8123")
SECRET = os.getenv("AGENTIC_CONTROL_SECRET", os.getenv("MESH_CLUSTER_KEY", ""))


def sign(payload: dict) -> str:
    secret = os.getenv("AGENTIC_CONTROL_SECRET", os.getenv("MESH_CLUSTER_KEY", ""))
    body = json.dumps(payload).encode()
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return mac


def call(base: str, path: str, payload: dict | None = None):
    url = f"{base}{path}"
    body = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["x-signature"] = sign(payload)
    req = request.Request(url, data=body, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode() or "{}")
    except error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": e.read().decode()}
    except error.URLError as e:
        return {"ok": False, "error": str(e.reason)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["health", "chat", "settings"])
    parser.add_argument("--session-id", default="cli")
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="llama3")
    parser.add_argument("--message")
    parser.add_argument("--ollama-host")
    parser.add_argument("--openrouter-key")
    parser.add_argument("--openai-key")
    args = parser.parse_args()

    if args.command == "health":
        print(call(CONTROL_BASE, "/health"))
    elif args.command == "chat":
        if not args.message:
            print("--message is required for chat"); sys.exit(2)
        payload = {
            "sessionId": args.session_id,
            "provider": args.provider,
            "model": args.model,
            "messages": [{"role": "user", "content": args.message}],
        }
        print(call(CONTROL_BASE, "/v1/control/chat", payload))
    elif args.command == "settings":
        payload = {}
        if args.ollama_host:
            payload["ollamaHost"] = args.ollama_host
        if args.openrouter_key:
            payload["openrouterKey"] = args.openrouter_key
        if args.openai_key:
            payload["openaiKey"] = args.openai_key
        print(call(BACKEND_BASE, "/v1/settings", payload or None))


if __name__ == "__main__":
    main()
