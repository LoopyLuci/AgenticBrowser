import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

const EXT_DIR = path.resolve("dist");
const BRAVE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: "list",
  use: {
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "brave-extension",
      testMatch: "**/*.spec.ts",
      tsconfig: "tsconfig.e2e.json",
      use: {
        ...devices["Desktop Chrome"],
        channel: undefined,
        executablePath: BRAVE,
        args: [
          `--disable-extensions-except=${EXT_DIR}`,
          `--load-extension=${EXT_DIR}`,
          "--no-first-run",
          "--no-default-browser-check",
        ],
      },
    },
  ],
});
