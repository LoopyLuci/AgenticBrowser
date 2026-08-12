# AgenticBrowser Verification Checklist

## Extension
- [x] `cd agentic-browser-extension && npm run build` succeeds
- [x] `dist/manifest.json` name/version are `AgenticBrowser`
- [x] `test/smoke.js` passes build + manifest validation
- [ ] Load unpacked from `dist` in Chrome/Edge/Firefox

## Backend
- [x] `cd agentic-browser-backend && uvicorn main:app --host 0.0.0.0 --port 8123`
- [x] `GET /health` returns `{"status":"ok"}`
- [x] `POST /v1/settings` returns updated provider state
- [x] `POST /v1/chat` works for configured providers
- [x] `GET /providers` returns available/configured providers
- [x] `GET /v1/tools` returns tool registry
- [x] `POST /v1/tools` executes registered tools
- [x] `pytest tests/test_backend.py -v` passes
- [x] `pytest tests/test_observability.py -v` passes
- [x] `pytest tests/test_rate_limit.py -v` passes
- [x] `pytest tests/test_ssl.py -v` passes
- [x] `pytest tests/test_supervisor.py -v` passes

## Control plane
- [x] `cd agentic-browser-control && npm run dev`
- [x] `GET /health` returns `{"status":"ok"}`
- [x] `POST /v1/control/chat` returns forwarded response
- [x] WebSocket `/control` auth + chat flow implemented
- [x] `npm test` passes control-plane smoke tests

## Hermes wrapper
- [x] `python scripts/tests/test_hermes_control.py` passes
- [x] `python -m pytest scripts/tests/test_skill_dispatch.py` passes

## Web UI
- [x] `cd agentic-browser-web-ui && npm run build` succeeds
- [x] `dist/index.html` builds and connects to backend at `http://localhost:8123`

## Packaging
- [x] `bash scripts/package-extension.sh` creates release artifacts
- [x] `python scripts/validate-release.py` passes
- [ ] GitHub Actions CI workflow validates all packages on every PR

## Launchers
- [x] Bash: `bash agentic-browser-control/scripts/start.sh`
- [x] PowerShell: `powershell -ExecutionPolicy Bypass -File agentic-browser-control/scripts/start.ps1`
- [x] Command Prompt: `agentic-browser-control\scripts\start.cmd`

## Branding
- [x] No remaining `page-assist` product naming in shipped files
- [x] Extension title is `AgenticBrowser`
