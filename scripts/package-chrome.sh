#!/usr/bin/env bash
set -euo pipefail
# Package Chrome Web Store zip from extension build output.
SRC_DIR="${1:-agentic-browser-extension/dist}"
DEST="${2:-release/agenticbrowser-extension-chrome.zip}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
mkdir -p "$(dirname "$DEST")"
if [ ! -d "$SRC_DIR" ]; then
  echo "Missing extension dist: $SRC_DIR"
  exit 1
fi
if command -v zip >/dev/null 2>&1; then
  tmpdir="$(mktemp -d)"
  (cd "$tmpdir" && zip -r "$DEST" agenticbrowser >/dev/null)
  rm -rf "$tmpdir"
else
  # Use explicit Python helper with POSIX paths to avoid Windows/MSYS path issues.
  python "$SCRIPT_DIR/package_chrome_zip.py" \
    "$(cygpath -u "$(pwd)")/$DEST" \
    "$(cygpath -u "$(pwd)")/$SRC_DIR"
fi
echo "Packaged Chrome extension: $DEST"
