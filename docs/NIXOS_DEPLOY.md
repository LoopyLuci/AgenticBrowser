# NixOS Deployment Guide

This guide covers bringing up AgenticBrowser on NixOS as the remote target in the Windows → Hermes → mesh → NixOS control flow.

## Prerequisites
- NixOS 24.05+
- Network access to the Windows/Hermes host for mesh traffic
- `sudo` access on the NixOS node

## 1. Create service modules
Place backend and control-plane modules under `/etc/nixos/agentic-browser/` or a flake output.

## 2. Backend service
Run the FastAPI backend with uvicorn. If using HTTPS, set:
- `ssl-keyfile`
- `ssl-certfile`

If mTLS is enabled, also configure:
- `ssl-ca-certs`
- client cert verification mode

## 3. Control plane service
Run the control server on the desired Hermes mesh port. Required env vars:
- `PORT`
- `AGENTIC_CONTROL_SECRET` or `MESH_CLUSTER_KEY`
- `AGENTIC_BACKEND` for backend base URL

### Control plane HTTPS
Run the control server with HTTPS by setting:
- `HTTPS=true`
- `HTTPS_KEY_PATH`
- `HTTPS_CERT_PATH`

Example:
- `HTTPS=true HTTPS_KEY_PATH=/etc/agentic/key.pem HTTPS_CERT_PATH=/etc/agentic/cert.pem node dist/server.js`

## 4. Firewall
Allow:
- `8123/tcp` backend HTTP/HTTPS
- `8766/tcp` control plane
- mTLS/mesh ports as required by your cluster config

## 5. Verify
From Hermes/Windows:
- Control plane health: `GET /health`
- Backend health: `GET /health`

## Notes
- Keep secrets in a NixOS age-encrypted secret store or SOPS.
- Use systemd services with `Restart=on-failure`.
