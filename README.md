# AgenticBrowser

Next-generation agentic browser assistant with a pink/purple/green retro punk theme.

## Packages
- `agentic-browser-extension/` — Chrome/Edge/Firefox sidebar extension built with React and Vite.
- `agentic-browser-web-ui/` — Standalone web UI.
- `agentic-browser-backend/` — FastAPI backend with Ollama, OpenRouter, OpenAI, settings, and agentic tool registry.
- `agentic-browser-control/` — Hermes/CLI control plane with REST and WebSocket.

## Quick start
1. Start backend:
```bash
cd agentic-browser-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn httpx pydantic
uvicorn main:app --host 0.0.0.0 --port 8123
```

2. Start control plane:
```bash
cd agentic-browser-control
npm install
npx tsx src/server.ts
```

3. Build extension:
```bash
cd agentic-browser-extension
npm install
npm run build
```

4. Load `agentic-browser-extension/dist` as an unpacked extension in Chrome or Edge.

## Controls
- Toggle sidebar: `Ctrl+Shift+Y`
- Chat mode and Page Chat mode are available in the sidebar.
- Settings UI saves provider keys to the backend `/v1/settings`.

## Hermes integration
- Control plane exposes `/v1/control/chat` and WebSocket `/control`.
- Hermes desktop/CLI can POST prompts and receive responses through the control server.

## Notes
- AgenticBrowser is the canonical product name throughout all repos.
- Default ports: backend `8123`, control plane `8766`.
