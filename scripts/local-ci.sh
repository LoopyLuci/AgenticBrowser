#!/usr/bin/env bash
set -euo pipefail

echo "== AgenticBrowser Local CI =="

echo "-- Backend tests --"
cd agentic-browser-backend
.venv/Scripts/python -m pytest tests/test_backend.py tests/test_providers.py -v

echo "-- Control typecheck --"
cd ../agentic-browser-control
npm run build

echo "-- Extension build + Playwright smoke --"
cd ../agentic-browser-extension
npm run build
npx playwright test tests/smoke.spec.ts --reporter=line

echo "-- Web build --"
cd ../agentic-browser-web-ui
npm run build

echo "== Local CI passed =="
