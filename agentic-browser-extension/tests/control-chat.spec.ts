import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const EXT_DIR = path.resolve("dist");
const BRAVE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";

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

test("extension sidepanel bundle includes chat input and submit handler", async () => {
  const js = path.join(EXT_DIR, "sidepanel.js");
  const content = fs.readFileSync(js, "utf8");
  expect(content).toContain("Ask anything");
  expect(content).toMatch(/onKeyDown|Enter/);
});

test("Brave loads the sideloaded extension bundle in headless", async ({ browser }) => {
  if (process.env.CI || process.env.HEADLESS === "true") {
    test.skip(true, "Skip live Brave extension UI test in automated environments");
    return;
  }

  const context = await browser.launchPersistentContext("C:\\Users\\limpi\\AppData\\Local\\Temp\\playwright-brave-ext", {
    executablePath: BRAVE,
    headless: false,
    args: [
      `--disable-extensions-except=${EXT_DIR}`,
      `--load-extension=${EXT_DIR}`,
      "--no-first-run",
      "--no-default-browser-check",
    ],
  });

  const page = await context.newPage();
  await page.goto("https://example.com");
  await page.waitForTimeout(1000);

  const loaded = await page.evaluate(async () => {
    try {
      if (!chrome.management?.getAll) return false;
      const all = await new Promise((resolve) => chrome.management.getAll(resolve));
      return all.some((e) => e.enabled && e.path && e.path.includes("agentic-browser-extension"));
    } catch {
      return false;
    }
  });

  expect(loaded, "AgenticBrowser extension was not loaded").toBe(true);

  await context.close();
});
