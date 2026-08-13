#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
NIXOS_MODULE="${REPO_ROOT}/nix/nixos/agentic-browser.nix"
ENV_FILE="${1:-/etc/agentic-browser/agentic.env}"
BUILD_HOST="${2:-nixos}"
BUILD_USER="${3:-root}"

if [ ! -f "${NIXOS_MODULE}" ]; then
  echo "NixOS module not found: ${NIXOS_MODULE}"
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "Env file not found: ${ENV_FILE}"
  exit 1
fi

echo "Deploying AgenticBrowser to ${BUILD_HOST}..."
ssh "${BUILD_USER}@${BUILD_HOST}" "mkdir -p /etc/agentic-browser /opt/agentic-browser/control /opt/agentic-browser/backend"
scp "${ENV_FILE}" "${BUILD_USER}@${BUILD_HOST}:/etc/agentic-browser/agentic.env"
ssh "${BUILD_USER}@${BUILD_HOST}" "nix build --flake '${NIXOS_MODULE}'"
echo "Deployment complete. Enable with: systemctl enable --now agentic-browser-control agentic-browser-backend"
