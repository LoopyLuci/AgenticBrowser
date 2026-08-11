#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8766}"
cd "$(cd "$(dirname "$0")/.." && pwd)"

kill_port() {
  local p="$1"
  local pid
  pid="$(netstat -ano | awk -v p=":$p" '$0 ~ p {print $5; exit}')" || true
  if [ -n "${pid:-}" ]; then
    echo "Killing stale PID $pid on port $p"
    taskkill /F /PID "$pid" >/dev/null 2>&1 || true
    sleep 1
  fi
}

if [ "$PORT" != "8766" ]; then
  kill_port "$PORT"
fi

# Always clean the primary control port too, in case it was reused.
kill_port 8766

export AGENTIC_CONTROL_SECRET="${AGENTIC_CONTROL_SECRET:-demo}"
npx tsx src/server.ts
