import { test, expect } from "@playwright/test";

test.describe("Home Page — Platform Overview", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("shows welcome header with user identity", async ({ page }) => {
    await expect(page.locator("text=Welcome")).toBeVisible();
  });

  test("shows Infrastructure card with data planes count", async ({
    page,
  }) => {
    await expect(page.locator("text=Infrastructure")).toBeVisible();
    await expect(page.locator("text=Data planes connected")).toBeVisible();
  });

  test("shows Environments count", async ({ page }) => {
    await expect(page.locator("text=Environments")).toBeVisible();
  });

  test("shows Developer Portal card with projects and components", async ({
    page,
  }) => {
    await expect(page.locator("text=Developer Portal")).toBeVisible();
    await expect(page.locator("text=Projects created")).toBeVisible();
    await expect(page.locator("text=Components deployed")).toBeVisible();
  });

  test("shows Platform Details with DataPlane and environment cards", async ({
    page,
  }) => {
    await expect(page.locator("text=Platform Details")).toBeVisible();
    // Should show at least the Development environment
    await expect(page.locator("text=Development")).toBeVisible();
  });

  test("environment cards show components count", async ({ page }) => {
    const devCard = page
      .locator(':has-text("Development")')
      .filter({ hasText: "Components" });
    await expect(devCard.first()).toBeVisible();
  });
});
