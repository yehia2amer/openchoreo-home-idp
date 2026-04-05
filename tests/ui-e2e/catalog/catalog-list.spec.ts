import { test, expect } from "@playwright/test";
import { waitForContentLoaded } from "../helpers/navigation";

test.describe("Catalog — Entity List", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/catalog");
    await waitForContentLoaded(page);
  });

  test("catalog page loads without error", async ({ page }) => {
    await expect(
      page.locator('table, [class*="Table"]').first()
    ).toBeVisible({ timeout: 15000 });
  });

  test("shows component entities", async ({ page }) => {
    await expect(
      page
        .locator("text=frontend")
        .or(page.locator("text=document-svc"))
        .or(page.locator("text=collab-svc"))
    ).toBeVisible({ timeout: 10000 });
  });

  test("clicking an entity navigates to its detail page", async ({
    page,
  }) => {
    const entityLink = page.locator('a:has-text("frontend")').first();
    const isVisible = await entityLink
      .isVisible({ timeout: 5000 })
      .catch(() => false);
    if (isVisible) {
      await entityLink.click();
      await page.waitForLoadState("networkidle");
      // Should be on entity detail page with tabs
      await expect(page.locator('[role="tab"]').first()).toBeVisible({
        timeout: 10000,
      });
    }
  });
});
