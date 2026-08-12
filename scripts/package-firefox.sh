#!/usr/bin/env bash
set -euo pipefail
# Package Firefox/AMO extension bundle from extension build output.
SRC_DIR="${1:-agentic-browser-extension/dist}"
DEST="${2:-release/agenticbrowser-extension-firefox.zip}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -W | sed 's|\\|/|g')"
mkdir -p "$(dirname "$DEST")"
if [ ! -d "$SRC_DIR" ]; then
  echo "Missing extension dist: $SRC_DIR"
  exit 1
fi
tmpdir="$(mktemp -d)"
mkdir -p "$tmpdir/agenticbrowser"
cp -R "$SRC_DIR"/* "$tmpdir/agenticbrowser"/
if [ ! -f "$tmpdir/agenticbrowser/manifest.firefox.json" ]; then
  if [ -f "$tmpdir/agenticbrowser/manifest.json" ]; then
    cp "$tmpdir/agenticbrowser/manifest.json" "$tmpdir/agenticbrowser/manifest.firefox.json"
  else
    echo "Missing manifest.firefox.json"
    exit 1
  fi
fi
if command -v zip >/dev/null 2>&1; then
  (cd "$tmpdir" && zip -r "$DEST" agenticbrowser >/dev/null)
else
  powershell -Command "Set-ExecutionPolicy Bypass -Scope Process; & '$(cygpath -w "$SCRIPT_DIR/package.ps1")' -Src '$(cygpath -w "$tmpdir/agenticbrowser")' -Dest '$(cygpath -w "$DEST")'"
fi
rm -rf "$tmpdir"
echo "Packaged Firefox extension: $DEST"
