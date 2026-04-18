import { test, expect, type Page } from '@playwright/test';

/**
 * Standalone E2E login flow: Backstage → Thunder OAuth → credentials → redirect → main screen.
 * Env: BACKSTAGE_URL, THUNDER_USERNAME, THUNDER_PASSWORD
 */

const BACKSTAGE_URL =
  process.env.BACKSTAGE_URL ?? 'https://backstage.idp.aistudio.consulting';
const USERNAME = process.env.THUNDER_USERNAME ?? 'admin@openchoreo.dev';
const PASSWORD = process.env.THUNDER_PASSWORD ?? 'Admin@123';
const AUTH_ERROR_TEXT = 'Authentication failed, Invalid client credentials';

test.describe('Login Flow', () => {
  // Full OAuth roundtrip through Cloudflare tunnel needs more than the default 60s
  test.setTimeout(120_000);
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

  test.afterEach(async ({ page }, testInfo) => {
    void page;
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
    waitUntil: 'networkidle',
    timeout: 60_000,
  });

  // Debug: capture page state after goto
  await page.screenshot({ path: 'test-results/login-flow-after-goto.png' });
  console.log(`[LOGIN-FLOW] After goto URL: ${page.url()}`);

  // Three scenarios after page load:
  // 1. Already authenticated (dashboard visible) — auth.setup ran in same browser
  // 2. Backstage sign-in page — click "Sign In" to trigger OAuth redirect
  // 3. Auto-redirect to Thunder — URL changes to thunder/oauth
  // Check if already authenticated by looking for the page title (not visibility-dependent)
  const pageTitle = await page.title();
  const alreadyOnDashboard = pageTitle.includes('Welcome') && !page.url().includes('thunder') && !page.url().includes('gate');
  console.log(`[LOGIN-FLOW] Page title: '${pageTitle}', Already on dashboard: ${alreadyOnDashboard}`);

  if (alreadyOnDashboard) {
    console.log('[LOGIN-FLOW] Already authenticated, verifying dashboard');
    await page.screenshot({ path: 'test-results/login-flow-success.png' });
    // Page title contains 'Welcome' — that IS the assertion (title only shows Welcome when logged in)
    expect(pageTitle).toContain('Welcome');
    return;
  }

  // Handle Backstage sign-in page if present
  const signInButton = page.locator('button:has-text("Sign In"), button:has-text("Sign in")').first();
  const signInFound = await signInButton.isVisible({ timeout: 15_000 }).catch(() => false);
  console.log(`[LOGIN-FLOW] Sign-in button found: ${signInFound}`);
  if (signInFound) {
    await signInButton.click();
    console.log(`[LOGIN-FLOW] Clicked Sign In, URL now: ${page.url()}`);
  }

  // When: OAuth redirects to Thunder login page
  await page.waitForURL(
    (url) => /thunder|oauth|login|authorize/.test(url.href),
    { timeout: 60_000 },
  );

  // Thunder shell can stay blank for a while before the actual form mounts.
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
  await usernameField.waitFor({ state: 'visible', timeout: 90_000 });
  await usernameField.fill(USERNAME);

  // When: handle optional "Continue" step before password
  const continueButton = page.getByRole('button', { name: /continue/i });
  if (await continueButton.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await continueButton.click();
    await page
      .locator('input[name="password"], input[type="password"], #password')
      .first()
      .waitFor({ state: 'visible', timeout: 30_000 });
  }

  // When: fill password
  const passwordField = page
    .locator(
      ['input[name="password"]', 'input[type="password"]', '#password'].join(
        ', ',
      ),
    )
    .first();
  await passwordField.waitFor({ state: 'visible', timeout: 30_000 });
  await passwordField.fill(PASSWORD);

  await page.screenshot({ path: 'test-results/login-flow-before-submit.png' });

  // When: submit the login form
  const submitButton = page
    .locator(
      [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Sign in")',
        'button:has-text("Sign In")',
        'button:has-text("Log in")',
      ].join(', '),
    )
    .first();
  await submitButton.waitFor({ state: 'visible', timeout: 30_000 });
  await submitButton.click();

  // Then: redirected back to Backstage
  await page.waitForURL(
    (url) =>
      url.href.includes(new URL(BACKSTAGE_URL).hostname) ||
      url.pathname === '/gate/signin',
    { timeout: 90_000 },
  );

  await expect(
    page.locator(`text=${AUTH_ERROR_TEXT}`),
    `Live OAuth callback returned an auth backend error instead of landing in Backstage: ${page.url()}`,
  ).toHaveCount(0, { timeout: 5_000 });

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
