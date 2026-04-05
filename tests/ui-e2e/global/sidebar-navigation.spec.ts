import { test, expect } from "@playwright/test";
import { navigateToSidebar } from "../helpers/navigation";

test.describe("Sidebar Navigation", () => {
  test("Home link navigates to platform overview", async ({ page }) => {
    await page.goto("/");
    await navigateToSidebar(page, "Home");
    await expect(page.locator("text=Platform Overview")).toBeVisible();
  });

  test("Catalog link navigates to catalog page", async ({ page }) => {
    await page.goto("/");
    await navigateToSidebar(page, "Catalog");
    await expect(page).toHaveURL(/catalog/);
  });

  test("Platform link navigates to platform topology", async ({ page }) => {
    await page.goto("/");
    await navigateToSidebar(page, "Platform");
    await expect(page).toHaveURL(/platform/);
    await expect(
      page.locator("text=Platform Overview").or(page.locator("text=Scope"))
    ).toBeVisible({ timeout: 15000 });
  });

  test("APIs link navigates to API catalog", async ({ page }) => {
    await page.goto("/");
    await navigateToSidebar(page, "APIs");
    await expect(page).toHaveURL(/api/);
  });

  test("Create link navigates to scaffolder", async ({ page }) => {
    await page.goto("/");
    await navigateToSidebar(page, "Create");
    await expect(page).toHaveURL(/create/);
  });
});
