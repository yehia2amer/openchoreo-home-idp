import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  AlertsQueryRequest,
} from "../helpers/observer-api.js";
import { readFileSync } from "fs";
import { pollUntil, POLL_BUDGETS } from "../helpers/polling.js";
import { execSync } from "child_process";
import * as path from "path";
import { makeAlertRuleName } from "../helpers/test-run-id.js";

const client = new ObserverApiClient();

const CR_NAME = makeAlertRuleName("query-alert");
const CR_NAMESPACE = "oc-system-homelab-tools-development";
const FIXTURE_PATH = path.resolve(
  __dirname,
  "fixtures/e2e-log-alert-rule.yaml",
);

// SKIP: Depends on webhook which returns 404 on GKE. Namespace oc-system-homelab-tools-development doesn't exist yet.
test.describe.skip("Observer Alerts Query", () => {
  test.describe.configure({ mode: "serial" });

  // ---------------------------------------------------------------------------
  // Setup — apply CR and fire webhook so there is at least one alert record
  // ---------------------------------------------------------------------------
  test.beforeAll(async () => {
    // 1. Apply the ObservabilityAlertRule CR
    try {
      const fixtureContent = readFileSync(FIXTURE_PATH, "utf8").replace(
        /name: e2e-test-log-alert/g,
        `name: ${CR_NAME}`,
      );

      execSync(`kubectl apply -f -`, {
        input: fixtureContent,
        stdio: "pipe",
      });
    } catch (error) {
      console.warn("Failed to apply ObservabilityAlertRule CR:", error);
    }

    // 2. Fire the webhook to create an alert record
    const { status } = await client.sendAlertWebhook({
      ruleName: CR_NAME,
      ruleNamespace: CR_NAMESPACE,
      alertValue: 99,
      alertTimestamp: new Date().toISOString(),
    });

    if (status !== 200) {
      console.warn(`Webhook returned status ${status} during setup`);
    }

    // 3. Brief wait for the alert to be stored
    await new Promise((resolve) => setTimeout(resolve, 2_000));
  });

  // ---------------------------------------------------------------------------
  // Cleanup — delete the CR
  // ---------------------------------------------------------------------------
  test.afterAll(async () => {
    try {
      execSync(
        `kubectl delete observabilityalertrule ${CR_NAME} -n ${CR_NAMESPACE} --ignore-not-found`,
        {
        stdio: "pipe",
        },
      );
    } catch (error) {
      console.warn("Cleanup warning:", error);
    }
  });

  // ---------------------------------------------------------------------------
  // 1. Happy path — query returns alert data from webhook
  // ---------------------------------------------------------------------------
  test("query alerts returns alert data created by webhook", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    const req: AlertsQueryRequest = {
      startTime: oneHourAgo.toISOString(),
      endTime: now.toISOString(),
      limit: 50,
      sortOrder: "desc",
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    // Poll until at least one alert appears
    const { body } = await pollUntil(
      () => client.queryAlerts(req),
      (res) => res.body.total > 0,
      { ...POLL_BUDGETS.alerts, description: "waiting for alert to appear" },
    );

    expect(body.total, "total should be > 0").toBeGreaterThan(0);
    expect(body.alerts.length, "alerts array should have items").toBeGreaterThan(
      0,
    );
    expect(typeof body.tookMs, "tookMs should be a number").toBe("number");

    const alert = body.alerts[0];
    expect(alert.timestamp, "alert should have timestamp").toBeTruthy();
    expect(alert.alertId, "alert should have alertId").toBeTruthy();
    expect(
      alert.alertValue !== undefined,
      "alert should have alertValue",
    ).toBe(true);

    // Verify metadata.alertRule has name
    expect(
      alert.metadata?.alertRule?.name,
      "alertRule should have name",
    ).toBeTruthy();
  });

  // ---------------------------------------------------------------------------
  // 2. Filter by namespace — query with specific namespace in searchScope
  // ---------------------------------------------------------------------------
  test("query alerts with specific namespace returns 200", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    const req: AlertsQueryRequest = {
      startTime: oneHourAgo.toISOString(),
      endTime: now.toISOString(),
      limit: 10,
      searchScope: {
        namespace: "default",
      },
    };

    const { status, body } = await client.queryAlerts(req);

    expect(status, "status should be 200").toBe(200);
    expect(Array.isArray(body.alerts), "alerts should be an array").toBe(true);
    expect(typeof body.total, "total should be a number").toBe("number");
    expect(typeof body.tookMs, "tookMs should be a number").toBe("number");
  });

  // ---------------------------------------------------------------------------
  // 3. Empty result — query with epoch time range returns no alerts
  // ---------------------------------------------------------------------------
  test("query alerts with epoch time range returns empty result", async () => {
    const req: AlertsQueryRequest = {
      startTime: "1970-01-01T00:00:00Z",
      endTime: "1970-01-01T00:00:01Z",
      limit: 10,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryAlerts(req);

    expect(status, "status should be 200").toBe(200);
    expect(body.alerts, "alerts should be empty array").toEqual([]);
    expect(body.total, "total should be 0").toBe(0);
  });

  // ---------------------------------------------------------------------------
  // 4. Validation error — missing searchScope.namespace returns 400
  // ---------------------------------------------------------------------------
  test("query alerts without namespace returns 400", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    // Send a request with empty namespace to trigger validation error
    const { status, body } = await client.queryAlerts({
      startTime: oneHourAgo.toISOString(),
      endTime: now.toISOString(),
      searchScope: { namespace: "" },
    } as AlertsQueryRequest);

    expect(status, "missing namespace should return 400").toBe(400);

    // Verify ErrorResponse shape
    const errorBody = body as unknown as { title: string; message?: string };
    expect(errorBody.title, "error should have title").toBeTruthy();
  });
});
