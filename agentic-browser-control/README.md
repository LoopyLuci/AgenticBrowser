# AgenticBrowser Control Plane

Local control plane for AgenticBrowser on Windows.

## Launch on Windows

Prefer PowerShell or Command Prompt for long-running server processes.
Background `bash` jobs can fail with:

```
bash: no job control in this shell
```

Recommended PowerShell launch:

```powershell
cd D:\Projects\AgenticBrowser\agentic-browser-control
$env:AGENTIC_CONTROL_SECRET = "demo"
npm run start:control
```

Recommended Command Prompt launch:

```cmd
cd /d D:\Projects\AgenticBrowser\agentic-browser-control
set AGENTIC_CONTROL_SECRET=demo
npm run start:control
```

## Known limitation: port reuse

On this Windows environment, `server.listen({ reusePort: true })` is not supported:

```
ENOTSUP: operation not supported on socket 127.0.0.1:8766 ENOTSUP
```

Because of that, rapid restarts can still hit `EADDRINUSE` if a previous instance
has not fully released the socket.

## Recommended workaround

Use the provided launcher, which frees the primary control port before starting:

```bash
cd agentic-browser-control
bash scripts/start.sh
```

Or clean the port manually before restart:

```bash
netstat -ano | awk '/:8766/ && /LISTENING/ {print $5}' | sort -u | xargs -r -I {} taskkill /F /PID {}
```

## Troubleshooting

### Hermes Desktop skill dispatch returns `Invalid signature`

If the Hermes skill wrapper or local `scripts/hermes_control.py` fails with `401 Invalid signature`, confirm the control plane was started with the same secret expected by the client. On this Windows setup, if the server did not inherit the environment variable, HMAC auth will reject the request even if `/health` succeeds.

Workaround:

- Start control plane with an explicit secret: `AGENTIC_CONTROL_SECRET=demo npm run start:control`
- Call the wrapper with the same secret: `AGENTIC_CONTROL_SECRET=demo python scripts/hermes_control.py chat ...`

Windows-specific checklist:

1. Use PowerShell or Command Prompt; some bash contexts on Windows do not reliably export env vars into child Node processes.
2. Verify the server sees the secret by checking its startup log for `control secret loaded` or an equivalent auth-init message.
3. Restart after killing stale listeners on `8766` if the server is reusing state from an earlier launch.
4. If running from Hermes Desktop, confirm the shell session matches the one where the env var was set; a new shell does not inherit the prior session’s exports.

Known local limitation:
- When launching from some Windows shell contexts, `AGENTIC_CONTROL_SECRET` may not reach the Node process. Prefer PowerShell or Command Prompt for Hermes Desktop skill dispatch testing.

## Dev

```bash
npm run dev
```

## Production

```bash
npm run build
npm run start
```
