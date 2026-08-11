# AgenticBrowser — Hermes Desktop/CLI Integration

## Overview
Hermes Agent Desktop/CLI can control AgenticBrowser through the control plane at `http://localhost:8766` using HMAC-SHA256 signed requests.

## Control Plane Auth
- Header: `x-signature: <HMAC-SHA256 hex>`
- Secret from `AGENTIC_CONTROL_SECRET` or `MESH_CLUSTER_KEY`
- Body: raw JSON string used as HMAC message
- Example: `x-signature` = `HMAC(secret, JSON.stringify(payload))`

## Pairing
1. Set `AGENTIC_CONTROL_SECRET` in `agentic-browser-control` environment.
2. Send `POST /v1/control/chat` with `x-signature`.
3. Extension can also open `http://localhost:8766/health` to verify connectivity.

## WebSocket
- Path: `ws://localhost:8766/control`
- Auth message: `{"type":"auth","sessionId":"<id>","token":"<optional>"}`
- Chat message: `{"type":"chat","id":"<reqId>","sessionId":"<id>","provider":"ollama","model":"llama3","messages":[...]}`

## Hermes Skill
Use `mesh-cluster-control` style commands to dispatch browser tasks:
- Open page
- Summarize selection
- Run tool by name
- Stream chat response
