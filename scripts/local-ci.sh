#!/usr/bin/env bash
set -euo pipefail

echo "== AgenticBrowser Local CI =="

echo "-- Backend tests --"
cd agentic-browser-backend
.venv/Scripts/python -m pytest tests/test_backend.py tests/test_providers.py -v

echo "-- Backend live provider smoke --"
if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  OLLAMA_HOST=http://localhost:11434 OLLAMA_MODEL=qwen2.5:0.5b AGENTIC_TEST_OLLAMA=1 .venv/Scripts/python -m pytest tests/test_backend.py::test_provider_live_ollama_smoke tests/test_providers.py::test_ollama_live -v
else
  echo "Ollama not reachable at localhost:11434; skipping live test"
fi

if [ -n "${OPENROUTER_KEY:-}" ]; then
  AGENTIC_TEST_OPENROUTER=1 .venv/Scripts/python -m pytest tests/test_providers.py::test_openrouter_live -v
else
  echo "OPENROUTER_KEY not set; skipping OpenRouter live test"
fi

if [ -n "${OPENAI_KEY:-}" ]; then
  AGENTIC_TEST_OPENAI=1 .venv/Scripts/python -m pytest tests/test_providers.py::test_openai_live -v
else
  echo "OPENAI_KEY not set; skipping OpenAI live test"
fi

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
