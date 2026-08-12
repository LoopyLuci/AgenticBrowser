#!/usr/bin/env bash
set -euo pipefail

CONTROL_PORT=${1:-8766}
BACKEND_PORT=${2:-8123}
CONTROL_URL="http://127.0.0.1:${CONTROL_PORT}"
BACKEND_URL="http://127.0.0.1:${BACKEND_PORT}"

pass() { echo "[PASS] $1"; }
fail() { echo "[FAIL] $1"; exit 1; }

check_url() {
  local url=$1
  local name=$2
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
  if [ "$status" = "200" ]; then
    pass "$name health: $status"
  else
    fail "$name health: $status"
  fi
}

check_url "$BACKEND_URL/health" "Backend"
check_url "$CONTROL_URL/health" "Control plane"

echo "Validation passed"
