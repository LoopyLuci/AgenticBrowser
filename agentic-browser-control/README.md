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

## Dev

```bash
npm run dev
```

## Production

```bash
npm run build
npm run start
```
