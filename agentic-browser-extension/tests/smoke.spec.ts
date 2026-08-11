import { test, expect } from "@playwright/test";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const EXT_DIR = path.resolve("dist");
const MANIFEST = path.join(EXT_DIR, "manifest.json");
const ECONNREFUSED_CODE = "ECONNREFUSED";

function request(opts: any) {
  return new Promise((resolve, reject) => {
    const req = http.request(opts, (res: any) => {
      let data = "";
      res.on("data", (chunk: any) => (data += chunk));
      res.on("end", () => resolve({ status: res.statusCode, body: data }));
    });
    req.on("error", (err: any) => {
      const code = err?.code || "";
      const status = code === ECONNREFUSED_CODE ? 0 : -1;
      resolve({ status, body: "", code });
    });
    req.write(opts.body || "");
    req.end();
  });
}

test("extension builds and manifest is valid", async () => {
  expect(fs.existsSync(EXT_DIR), "dist/ missing").toBe(true);
  expect(fs.existsSync(MANIFEST), "manifest.json missing").toBe(true);
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
  expect(manifest.name).toBe("AgenticBrowser");
  expect(manifest.manifest_version).toBe(3);
});

test("sidepanel html exists", async () => {
  const html = path.join(EXT_DIR, "sidepanel.html");
  expect(fs.existsSync(html), "sidepanel.html missing").toBe(true);
});

test("background script exists", async () => {
  const bg = path.join(EXT_DIR, "background.js");
  expect(fs.existsSync(bg), "background.js missing").toBe(true);
});

test("content script exists", async () => {
  const cs = path.join(EXT_DIR, "content.js");
  expect(fs.existsSync(cs), "content.js missing").toBe(true);
});

test("backend health endpoint returns ok", async () => {
  const resp = await request({
    hostname: "127.0.0.1",
    port: 8123,
    path: "/health",
    method: "GET",
  });
  if (resp.status === 0 || resp.status === ECONNREFUSED_CODE) {
    test.skip(true, "Backend not running on 127.0.0.1:8123");
    return;
  }
  expect(resp.status).toBe(200);
  expect(JSON.parse(resp.body)).toEqual({ status: "ok" });
});

test("backend tools endpoint returns tools", async () => {
  const resp = await request({
    hostname: "127.0.0.1",
    port: 8123,
    path: "/v1/tools",
    method: "GET",
  });
  if (resp.status === 0 || resp.status === ECONNREFUSED_CODE) {
    test.skip(true, "Backend not running on 127.0.0.1:8123");
    return;
  }
  expect(resp.status).toBe(200);
  const data = JSON.parse(resp.body);
  expect(data.tools).toHaveProperty("get_page");
  expect(data.tools).toHaveProperty("get_selection");
  expect(data.tools).toHaveProperty("search");
  expect(data.tools).toHaveProperty("summarize");
});

test("backend state history endpoint returns empty history for new session", async () => {
  const resp = await request({
    hostname: "127.0.0.1",
    port: 8123,
    path: "/v1/state/history?session_id=playwright-smoke",
    method: "GET",
  });
  if (resp.status === 0 || resp.status === ECONNREFUSED_CODE) {
    test.skip(true, "Backend not running on 127.0.0.1:8123");
    return;
  }
  expect(resp.status).toBe(200);
  const data = JSON.parse(resp.body);
  expect(data.session_id).toBe("playwright-smoke");
  expect(Array.isArray(data.messages)).toBe(true);
  expect(data.messages.length).toBe(0);
});
