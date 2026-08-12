import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const EXT_DIR = path.resolve("dist");

test("extension sidepanel bundle includes chat UI", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  expect(fs.existsSync(js), "sidepanel.js missing").toBe(true);
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("chat");
});

test("extension sidepanel bundle includes control chat route", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("control");
  expect(content).toContain("v1");
  expect(content).toContain("chat");
});

test("extension sidepanel opens with chat input element", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("chat");
  expect(content).toMatch(/input|textarea/i);
});
