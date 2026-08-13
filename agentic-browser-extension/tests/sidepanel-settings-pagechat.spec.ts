import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const EXT_DIR = path.resolve("dist");

test("extension sidepanel bundle includes settings form fields", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("Ollama Host");
  expect(content).toContain("OpenRouter Key");
  expect(content).toContain("Save");
});

test("extension sidepanel bundle includes page-chat mode toggle", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("Page Chat");
  expect(content).toMatch(/Ask about this page|page-chat/);
});
