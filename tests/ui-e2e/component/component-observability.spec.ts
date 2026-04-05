import { test, expect } from "@playwright/test";
import {
  navigateToComponent,
  clickTabIfVisible,
  assertNoErrorBanner,
  waitForContentLoaded,
  getTabPanel,
} from "../helpers/navigation";

const COMPONENTS = (
  process.env.TEST_COMPONENTS || "frontend,document-svc,collab-svc"
).split(",");

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Logs Tab`, () => {
    test("logs tab loads without error (if observability enabled)", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "LOGS");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
      await expect(getTabPanel(page)).not.toBeEmpty();
    });

    test("logs tab shows log viewer or search interface", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "LOGS");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);

      await expect(
        page
          .locator('input[placeholder*="search" i]')
          .or(page.locator('[class*="log" i]'))
          .or(page.locator("text=No logs"))
          .or(page.locator("pre, code"))
          .or(page.locator("text=Environment"))
      ).toBeVisible({ timeout: 15000 });
    });
  });

  test.describe(`Component "${component}" — Metrics Tab`, () => {
    test("metrics tab loads without error (if observability enabled)", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "METRICS");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
      await expect(getTabPanel(page)).not.toBeEmpty();
    });

    test("metrics tab shows graphs or no-metrics message", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "METRICS");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);

      await expect(
        page
          .locator('svg[class*="chart" i], canvas, [class*="Chart"]')
          .or(page.locator("text=No metrics"))
          .or(page.locator("text=CPU"))
          .or(page.locator("text=Memory"))
          .or(page.locator("text=Requests"))
      ).toBeVisible({ timeout: 20000 });
    });
  });

  test.describe(`Component "${component}" — Alerts Tab`, () => {
    test("alerts tab loads without error (if observability enabled)", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "ALERTS");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
      await expect(getTabPanel(page)).not.toBeEmpty();
    });

    test("alerts tab shows alert rules or empty state", async ({
      page,
    }) => {
      await navigateToComponent(page, component);
      const tabExists = await clickTabIfVisible(page, "ALERTS");
      if (!tabExists) {
        test.skip();
        return;
      }
      await waitForContentLoaded(page);

      await expect(
        page
          .locator('table, [class*="Table"]')
          .or(page.locator("text=No alerts"))
          .or(page.locator("text=No alert rules"))
          .or(page.locator("text=Alert"))
      ).toBeVisible({ timeout: 15000 });
    });
  });
}
