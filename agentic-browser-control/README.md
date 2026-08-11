# AgenticBrowser Control Plane

Local control plane for AgenticBrowser on Windows.

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
