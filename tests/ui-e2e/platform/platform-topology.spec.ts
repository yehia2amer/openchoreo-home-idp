import { test, expect } from "@playwright/test";
import { waitForContentLoaded } from "../helpers/navigation";

test.describe("Platform — Topology Graph", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/platform");
    await waitForContentLoaded(page);
  });

  test("platform topology graph renders", async ({ page }) => {
    await expect(
      page
        .locator('canvas, svg, [class*="graph"], [class*="topology"]')
        .first()
    ).toBeVisible({ timeout: 20000 });
  });

  test("shows filter dropdowns (Scope, Kind, Project)", async ({ page }) => {
    await expect(
      page.locator("text=Scope").or(page.locator("text=Kind"))
    ).toBeVisible({ timeout: 10000 });
  });

  test("shows project nodes in the graph", async ({ page }) => {
    await expect(
      page.locator("text=doclet").or(page.locator("text=Default Project"))
    ).toBeVisible({ timeout: 15000 });
  });

  test("shows environment nodes in the graph", async ({ page }) => {
    await expect(page.locator("text=Development")).toBeVisible({
      timeout: 15000,
    });
  });
});
