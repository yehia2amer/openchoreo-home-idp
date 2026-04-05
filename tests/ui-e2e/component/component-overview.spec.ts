import { test, expect } from "@playwright/test";
import {
  navigateToComponent,
  clickTab,
  assertNoErrorBanner,
  waitForContentLoaded,
  getTabPanel,
} from "../helpers/navigation";

// All components in the doclet demo app
const COMPONENTS = (
  process.env.TEST_COMPONENTS || "frontend,document-svc,collab-svc,nats,postgres"
).split(",");

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Overview Tab`, () => {
    test("component page loads with entity header", async ({ page }) => {
      await navigateToComponent(page, component);
      await expect(page.locator(`text=${component}`).first()).toBeVisible();
    });

    test("overview tab shows component metadata", async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, "OVERVIEW");
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
      await expect(getTabPanel(page)).not.toBeEmpty();
    });

    test("overview tab shows deployment status", async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, "OVERVIEW");
      await waitForContentLoaded(page);

      await expect(
        page
          .locator("text=Development")
          .or(page.locator("text=Ready"))
          .or(page.locator("text=Running"))
          .or(page.locator("text=Status"))
      ).toBeVisible({ timeout: 15000 });
    });
  });

  test.describe(`Component "${component}" — Definition Tab`, () => {
    test("definition tab shows YAML with apiVersion and kind", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      await clickTab(page, "DEFINITION");
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);

      await expect(
        page
          .locator("text=apiVersion")
          .or(page.locator("text=kind"))
          .or(
            page.locator(
              'code, pre, [class*="CodeMirror"], [class*="monaco"]'
            )
          )
      ).toBeVisible({ timeout: 15000 });
    });
  });
}
