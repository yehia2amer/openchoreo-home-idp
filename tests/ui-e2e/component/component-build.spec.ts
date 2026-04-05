import { test, expect } from "@playwright/test";
import {
  navigateToComponent,
  clickTab,
  clickTabIfVisible,
  assertNoErrorBanner,
  waitForContentLoaded,
  getTabPanel,
} from "../helpers/navigation";

// Only buildable components (not nats/postgres which are pre-built)
const BUILDABLE = (
  process.env.TEST_BUILDABLE_COMPONENTS || "frontend,document-svc,collab-svc"
).split(",");

for (const component of BUILDABLE) {
  test.describe(`Component "${component}" — Build Tab`, () => {
    test("build tab loads without error", async ({ page }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "BUILD");
      if (!tabExists) {
        test.skip(); // Workflow plane not enabled
        return;
      }
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
    });

    test("build tab shows workflow run history", async ({ page }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "BUILD");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);

      await expect(
        page
          .locator('table, [class*="Table"]')
          .or(page.locator("text=Succeeded"))
          .or(page.locator("text=Failed"))
          .or(page.locator("text=No builds"))
          .or(page.locator("text=No workflow runs"))
      ).toBeVisible({ timeout: 15000 });
    });
  });
}
