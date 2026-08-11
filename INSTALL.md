# AgenticBrowser Install Guide

## Backend
1. `cd agentic-browser-backend`
2. `python -m venv .venv`
3. `.\.venv\Scripts\Activate.ps1`
4. `pip install fastapi uvicorn httpx pydantic`
5. `uvicorn main:app --host 0.0.0.0 --port 8123`

## Control Plane
1. `cd agentic-browser-control`
2. `npm install`
3. `npm run dev`

## Extension
1. `cd agentic-browser-extension`
2. `npm install`
3. `npm run build`
4. Load `dist/` as unpacked extension

## Web UI
1. `cd agentic-browser-web-ui`
2. `npm install`
3. `npm run dev`

## Multi-Browser Notes
- Chrome/Edge: load unpacked `agentic-browser-extension/dist`
- Firefox: load temporary add-on from `agentic-browser-extension/dist`
- Manifest is MV3-compatible and targets Chrome-style APIs; Firefox MV3 support is available in Firefox 109+
