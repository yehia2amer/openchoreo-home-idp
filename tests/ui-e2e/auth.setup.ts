import { test as setup, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const BACKSTAGE_URL =
  process.env.BACKSTAGE_URL || "https://openchoreo.local:8443";

setup("authenticate via Thunder OAuth", async ({ page }) => {
  // Ensure .auth directory exists
  const authDir = path.join(__dirname, ".auth");
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  // Navigate to Backstage — triggers OAuth redirect to Thunder
  await page.goto(BACKSTAGE_URL);

  // Check if we get redirected to Thunder login
  const isThunderRedirect = await page
    .waitForURL(/thunder|oauth|login|authorize/, { timeout: 15000 })
    .then(() => true)
    .catch(() => false);

  if (isThunderRedirect) {
    // Thunder login page — fill credentials
    const username =
      process.env.THUNDER_USERNAME || "admin@openchoreo.dev";
    const password = process.env.THUNDER_PASSWORD || "admin";

    // Try common login form selectors
    const usernameInput = page
      .locator(
        'input[name="username"], input[type="email"], #username, input[name="login"]'
      )
      .first();
    const passwordInput = page
      .locator(
        'input[name="password"], input[type="password"], #password'
      )
      .first();

    await usernameInput.waitFor({ timeout: 10000 });
    await usernameInput.fill(username);
    await passwordInput.fill(password);

    // Submit the form
    await page
      .locator(
        'button[type="submit"], input[type="submit"], button:has-text("Sign in"), button:has-text("Log in")'
      )
      .first()
      .click();

    // Wait for redirect back to Backstage
    await page.waitForURL(`${BACKSTAGE_URL}/**`, { timeout: 30000 });
  }

  // Verify we're on Backstage and it loaded
  await expect(
    page
      .locator('text="Welcome"')
      .or(page.locator('[data-testid="user-settings-menu"]'))
      .or(page.locator("text=Platform Overview"))
      .or(page.locator("text=OpenChoreo"))
  ).toBeVisible({ timeout: 15000 });

  // Save auth state for reuse by all other tests
  await page.context().storageState({ path: ".auth/state.json" });
});
