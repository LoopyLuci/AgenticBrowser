import express from "express";
import cors from "cors";
import http from "http";
import https from "https";
import fs from "node:fs";
import net from "node:net";
import { wireWs } from "./ws/index.js";
import { requireHmac } from "./middleware/auth.js";
import { startDiscoveryBeacon } from "./discovery/udp.js";

const PORT = Number(process.env.PORT || 8766);

function createServer(app: express.Express): http.Server | https.Server {
  if (process.env.HTTPS === "true") {
    const keyPath = process.env.HTTPS_KEY_PATH || process.env.HTTPS_KEY || "";
    const certPath = process.env.HTTPS_CERT_PATH || process.env.HTTPS_CERT || "";
    if (!keyPath || !certPath) {
      throw new Error("HTTPS enabled but HTTPS_KEY_PATH/HTTPS_CERT_PATH are missing");
    }
    const key = fs.readFileSync(keyPath);
    const cert = fs.readFileSync(certPath);
    return https.createServer({ key, cert }, app);
  }
  return http.createServer(app);
}

type PreflightResult = { ok: boolean; error?: string };

async function preflight(): Promise<PreflightResult> {
  const port = Number(process.env.PORT || 8766);
  if (!Number.isFinite(port) || port <= 0 || port > 65535) {
    return { ok: false, error: `Invalid PORT: ${process.env.PORT}` };
  }

  const secret = process.env.AGENTIC_CONTROL_SECRET || process.env.MESH_CLUSTER_KEY;
  if (!secret) {
    return { ok: false, error: "Missing AGENTIC_CONTROL_SECRET or MESH_CLUSTER_KEY" };
  }

  return { ok: true };
}

function isPortInUse(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = net.createConnection(port, "127.0.0.1");
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("error", () => resolve(false));
    socket.setTimeout(1000, () => {
      socket.destroy();
      resolve(false);
    });
  });
}

async function waitForBackend(url: string, timeoutMs = 15000): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url).catch(() => null);
      if (res && res.ok) return;
    } catch {
      // ignore
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Backend health check failed: ${url}`);
}

async function start() {
  const preflightResult = await preflight();
  if (!preflightResult.ok) {
    console.error("Control server preflight failed:", preflightResult.error);
    process.exit(1);
    return;
  }

  let port = PORT;
  while (true) {
    if (!(await isPortInUse(port))) {
      const app = express();
      app.use(cors());
      app.use(
        express.json({
          limit: "1mb",
          verify: (req: any, _res: any, buf: Buffer) => {
            req.rawBody = buf.toString("utf8");
          },
        })
      );

      const server = createServer(app);
      wireWs(server);
      startDiscoveryBeacon({ port, controlPort: port });

      app.get("/health", (_, res) => res.json({ status: "ok" }));
      app.post("/v1/control/chat", requireHmac, async (req, res) => {
        const { sessionId, provider, model, messages } = req.body || {};
        try {
          const { forwardChat } = await import("./chat/forwarder.js");
          const data = await forwardChat({ sessionId, provider, model, messages: messages || [] });
          res.json({ ok: true, sessionId, provider, model, data });
        } catch (err: any) {
          res.status(500).json({ ok: false, error: err?.message || "Backend error" });
        }
      });

      await new Promise<void>((resolve, reject) => {
        server.listen(port, "127.0.0.1", async () => {
          try {
            await waitForBackend(
              `${process.env.AGENTIC_BACKEND || "http://localhost:8123"}/health`
            );
            console.log(
              `AgenticBrowser control server on ${process.env.HTTPS === "true" ? "https" : "http"}://localhost:${port}`
            );
            resolve();
          } catch (err: any) {
            reject(err);
          }
        });
        server.on("error", (err: any) => {
          if (err?.code === "EADDRINUSE") {
            reject(new Error(`EADDRINUSE:${port}`));
          } else {
            reject(err);
          }
        });
      });
      return;
    }

    if (port >= PORT + 20) {
      console.error(`No available port found in range ${PORT}-${PORT + 20}`);
      process.exit(1);
      return;
    }

    console.warn(`Port ${port} busy, trying ${port + 1}`);
    await new Promise((resolve) => setTimeout(resolve, 500));
    port += 1;
  }
}

start().catch((err) => {
  console.error("Control server failed:", err);
  process.exit(1);
});
