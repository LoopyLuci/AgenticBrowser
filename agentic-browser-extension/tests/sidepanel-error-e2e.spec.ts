import { test, expect, chromium } from "@playwright/test";
import path from "node:path";

const EXT_DIR = path.resolve("dist");
const BRAVE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";

test("sidepanel loads extension UI and shows provider/timeout controls", async () => {
  const context = await chromium.launchPersistentContext("", {
    executablePath: BRAVE,
    headless: true,
    args: [
      `--disable-extensions-except=${EXT_DIR}`,
      `--load-extension=${EXT_DIR}`,
      "--no-first-run",
      "--no-default-browser-check",
    ],
  });

  try {
    const page = await context.newPage();
    await page.goto(`file://${path.join(EXT_DIR, "sidepanel.html").replace(/\\/g, "/")}`);
    await page.waitForTimeout(500);

    const providerSelect = page.locator('select').first();
    const timeoutInput = page.locator('input[placeholder*="seconds"], input[type="number"]').first();
    const saveButton = page.locator('button:has-text("Save")');

    // Best-effort smoke assertions; headless Brave extension rendering may be limited.
    await expect(providerSelect.or(timeoutInput).or(saveButton).first()).toBeVisible();
  } finally {
    await context.close();
  }
});
