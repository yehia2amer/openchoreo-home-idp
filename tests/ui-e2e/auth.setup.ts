import { test as setup, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const BACKSTAGE_URL =
  process.env.BACKSTAGE_URL || "https://backstage.idp.aistudio.consulting";

setup("authenticate via Thunder OAuth", async ({ page }) => {
  setup.setTimeout(120_000);
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
    await page.waitForLoadState("domcontentloaded");
    const usernameInput = page.locator("#username");
    await usernameInput.waitFor({ state: "visible", timeout: 60000 });
    console.log("[TEST] Username field visible, filling...");
    
    await usernameInput.fill(process.env.THUNDER_USERNAME || "admin@pwc.com");
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
    // Check for Backstage sign-in page (shows "Sign In" button before redirecting to Thunder)
    const signInButton = page.locator('button:has-text("Sign In"), button:has-text("Sign in")').first();
    
    if (await signInButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      console.log("[TEST] On Backstage sign-in page, clicking Sign In button...");
      await signInButton.click();
      
      // Wait for redirect to Thunder
      await page.waitForURL(
        (url) => /thunder|oauth|gate|authorize/.test(url.href),
        { timeout: 60000 },
      );
      console.log(`[TEST] Redirected to Thunder: ${page.url()}`);
      
      // Fill Thunder login form
      await page.waitForLoadState("domcontentloaded");
      const usernameInput = page.locator("#username");
      await usernameInput.waitFor({ state: "visible", timeout: 60000 });
      console.log("[TEST] Username field visible, filling...");
      await usernameInput.fill(process.env.THUNDER_USERNAME || "admin@pwc.com");
      await page.locator("#password").fill(process.env.THUNDER_PASSWORD || "Admin@123");
      
      console.log("[TEST] Clicking Sign In on Thunder...");
      await page.locator('button[type="submit"]').click();
      
      console.log(`[TEST] After Thunder submit, waiting for redirect back... URL: ${page.url()}`);
      await page.waitForURL(
        (url) => !url.href.includes("thunder") && !url.href.includes("gate"),
        { timeout: 60000 },
      );
      console.log(`[TEST] Back at Backstage: ${page.url()}`);
    } else {
      console.log(`[TEST] Already authenticated or unknown state. URL: ${page.url()}`);
    }
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
      .first()
  ).toBeVisible({ timeout: 30000 });

  await page.context().storageState({ path: ".auth/state.json" });
});
