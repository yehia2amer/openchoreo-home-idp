import { test, expect } from "@playwright/test";
import {
  navigateToComponent,
  clickTab,
  assertNoErrorBanner,
  waitForContentLoaded,
} from "../helpers/navigation";

const COMPONENTS = (
  process.env.TEST_COMPONENTS || "frontend,document-svc,collab-svc,nats,postgres"
).split(",");

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Deploy Tab`, () => {
    test("deploy tab loads without error", async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, "DEPLOY");
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
    });

    test("deploy tab shows Development environment card", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      await clickTab(page, "DEPLOY");
      await waitForContentLoaded(page);

      await expect(page.locator("text=Development")).toBeVisible({
        timeout: 15000,
      });
    });

    test("development environment shows deployment status", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      await clickTab(page, "DEPLOY");
      await waitForContentLoaded(page);

      await expect(
        page
          .locator("text=Ready")
          .or(page.locator("text=NotReady"))
          .or(page.locator("text=Deployed"))
          .or(page.locator("text=Not Deployed"))
          .or(page.locator('[class*="StatusOK"]'))
      ).toBeVisible({ timeout: 15000 });
    });
  });
}
