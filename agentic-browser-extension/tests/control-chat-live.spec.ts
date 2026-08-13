import { test, expect, chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const EXT_DIR = path.resolve("dist");
const BRAVE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";

async function getExtensionId(context) {
  const extensionIdSet = new Set();
  await context.addInitScript(() => {
    if ((window as any).chrome?.management?.getAll) {
      (window as any).chrome.management.getAll((exts) => {
        exts.forEach((e: any) => extensionIdSet.add(e.id));
      });
    }
  });
  await new Promise((r) => setTimeout(r, 1000));
  const paths = fs.readdirSync(EXT_DIR);
  const manifestPath = path.join(EXT_DIR, "manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const name = manifest.name || "AgenticBrowser";
  const id = Array.from(extensionIdSet).find((id) => id !== undefined) || "";
  return id;
}

test("Brave sidepanel chat input accepts typing and submit", async () => {
  if (process.env.CI || process.env.HEADLESS === "true") {
    test.skip(true, "Skip headed Brave live extension test in CI/headless");
    return;
  }

  const context = await chromium.launchPersistentContext("", {
    channel: undefined,
    executablePath: BRAVE,
    headless: true,
    args: [
      `--disable-extensions-except=${EXT_DIR}`,
      `--load-extension=${EXT_DIR}`,
      "--no-first-run",
      "--no-default-browser-check",
    ],
  });
  const extensionId = await getExtensionId(context);
  const page = await context.newPage();
  await page.goto(`chrome-extension://${extensionId}/sidepanel.html`);
  await new Promise((r) => setTimeout(r, 1000));
  const input = page.locator("input[placeholder*='Ask anything']");
  await expect(input).toBeVisible();
  await input.fill("hello from playwright");
  await input.press("Enter");
  await new Promise((r) => setTimeout(r, 500));
  const messages = page.locator("text=hello from playwright");
  await expect(messages).toBeVisible();
  await context.close();
});
