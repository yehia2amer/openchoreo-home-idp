import { test, expect, type Page } from '@playwright/test';

/**
 * Standalone E2E login flow: Backstage → Thunder OAuth → credentials → redirect → main screen.
 * Env: BACKSTAGE_URL, THUNDER_USERNAME, THUNDER_PASSWORD
 */

const BACKSTAGE_URL =
  process.env.BACKSTAGE_URL ?? 'https://backstage.idp.aistudio.consulting';
const USERNAME = process.env.THUNDER_USERNAME ?? 'admin@openchoreo.dev';
const PASSWORD = process.env.THUNDER_PASSWORD ?? 'admin';

test.describe('Login Flow', () => {
  test.use({
    ignoreHTTPSErrors: true,
    storageState: undefined,
  });

  test('should complete full OAuth login and reach the main screen', async ({
    browser,
  }) => {
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    const page = await context.newPage();

    try {
      await loginFlow(page);
    } finally {
      await context.close();
    }
  });

  test.afterEach(async (_unused, testInfo) => {
    if (testInfo.status !== testInfo.expectedStatus) {
      try {
        testInfo.annotations.push({
          type: 'failure-screenshot',
          description: `test-results/login-flow-failure-${Date.now()}.png`,
        });
      } catch {
        /* best-effort */
      }
    }
  });
});

async function loginFlow(page: Page): Promise<void> {
  // Given: navigate to Backstage, expect OAuth redirect
  await page.goto(BACKSTAGE_URL, {
    waitUntil: 'domcontentloaded',
    timeout: 30_000,
  });

  // When: OAuth redirects to Thunder login page
  await page.waitForURL(
    (url) => /thunder|oauth|login|authorize/.test(url.href),
    { timeout: 30_000 },
  );

  // When: fill username (multiple selectors for Thunder's varying form layouts)
  const usernameField = page
    .locator(
      [
        'input[name="usernameUserInput"]',
        'input[name="username"]',
        'input[type="email"]',
        '#username',
        'input[name="login"]',
      ].join(', '),
    )
    .first();
  await usernameField.waitFor({ state: 'visible', timeout: 15_000 });
  await usernameField.fill(USERNAME);

  // When: handle optional "Continue" step before password
  const continueButton = page.locator('button:has-text("Continue")');
  if (await continueButton.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await continueButton.click();
    await page.waitForTimeout(1_000);
  }

  // When: fill password
  const passwordField = page
    .locator(
      ['input[name="password"]', 'input[type="password"]', '#password'].join(
        ', ',
      ),
    )
    .first();
  await passwordField.waitFor({ state: 'visible', timeout: 15_000 });
  await passwordField.fill(PASSWORD);

  await page.screenshot({ path: 'test-results/login-flow-before-submit.png' });

  // When: submit the login form
  const submitButton = page
    .locator(
      [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Sign in")',
        'button:has-text("Log in")',
      ].join(', '),
    )
    .first();
  await submitButton.waitFor({ state: 'visible', timeout: 15_000 });
  await submitButton.click();

  // Then: redirected back to Backstage
  await page.waitForURL(
    (url) => url.href.includes(new URL(BACKSTAGE_URL).hostname),
    { timeout: 30_000 },
  );

  // Then: main screen is visible
  const landingIndicator = page
    .locator(
      [
        'text="Welcome"',
        '[data-testid="user-settings-menu"]',
        'text="Platform Overview"',
        'text="OpenChoreo"',
      ].join(', '),
    )
    .first();

  await landingIndicator.waitFor({ state: 'visible', timeout: 15_000 });
  await page.screenshot({ path: 'test-results/login-flow-success.png' });
  await expect(landingIndicator).toBeVisible();
}
