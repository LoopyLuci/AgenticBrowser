# AgenticBrowser Verification

Use the local CI pipeline only; GitHub Actions are not used.

## Local CI
From repo root, run:
- `bash scripts/local-ci.sh`

## Backend
From `agentic-browser-backend`:
- `.venv/Scripts/python -m pytest -v`

## Control plane
From `agentic-browser-control`:
- `npm run build`
- `npm test`

## Extension
From `agentic-browser-extension`:
- `npm run build`
- `npx playwright test tests/control-chat.spec.ts --reporter=line --project=chromium`

## Notes
- `certs/key.pem` and `certs/cert.pem` are local test artifacts.
- `MTLS_ENABLED=true` enables mTLS checks; real cert validation is tested in `tests/test_mtls.py`.
- Discovery smoke uses control server startup log assertions in `agentic-browser-control/tests/discovery_smoke.py`.
- Discord webhook tests: `agentic-browser-backend/tests/test_discord.py` and `agentic-browser-backend/tests/test_discord_webhook.py`.
- Telegram bot smoke: `agentic-browser-backend/tests/test_telegram_bot.py`.
- Fake provider is registered via `tests/conftest.py` + `tests/test_chat_stream.py` fixture; no import-time mutation.
