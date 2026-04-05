import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: "**/*.spec.ts",
  fullyParallel: false, // Sequential — single browser session with auth state
  retries: 1,
  timeout: 60_000, // 60s per test — some tabs load observability data
  expect: { timeout: 15_000 },

  use: {
    baseURL: process.env.BACKSTAGE_URL || "https://openchoreo.local:8443",
    ignoreHTTPSErrors: true, // Self-signed certs
    screenshot: "only-on-failure",
    trace: "on-first-retry",
    video: "retain-on-failure",
  },

  projects: [
    // Auth setup — runs once before all tests
    {
      name: "auth-setup",
      testMatch: /auth\.setup\.ts/,
    },
    // All UI tests depend on auth
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: ".auth/state.json",
      },
      dependencies: ["auth-setup"],
    },
  ],

  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["junit", { outputFile: "results.xml" }],
    ["list"],
  ],
});
