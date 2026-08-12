import express from "express";
import cors from "cors";
import http from "http";
import net from "node:net";
import { wireWs } from "./ws/index.js";
import { requireHmac } from "./middleware/auth.js";

const PORT = Number(process.env.PORT || 8766);

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

async function start() {
  let port = PORT;
  while (true) {
    if (!(await isPortInUse(port))) {
      const app = express();
      app.use(cors());
      app.use(express.json({ limit: "1mb" }));

      app.use((req, _res, next) => {
        (req as any).rawBody = req.body;
        next();
      });

      const server = http.createServer(app);
      wireWs(server);

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
        server.listen(port, "127.0.0.1", () => {
          console.log(`AgenticBrowser control server on http://localhost:${port}`);
          resolve();
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
