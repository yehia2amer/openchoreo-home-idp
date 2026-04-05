import { test, expect } from "@playwright/test";
import {
  navigateToProject,
  clickTab,
  clickTabIfVisible,
  assertNoErrorBanner,
  waitForContentLoaded,
  getTabPanel,
} from "../helpers/navigation";

const PROJECT = process.env.TEST_PROJECT || "doclet";

test.describe(`Project "${PROJECT}" — Overview Tab`, () => {
  test("project page loads with entity header", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await expect(page.locator(`text=${PROJECT}`).first()).toBeVisible();
    await expect(
      page
        .locator("text=PROJECT")
        .or(page.locator('[class*="EntityTypeBadge"]'))
    ).toBeVisible();
  });

  test("overview tab shows project metadata", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, "OVERVIEW");
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);
    await expect(getTabPanel(page)).not.toBeEmpty();
  });

  test("shows namespace and project selectors", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await expect(
      page.locator("text=namespaces").or(page.locator("text=projects"))
    ).toBeVisible({ timeout: 10000 });
  });
});

test.describe(`Project "${PROJECT}" — Definition Tab`, () => {
  test("definition tab shows YAML content", async ({ page }) => {
    await navigateToProject(page, PROJECT);
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

test.describe(`Project "${PROJECT}" — Cell Diagram Tab`, () => {
  test("cell diagram tab renders the cell boundary", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, "CELL DIAGRAM");
    await waitForContentLoaded(page);

    await expect(
      page
        .locator('svg, canvas, [class*="diagram"], [class*="cell"]')
        .first()
    ).toBeVisible({ timeout: 20000 });
  });

  test("cell diagram shows component nodes", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, "CELL DIAGRAM");
    await waitForContentLoaded(page);

    await expect(
      page
        .locator("text=frontend")
        .or(page.locator("text=document-svc"))
    ).toBeVisible({ timeout: 15000 });
  });

  test("cell diagram has non-trivial size", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, "CELL DIAGRAM");
    await waitForContentLoaded(page);

    const diagram = page
      .locator('svg, canvas, [class*="diagram"]')
      .first();
    const box = await diagram.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeGreaterThan(100);
    expect(box!.height).toBeGreaterThan(100);
  });
});

test.describe(`Project "${PROJECT}" — Diagram Tab`, () => {
  test("entity relationships diagram renders", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, "DIAGRAM");
    await waitForContentLoaded(page);

    await expect(
      page
        .locator(
          'svg, canvas, [class*="diagram"], [class*="EntityRelations"]'
        )
        .first()
    ).toBeVisible({ timeout: 20000 });
  });
});

test.describe(`Project "${PROJECT}" — Logs Tab`, () => {
  test("logs tab loads without error (if observability enabled)", async ({
    page,
  }) => {
    await navigateToProject(page, PROJECT);
    const tabExists = await clickTabIfVisible(page, "LOGS");
    if (!tabExists) {
      test.skip();
      return;
    }
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);
    await expect(getTabPanel(page)).not.toBeEmpty();
  });
});

test.describe(`Project "${PROJECT}" — Traces Tab`, () => {
  test("traces tab loads without error (if observability enabled)", async ({
    page,
  }) => {
    await navigateToProject(page, PROJECT);
    const tabExists = await clickTabIfVisible(page, "TRACES");
    if (!tabExists) {
      test.skip();
      return;
    }
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);
    await expect(getTabPanel(page)).not.toBeEmpty();
  });
});

test.describe(`Project "${PROJECT}" — Incidents Tab`, () => {
  test("incidents tab loads without error (if observability enabled)", async ({
    page,
  }) => {
    await navigateToProject(page, PROJECT);
    const tabExists = await clickTabIfVisible(page, "INCIDENTS");
    if (!tabExists) {
      test.skip();
      return;
    }
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);
    await expect(getTabPanel(page)).not.toBeEmpty();
  });

  test("incidents tab shows table or empty state", async ({ page }) => {
    await navigateToProject(page, PROJECT);
    const tabExists = await clickTabIfVisible(page, "INCIDENTS");
    if (!tabExists) {
      test.skip();
      return;
    }
    await waitForContentLoaded(page);

    await expect(
      page
        .locator('table, [class*="Table"]')
        .or(page.locator("text=No incidents"))
        .or(page.locator("text=no data"))
    ).toBeVisible({ timeout: 15000 });
  });
});

test.describe(`Project "${PROJECT}" — RCA Reports Tab`, () => {
  test("RCA reports tab loads without error (if observability enabled)", async ({
    page,
  }) => {
    await navigateToProject(page, PROJECT);
    const tabExists = await clickTabIfVisible(page, "RCA REPORTS");
    if (!tabExists) {
      test.skip();
      return;
    }
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);
    await expect(getTabPanel(page)).not.toBeEmpty();
  });
});
