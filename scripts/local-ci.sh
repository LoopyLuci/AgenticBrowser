#!/usr/bin/env bash

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"
touch "$REPORT_DIR/backend-tests.log" "$REPORT_DIR/control-build.log" "$REPORT_DIR/control-tests.log" "$REPORT_DIR/extension-build.log" "$REPORT_DIR/extension-e2e.log" "$REPORT_DIR/packaging.log" "$REPORT_DIR/web-tests.log" "$REPORT_DIR/web-build.log" "$REPORT_DIR/root-build.log"
: > "$REPORT_DIR/ci.log"
: > "$REPORT_DIR/results.jsonl"

echo "{\"run\":\"started\",\"timestamp\":\"$(date -Iseconds)\"}" >> "$REPORT_DIR/results.jsonl"

log_stage() {
  echo ""
  echo "== $1 =="
  echo "== $1 ==" >> "$REPORT_DIR/ci.log"
}

fail_stage() {
  echo "FAILED: $1"
  echo "FAILED: $1" >> "$REPORT_DIR/ci.log"
  echo "{\"stage\":\"$1\",\"status\":\"failed\",\"timestamp\":\"$(date -Iseconds)\"}" >> "$REPORT_DIR/results.jsonl"
  exit 1
}

pass_stage() {
  echo "PASS: $1"
  echo "PASS: $1" >> "$REPORT_DIR/ci.log"
  echo "{\"stage\":\"$1\",\"status\":\"passed\",\"timestamp\":\"$(date -Iseconds)\"}" >> "$REPORT_DIR/results.jsonl"
}

cd "$(dirname "$0")/.."

echo "-- Backend tests --"
cd agentic-browser-backend
.venv/Scripts/python -m pytest tests/test_backend.py tests/test_providers.py tests/test_observability.py tests/test_rate_limit.py tests/test_ssl.py tests/test_supervisor.py tests/test_discord.py tests/test_discord_webhook.py tests/test_providers_adapters.py tests/test_provider_resilience.py -v --tb=short 2>&1 | tee "$REPORT_DIR/backend-tests.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "backend-tests"; fi
pass_stage "backend-tests"

echo "-- Control typecheck --"
cd ../agentic-browser-control
npm run build 2>&1 | tee "$REPORT_DIR/control-build.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "control-build"; fi
npm test 2>&1 | tee "$REPORT_DIR/control-tests.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "control-tests"; fi
pass_stage "control-plane"

echo "-- Extension build + Playwright --"
cd ../agentic-browser-extension
npm run build 2>&1 | tee "$REPORT_DIR/extension-build.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "extension-build"; fi
if [ "${AGENTIC_RUN_EXTENSION_E2E:-}" = "1" ]; then
  npx playwright test tests/sidepanel-error-e2e.spec.ts --reporter=line --project=brave-extension 2>&1 | tee "$REPORT_DIR/extension-e2e.log"
  if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "extension-e2e"; fi
  pass_stage "extension-e2e"
else
  echo "Skipping extension E2E; set AGENTIC_RUN_EXTENSION_E2E=1 to enable"
fi
pass_stage "extension-build"

echo "-- Windows packaging validation --"
cd ..
bash scripts/package-extension.sh agentic-browser-extension/dist release/agenticbrowser-extension-windows.zip 2>&1 | tee "$REPORT_DIR/packaging.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "packaging-windows"; fi
python scripts/validate-release.py 2>&1 | tee "$REPORT_DIR/packaging.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "packaging-validation"; fi
pass_stage "packaging-windows"

echo "-- Web UI tests + build --"
cd agentic-browser-web-ui
npm test 2>&1 | tee "$REPORT_DIR/web-tests.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "web-tests"; fi
npm run build 2>&1 | tee "$REPORT_DIR/web-build.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "web-build"; fi
pass_stage "web-ui"

echo "-- Root monorepo build --"
cd ..
npm run build 2>&1 | tee "$REPORT_DIR/root-build.log"
if [ ${PIPESTATUS[0]} -ne 0 ]; then fail_stage "root-build"; fi
pass_stage "root-build"

echo ""
echo "== CI Summary =="
echo "Report: $REPORT_DIR/ci.log"
echo "Results: $REPORT_DIR/results.jsonl"
echo ""
echo "== Local CI passed =="
echo "{\"run\":\"completed\",\"status\":\"passed\",\"timestamp\":\"$(date -Iseconds)\"}" >> "$REPORT_DIR/results.jsonl"
