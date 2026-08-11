#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="$ROOT/agentic-browser-extension"
if [ ! -d "$PKG" ]; then
  echo "Missing $PKG"
  exit 1
fi
pushd "$PKG" >/dev/null
npm run build
popd >/dev/null
mkdir -p "$ROOT/release"
cp -f "$PKG/dist/manifest.json" "$ROOT/release/agenticbrowser-manifest.json"
cp -f "$PKG/dist/sidepanel.html" "$ROOT/release/agenticbrowser-sidepanel.html"
cp -f "$PKG/dist/sidepanel.js" "$ROOT/release/agenticbrowser-sidepanel.js"
cp -f "$PKG/dist/sidepanel.css" "$ROOT/release/agenticbrowser-sidepanel.css"
cp -f "$PKG/dist/background.js" "$ROOT/release/agenticbrowser-background.js"
cp -f "$PKG/dist/content.js" "$ROOT/release/agenticbrowser-content.js"
zip -r "$ROOT/release/agenticbrowser-extension.zip" "$PKG/dist" >/dev/null 2>&1 || true
echo "Packaged into $ROOT/release/"
