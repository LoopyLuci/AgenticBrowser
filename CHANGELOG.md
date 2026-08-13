# AgenticBrowser Changelog

All notable changes to this project will be documented in this file.

## [unreleased]
- Added Telegram bot capability scaffold with command routing.
- Added Discord webhook receive tests.
- Added real client-cert mTLS validation tests using generated certs.
- Added rate-limit concurrency test asserting the 121st request is rejected.
- Added backend SSE streaming smoke test.
- Added NixOS module validation into local CI only.
- Removed GitHub Actions and made local CI/CD canonical.
- Added auto-elevating Brave sideload script for local testing.
