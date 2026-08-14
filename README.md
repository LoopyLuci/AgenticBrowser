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

## Store submission prerequisites
Current packaging is ready; store submission is blocked by missing credentials only.

### Packaging validation
Before manual upload, run:
- `python scripts/validate-release.py`

### Chrome Web Store
1. Create a Chrome Web Store developer account.
2. Prepare a signed ZIP from `release/agenticbrowser-extension-chrome.zip`.
3. Required env vars: none in repo; add your own publishing secret workflow outside this repo.

### Firefox AMO
1. Use `release/agenticbrowser-extension-firefox.zip`.
2. Required AMO vars: `AMO_API_KEY`, `JWT_ISSUER`, `JWT_SECRET`.
3. Keep these out of version control; use local `.env` or secret store.

### Control plane Hermes auth
For local development, if HMAC auth is unavailable, use `AGENTIC_CONTROL_SECRET=demo` in PowerShell or Command Prompt. See `agentic-browser-control/README.md`.

## Local development

### Backend
```bash
cd agentic-browser-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8123
```

### Web UI
```bash
cd agentic-browser-web-ui
npm install
npm run dev
```

### Extension
```bash
cd agentic-browser-extension
npm install
npm run build
```
Load `agentic-browser-extension/dist` as an unpacked extension in Brave/Chrome.

### Run together
Start the backend first, then the web UI, then load the extension. The sidepanel and web UI both talk to `http://localhost:8123`.

## Local CI
Run the on-device pipeline from the repo root:
- Bash: `bash scripts/local-ci.sh`
- PowerShell: `pwsh scripts/local-ci.ps1`
- PowerShell watch mode: `pwsh scripts/local-ci.ps1 -Watch`

Reports are written to `reports/ci.log` and `reports/results.jsonl`.

### Extension E2E
Extension Playwright is opt-in because Brave headless automation can be limited:
- Bash: `AGENTIC_RUN_EXTENSION_E2E=1 bash scripts/local-ci.sh`
- PowerShell: `$env:AGENTIC_RUN_EXTENSION_E2E="1"; pwsh scripts/local-ci.ps1`

## Tests
- Backend: `cd agentic-browser-backend && .venv/Scripts/python -m pytest`
- Control plane: `cd agentic-browser-control && npm run build && npm test`
- Extension: `cd agentic-browser-extension && HEADLESS=true npx playwright test`
- Web UI: `cd agentic-browser-web-ui && npm test`

## Notes
- AgenticBrowser is the canonical product name throughout all repos.
- Default ports: backend `8123`, control plane `8766`.
- Local dev SSL certs live under `certs/`.

## Live provider tests / env setup

Set `OLLAMA_HOST` for local live tests, for example:
- PowerShell: `$env:OLLAMA_HOST="http://localhost:11434"`
- Command Prompt: `set OLLAMA_HOST=http://localhost:11434`
- Bash: `export OLLAMA_HOST=http://localhost:11434`

Backend tests:
- `cd agentic-browser-backend && OLLAMA_HOST=http://localhost:11434 OLLAMA_MODEL=qwen2.5:0.5b .venv/Scripts/python -m pytest`

Local CI:
- `bash scripts/local-ci.sh`
- OpenRouter/OpenAI live tests run only when `OPENROUTER_KEY` / `OPENAI_KEY` are set.
- If Ollama is reachable at `localhost:11434`, the live Ollama smoke test runs automatically.

Extension backend URL config:
- Open the extension sidepanel Settings.
- Save `Ollama Host` and, if needed, provider keys.
- The sidepanel sends chat requests through the background script to the backend configured there.
- mTLS/SSL is supported via the backend HTTPS port once SSL is enabled in your backend launch command.

### Manual extension smoke test
Use this checklist when running Brave/Chrome locally:
1. Load `agentic-browser-extension/dist` as an unpacked extension.
2. Open the sidepanel.
3. Confirm the empty-state prompt is visible when no messages exist.
4. Leave the input blank and press Enter; confirm the empty-input guard appears.
5. Send `hello`; confirm the assistant reply appears or an `Error:` detail is shown when the backend is unreachable.
