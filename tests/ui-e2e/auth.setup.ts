import { test as setup, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const BACKSTAGE_URL =
  process.env.BACKSTAGE_URL || "https://backstage.idp.aistudio.consulting";

setup("authenticate via Thunder OAuth", async ({ page }) => {
  const authDir = path.join(__dirname, ".auth");
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  page.on("console", (msg) => console.log(`[BROWSER] ${msg.text()}`));
  page.on("response", (resp) => {
    if (resp.status() >= 300 && resp.status() < 400) {
      console.log(`[REDIRECT] ${resp.status()} ${resp.url()} -> ${resp.headers()["location"] || "?"}`);
    }
  });

  console.log(`[TEST] Navigating to ${BACKSTAGE_URL}`);
  await page.goto(BACKSTAGE_URL, {
    waitUntil: "networkidle",
    timeout: 60000,
  });
  console.log(`[TEST] After goto, URL is: ${page.url()}`);

  // If we ended up on Thunder login, fill and submit
  if (page.url().includes("thunder") || page.url().includes("gate")) {
    console.log("[TEST] On Thunder login page, filling form...");
    const usernameInput = page.locator("#username");
    await usernameInput.waitFor({ state: "visible", timeout: 30000 });
    console.log("[TEST] Username field visible, filling...");
    
    await usernameInput.fill(process.env.THUNDER_USERNAME || "admin@openchoreo.dev");
    await page.locator("#password").fill(process.env.THUNDER_PASSWORD || "Admin@123");
    
    console.log("[TEST] Clicking Sign In...");
    await page.locator('button[type="submit"]').click();
    
    console.log(`[TEST] After click, waiting for navigation... Current URL: ${page.url()}`);
    await page.waitForURL(
      (url) => !url.href.includes("thunder") && !url.href.includes("gate"),
      { timeout: 60000 },
    );
    console.log(`[TEST] After waitForURL, URL is: ${page.url()}`);
  } else {
    console.log(`[TEST] Not on Thunder, checking if already authenticated. URL: ${page.url()}`);
  }

  // Take a screenshot to see what we got
  await page.screenshot({ path: "test-results/debug-after-login.png" });
  console.log(`[TEST] Final URL: ${page.url()}`);
  console.log(`[TEST] Page title: ${await page.title()}`);

  // Use .first() to avoid strict mode violation — multiple elements may match
  await expect(
    page
      .locator('text="Welcome"')
      .or(page.locator('[data-testid="user-settings-menu"]'))
      .or(page.locator("text=Platform Overview"))
      .or(page.locator("text=OpenChoreo"))
      .or(page.locator("text=My Company Catalog"))
      .or(page.locator("nav"))
      .first()
  ).toBeVisible({ timeout: 30000 });

  await page.context().storageState({ path: ".auth/state.json" });
});
