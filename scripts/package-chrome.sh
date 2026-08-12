#!/usr/bin/env bash
set -euo pipefail
# Package Chrome Web Store zip from extension build output.
SRC_DIR="${1:-agentic-browser-extension/dist}"
DEST="${2:-release/agenticbrowser-extension-chrome.zip}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -W | sed 's|\\|/|g')"
mkdir -p "$(dirname "$DEST")"
if [ ! -d "$SRC_DIR" ]; then
  echo "Missing extension dist: $SRC_DIR"
  exit 1
fi
if command -v zip >/dev/null 2>&1; then
  tmpdir="$(mktemp -d)"
  mkdir -p "$tmpdir/agenticbrowser"
  cp -R "$SRC_DIR"/* "$tmpdir/agenticbrowser"/
  (cd "$tmpdir" && zip -r "$DEST" agenticbrowser >/dev/null)
  rm -rf "$tmpdir"
else
  powershell -Command "Set-ExecutionPolicy Bypass -Scope Process; & '$(cygpath -w "$SCRIPT_DIR/package.ps1")' -Src '$(cygpath -w "$SRC_DIR")' -Dest '$(cygpath -w "$DEST")'"
fi
echo "Packaged Chrome extension: $DEST"
