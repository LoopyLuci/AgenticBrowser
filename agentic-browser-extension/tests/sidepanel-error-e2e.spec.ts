import { test, expect, chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";
import crypto from "node:crypto";

const EXT_DIR = path.resolve("dist");
const BRAVE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";

async function getExtensionId(page) {
  await page.evaluate(() => {
    if ((window as any).chrome?.management?.getAll) {
      (window as any).chrome.management.getAll((exts) => {
        const agentic = exts.find(
          (e: any) => e.enabled && e.path && e.path.includes("agentic-browser-extension")
        );
        if (agentic) {
          (window as any).__AGENTIC_EXTENSION_ID__ = agentic.id;
        }
      });
    }
  });
  await new Promise((r) => setTimeout(r, 1000));

  const manifestPath = path.join(EXT_DIR, "manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const name = manifest.name || "AgenticBrowser";

  let extensionId = await page.evaluate(() => (window as any).__AGENTIC_EXTENSION_ID__ || "");
  if (!extensionId) {
    const normalized = EXT_DIR.toLowerCase().replace(/\\/g, "/");
    extensionId = crypto.createHash("sha256").update(normalized).digest("hex").slice(0, 32);
  }
  return extensionId;
}

test("sidepanel shows empty input guard and backend error state", async () => {
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
  const page = await context.newPage();
  const extensionId = await getExtensionId(page);
  await page.goto(`chrome-extension://${extensionId}/sidepanel.html`);
  await new Promise((r) => setTimeout(r, 1000));

  const input = page.locator("input[placeholder*='Ask anything']");
  await expect(input).toBeVisible();

  await input.fill("");
  await input.press("Enter");
  await new Promise((r) => setTimeout(r, 300));
  const emptyState = page.locator("text=Ask anything…");
  await expect(emptyState).toBeVisible();

  await page.route("**/v1/chat", (route) => route.fulfill({ status: 500, body: '{"detail":"offline"}' }));

  await input.fill("hello");
  await input.press("Enter");
  await new Promise((r) => setTimeout(r, 500));
  const errorText = page.locator("text=Error:");
  await expect(errorText).toBeVisible();

  await context.close();
});
