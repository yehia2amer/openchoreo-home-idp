import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type { AlertWebhookRequest } from "../helpers/observer-api.js";
import { readFileSync } from "fs";
import { execSync } from "child_process";
import * as path from "path";
import { makeAlertRuleName } from "../helpers/test-run-id.js";

const client = new ObserverApiClient();

const CR_NAME = makeAlertRuleName("webhook-alert");
const CR_NAMESPACE = "oc-system-homelab-tools-development";
const FIXTURE_PATH = path.resolve(
  __dirname,
  "fixtures/e2e-log-alert-rule.yaml",
);

// Alert webhook endpoint is on the Observer internal port (8081) only.
// It receives alerts from Alertmanager/control plane, not from external clients.
// See: cmd/observer/main.go - internalRoutes registers webhook on :8081
test.describe.skip("Observer Alert Webhook", () => {
  test.describe.configure({ mode: "serial" });

  // ---------------------------------------------------------------------------
  // Setup — apply the ObservabilityAlertRule CR from the fixture
  // ---------------------------------------------------------------------------
  test.beforeAll(async () => {
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
      // Don't fail — the CR might already exist from a previous run
    }
  });

  // ---------------------------------------------------------------------------
  // Cleanup — delete the CR so subsequent runs start clean
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
  // 1. Happy path — webhook returns success
  // ---------------------------------------------------------------------------
  test("POST /api/v1alpha1/alerts/webhook returns success", async () => {
    const req: AlertWebhookRequest = {
      ruleName: CR_NAME,
      ruleNamespace: CR_NAMESPACE,
      alertValue: 42,
      alertTimestamp: new Date().toISOString(),
    };

    const { status, body } = await client.sendAlertWebhook(req);

    expect(status, "webhook should return 200").toBe(200);
    expect(body.status, "response status should be 'success'").toBe("success");
  });

  // ---------------------------------------------------------------------------
  // 2. No auth required — webhook is a public endpoint
  // ---------------------------------------------------------------------------
  test("webhook works without Authorization header", async () => {
    const req: AlertWebhookRequest = {
      ruleName: CR_NAME,
      ruleNamespace: CR_NAMESPACE,
      alertValue: 7,
      alertTimestamp: new Date().toISOString(),
    };

    // Use rawRequest to have full control over headers — no Authorization
    const { status, body } = await client.rawRequest(
      "POST",
      "/api/v1alpha1/alerts/webhook",
      req,
      { "Content-Type": "application/json" },
    );

    expect(status, "webhook without auth should return 200").toBe(200);
    expect(body).toHaveProperty("status");
    expect(
      (body as { status: string }).status,
      "response status should be 'success'",
    ).toBe("success");
  });

  // ---------------------------------------------------------------------------
  // 3. Missing required field — should return error
  // ---------------------------------------------------------------------------
  test("webhook with empty ruleName returns error", async () => {
    const req: AlertWebhookRequest = {
      ruleName: "",
      ruleNamespace: CR_NAMESPACE,
      alertValue: 1,
      alertTimestamp: new Date().toISOString(),
    };

    const { status } = await client.sendAlertWebhook(req);

    expect(
      status >= 400,
      `missing ruleName should return 4xx error, got ${status}`,
    ).toBe(true);
  });
});
