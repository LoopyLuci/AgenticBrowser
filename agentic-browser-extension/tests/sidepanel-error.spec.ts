import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const EXT_DIR = path.resolve("dist");

test("sidepanel bundle references offline backend error handling", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("Error:");
  expect(content).toMatch(/STREAM_TOKEN|__DONE__/);
});

test("sidepanel bundle preserves empty input guard", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toMatch(/trim\(\)|Empty message|Ask anything/);
});
