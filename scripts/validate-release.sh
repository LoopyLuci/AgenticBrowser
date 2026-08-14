#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RELEASE_DIR="${1:-$ROOT/release}"

if [ ! -d "$RELEASE_DIR" ]; then
  echo "Missing release directory: $RELEASE_DIR"
  exit 1
fi

"$ROOT/.venv/Scripts/python" "$ROOT/scripts/validate-release.py" "$RELEASE_DIR"
STATUS=$?

if [ $STATUS -eq 0 ]; then
  echo "Release validation passed for $RELEASE_DIR"
else
  echo "Release validation failed for $RELEASE_DIR"
fi

exit $STATUS
