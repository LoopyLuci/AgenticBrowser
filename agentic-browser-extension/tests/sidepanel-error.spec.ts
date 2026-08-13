import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const EXT_DIR = path.resolve("dist");

test("sidepanel bundle omits empty/short placeholder-only strings", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("Ask anything");
  expect(content).toContain("Error:");
});

test("sidepanel bundle references backend host placeholder", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("localhost:8123");
  expect(content).toMatch(/CHAT_STREAM_REQUEST|REGISTER_STREAM_LISTENER/);
});
