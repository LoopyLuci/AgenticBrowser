#!/usr/bin/env bash
set -euo pipefail

if command -v nix-instantiate >/dev/null 2>&1; then
  nix-instantiate --check nix/nixos/agentic-browser.nix
else
  echo "nix-instantiate not available; skipping Nix syntax validation"
fi
