import { Page, expect } from "@playwright/test";

const BACKSTAGE_URL =
  process.env.BACKSTAGE_URL || "https://openchoreo.local:8443";

/** Navigate to a sidebar item and wait for content to load */
export async function navigateToSidebar(page: Page, label: string) {
  await page.click(`nav >> text="${label}"`);
  await page.waitForLoadState("networkidle");
}

/** Navigate to a specific project entity page */
export async function navigateToProject(page: Page, projectName: string) {
  await page.goto(`${BACKSTAGE_URL}/catalog/default/project/${projectName}`);
  await page.waitForLoadState("networkidle");
  await waitForContentLoaded(page);
}

/** Navigate to a specific component entity page */
export async function navigateToComponent(
  page: Page,
  componentName: string
) {
  await page.goto(
    `${BACKSTAGE_URL}/catalog/default/component/${componentName}`
  );
  await page.waitForLoadState("networkidle");
  await waitForContentLoaded(page);
}

/** Click a tab by its text label and wait for content to load */
export async function clickTab(page: Page, tabLabel: string) {
  const tab = page
    .locator(
      `[role="tab"]:has-text("${tabLabel}"), button:has-text("${tabLabel}")`
    )
    .first();
  await expect(tab).toBeVisible({ timeout: 10000 });
  await tab.click();
  await page.waitForLoadState("networkidle");
  // Small delay for React to render tab panel content
  await page.waitForTimeout(500);
}

/**
 * Click a tab if visible (for feature-flag-dependent tabs like Logs, Metrics).
 * Returns true if tab was clicked, false if not visible.
 */
export async function clickTabIfVisible(
  page: Page,
  tabLabel: string
): Promise<boolean> {
  const tab = page.locator(`[role="tab"]:has-text("${tabLabel}")`).first();
  const isVisible = await tab
    .isVisible({ timeout: 5000 })
    .catch(() => false);
  if (!isVisible) {
    return false;
  }
  await tab.click();
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  return true;
}

/** Assert no error banner/alert is shown on the page */
export async function assertNoErrorBanner(page: Page) {
  const errorBanner = page.locator(
    '[class*="MuiAlert-standardError"], [class*="MuiAlert-filledError"]'
  );
  const count = await errorBanner.count();
  if (count > 0) {
    const text = await errorBanner.first().textContent();
    throw new Error(`Error banner visible on page: ${text}`);
  }
}

/** Wait for loading spinners and progress bars to disappear */
export async function waitForContentLoaded(page: Page) {
  await page
    .locator('[class*="MuiCircularProgress"], [role="progressbar"]')
    .first()
    .waitFor({ state: "hidden", timeout: 30000 })
    .catch(() => {
      // OK if spinner was never shown
    });
}

/** Get the active tab panel content */
export function getTabPanel(page: Page) {
  return page.locator('[role="tabpanel"], main').first();
}
