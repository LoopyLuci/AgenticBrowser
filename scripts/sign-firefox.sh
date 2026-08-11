#!/usr/bin/env bash
set -euo pipefail
# Placeholder Firefox AMO signing stub.
# Replace placeholder values with real AMO signing endpoint and API key.
ZIP="${1:-release/agenticbrowser-extension.zip}"
DEST="${2:-release/agenticbrowser-extension-signed.zip}"
if [ ! -f "$ZIP" ]; then
  echo "Missing zip: $ZIP"
  exit 1
fi
cp "$ZIP" "$DEST"
echo "Placeholder signed package: $DEST"
echo "Next: integrate real AMO signing API / jpm sign --api-keypath ..."
