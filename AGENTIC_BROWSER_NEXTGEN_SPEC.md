# AgenticBrowser — Next-Gen Page Assist Clone

## Goal
Build an enhanced, future-proof, agentic browser assistant with a flawless pink/purple/green retro punk UI, deep integrations, and first-class extension support.

## Core Pillars
1. Multi-provider AI backend
2. Sidebar + standalone web UI
3. Agentic automation layer
4. Hermes/CLI control plane
5. Cross-browser extension
6. Flawless retro punk UX

## Architecture
- Extension package: `extension/`
  - Shell: WXT + React + Tailwind
  - Entries: sidepanel, popup, content script, background
  - Theme: global CSS + token system
- Web UI: `web-ui/`
  - Framework: Next.js or Vite + React
  - Shared design tokens/components with extension
- Agentic runtime: `agentic-core/`
  - Python package with provider adapters, agent loops, tool registry
- Control surface: `control/`
  - FastAPI control API
  - Hermes Agent integration
  - CLI + WebSocket control plane
- Config/policy: `config/`
  - Provider profiles, model routing, safety policy, allowlists

## Provider Support
- Ollama local models
- OpenAI-compatible APIs
- OpenRouter
- OpenCode
- Anthropic Claude
- Google Gemini
- Local LM Studio/llamafile-style endpoints

## Extension Feature Matrix
- Sidebar assistant on any page
- Chat with page / summarize / extract
- Local + remote model switching
- Context-aware actions from selection
- Clipboard, search, and page tools
- Knowledge attachments, prompts, and personas
- Auth/profile settings with secure storage
- Hermes remote control handshake

## UI/UX Theme: Retro Punk Cutesy
- Palette:
  - Pink: `#FF2FA7`
  - Purple: `#A259FF`
  - Green: `#39FF14`
  - Dark base: `#0B0B12`
  - Panel: `#141420`
- Effects:
  - Neon glow borders
  - CRT/grid overlays
  - Pixel accents
  - Smooth motion
  - Accessible contrast

## Agentic Capabilities
- Tool calling + function use
- Browser automation primitives
- Multi-step planning + execution
- Memory/session store
- Task templates + orchestration
- Safety + confirmation gating
- Future mode: recursive agent workflows

## Hermes Integration
- Control API exposes:
  - Session management
  - Model dispatch
  - Browser action execution
  - Push notifications
- Hermes desktop/CLI can:
  - Send prompts
  - Trigger browser actions
  - Manage sessions and provider config

## Browser Support
- Chrome
- Edge
- Brave
- Vivaldi
- Firefox
- Arc/Opera via web UI
- Safari later via WebKit portability

## Next Actions
1. Bootstrap extension with WXT + React + theme tokens
2. Build sidebar chat shell
3. Create provider adapter interface
4. Implement Hermes control API shell
5. Add agentic action registry
6. Verify multi-browser build pipeline
