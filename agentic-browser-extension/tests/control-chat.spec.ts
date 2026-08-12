import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const EXT_DIR = path.resolve("dist");

test("sidepanel bundle includes control chat UI", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  expect(fs.existsSync(js), "sidepanel.js missing").toBe(true);
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("chat");
});
