import { test, expect } from "@playwright/test";
import { waitForContentLoaded } from "../helpers/navigation";

test.describe("Create — Scaffolder Templates", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/create");
    await waitForContentLoaded(page);
  });

  test("scaffolder page loads with template cards", async ({ page }) => {
    await expect(
      page
        .locator(
          '[class*="TemplateCard"], [class*="template"], [class*="Card"]'
        )
        .first()
        .or(page.locator("text=Choose"))
    ).toBeVisible({ timeout: 15000 });
  });

  test("scaffolder shows component creation options", async ({ page }) => {
    await expect(
      page
        .locator("text=Component")
        .or(page.locator("text=Service"))
        .or(page.locator("text=Create"))
    ).toBeVisible({ timeout: 10000 });
  });
});
