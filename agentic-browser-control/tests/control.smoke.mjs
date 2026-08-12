import http from "node:http";
import { spawn } from "node:child_process";
import crypto from "node:crypto";
import https from "node:https";
import fs from "node:fs";

const SECRET = "test-secret";
const MOCK_BACKEND_PORT = 8124;
const CONTROL_PORT = 8767;

function sign(body) {
  const mac = crypto.createHmac("sha256", SECRET).update(body).digest("hex");
  return { body, mac };
}

function createMockBackend() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      if (req.url === "/v1/chat" && req.method === "POST") {
        let body = "";
        req.on("data", (chunk) => (body += chunk));
        req.on("end", () => {
          res.writeHead(200, { "content-type": "application/json" });
          res.end(
            JSON.stringify({
              provider: "mock",
              model: "mock",
              message: { content: "mocked" },
            })
          );
        });
      } else if (req.url === "/health") {
        res.writeHead(200, { "content-type": "application/json" });
        res.end(JSON.stringify({ status: "ok" }));
      } else {
        res.writeHead(404);
        res.end("not found");
      }
    });
    server.listen(MOCK_BACKEND_PORT, "127.0.0.1", () => resolve(server));
  });
}

function startControlServer(env = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(
      process.execPath,
      ["dist/server.js"],
      {
        cwd: process.cwd(),
        env: { ...process.env, PORT: String(CONTROL_PORT), ...env },
        stdio: ["ignore", "pipe", "pipe"],
      }
    );

    let settled = false;
    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        child.kill("SIGTERM");
        reject(new Error("control server did not start in time"));
      }
    }, 10000);

    child.stdout.on("data", (data) => {
      const text = data.toString();
      if (text.includes(`localhost:${CONTROL_PORT}`)) {
        if (!settled) {
          settled = true;
          clearTimeout(timer);
          resolve(child);
        }
      }
    });

    child.stderr.on("data", (data) => {});
    child.on("error", (err) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(err);
      }
    });
    child.on("exit", (code, signal) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error(`control server exited early: ${code} ${signal}`));
      }
    });
  });
}

function stopControlServer(child) {
  return new Promise((resolve) => {
    child.on("exit", () => resolve());
    child.kill("SIGTERM");
    setTimeout(() => {
      child.kill("SIGKILL");
      resolve();
    }, 2000);
  });
}

function request(path, opts = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(`http://127.0.0.1:${CONTROL_PORT}${path}`);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: opts.method || "GET",
      headers: opts.headers || {},
    };

    const req = http.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        let data;
        try {
          data = JSON.parse(body);
        } catch {
          data = body;
        }
        resolve({ status: res.statusCode, data });
      });
    });

    req.on("error", reject);
    if (opts.body) {
      req.write(opts.body);
    }
    req.end();
  });
}

function requestHttps(path, opts = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(`https://127.0.0.1:${CONTROL_PORT}${path}`);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: opts.method || "GET",
      headers: opts.headers || {},
      rejectUnauthorized: false,
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        let data;
        try {
          data = JSON.parse(body);
        } catch {
          data = body;
        }
        resolve({ status: res.statusCode, data });
      });
    });

    req.on("error", reject);
    if (opts.body) {
      req.write(opts.body);
    }
    req.end();
  });
}

async function waitForHealth() {
  const start = Date.now();
  while (Date.now() - start < 10000) {
    try {
      const res = await request("/health");
      if (res.status === 200 && res.data?.status === "ok") return;
    } catch {
      // ignore until healthy
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error("control plane /health did not become ready");
}

async function waitForHttpsHealth() {
  const start = Date.now();
  while (Date.now() - start < 10000) {
    try {
      const res = await requestHttps("/health");
      if (res.status === 200 && res.data?.status === "ok") return;
    } catch {
      // ignore until healthy
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error("control plane /health did not become ready over HTTPS");
}

async function runTests() {
  const mockBackend = await createMockBackend();
  let controlChild;
  let httpsChild;
  try {
    controlChild = await startControlServer({
      AGENTIC_CONTROL_SECRET: SECRET,
      AGENTIC_BACKEND: `http://127.0.0.1:${MOCK_BACKEND_PORT}`,
    });
    await waitForHealth();

    // 1) Health endpoint
    let res = await request("/health");
    if (res.status !== 200 || res.data?.status !== "ok") {
      throw new Error(`health failed: ${JSON.stringify(res)}`);
    }

    // 2) Unauthorized chat without signature
    const { body: emptyBody } = sign(JSON.stringify({}));
    res = await request("/v1/control/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: emptyBody,
    });
    if (res.status !== 401) {
      throw new Error(`expected 401 without signature, got ${JSON.stringify(res)}`);
    }

    // 3) Invalid signature
    const { body: chatBody } = sign(
      JSON.stringify({ sessionId: "s1", messages: [] })
    );
    res = await request("/v1/control/chat", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-signature": "invalid",
      },
      body: chatBody,
    });
    if (res.status !== 401) {
      throw new Error(`expected 401 with invalid signature, got ${JSON.stringify(res)}`);
    }

    // 4) Valid signature with demo secret
    res = await request("/v1/control/chat", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-signature": sign(chatBody).mac,
      },
      body: chatBody,
    });
    if (res.status !== 200 || !res.data?.ok) {
      const expected = crypto.createHmac("sha256", SECRET).update(chatBody).digest("hex");
      throw new Error(`expected ok with valid signature, got ${JSON.stringify(res)}; expectedMac=${expected} body=${JSON.stringify(JSON.parse(chatBody))}`);
    }

    // 5) HTTPS smoke if certs exist
    const keyPath = "certs/key.pem";
    const certPath = "certs/cert.pem";
    if (fs.existsSync(keyPath) && fs.existsSync(certPath)) {
      httpsChild = await startControlServer({
        PORT: String(CONTROL_PORT + 1),
        AGENTIC_CONTROL_SECRET: SECRET,
        AGENTIC_BACKEND: `http://127.0.0.1:${MOCK_BACKEND_PORT}`,
        HTTPS: "true",
        HTTPS_KEY_PATH: keyPath,
        HTTPS_CERT_PATH: certPath,
      });
      await waitForHttpsHealth();
      const health = await requestHttps("/health");
      if (health.status !== 200 || health.data?.status !== "ok") {
        throw new Error(`HTTPS health failed: ${JSON.stringify(health)}`);
      }
    } else {
      console.log("HTTPS smoke skipped: missing certs");
    }

    console.log(`control smoke: ${5} passed`);
  } finally {
    if (controlChild && controlChild.exitCode === null) {
      await stopControlServer(controlChild);
    }
    if (httpsChild && httpsChild.exitCode === null) {
      await stopControlServer(httpsChild);
    }
    mockBackend.close();
  }
}

runTests().catch((err) => {
  console.error(`control smoke failed: ${err.message}`);
  process.exitCode = 1;
});
