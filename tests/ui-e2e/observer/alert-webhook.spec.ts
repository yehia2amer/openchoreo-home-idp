import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type { AlertWebhookRequest } from "../helpers/observer-api.js";
import { readFileSync } from "fs";
import { execSync } from "child_process";
import * as path from "path";
import { makeAlertRuleName } from "../helpers/test-run-id.js";
import { startPortForward, OBSERVER_INTERNAL, type PortForwardHandle } from "../helpers/port-forward.js";

const client = new ObserverApiClient();

const CR_NAME = makeAlertRuleName("webhook-alert");
const CR_NAMESPACE = "dp-default-homelab-tools-development-9c449072";
const FIXTURE_PATH = path.resolve(
  __dirname,
  "fixtures/e2e-log-alert-rule.yaml",
);

// Alert webhook endpoint is on the Observer internal port (8081) only.
// It receives alerts from Alertmanager/control plane, not from external clients.
// See: cmd/observer/main.go - internalRoutes registers webhook on :8081
test.describe("Observer Alert Webhook", () => {
  test.describe.configure({ mode: "serial" });

  let internalClient: ObserverApiClient;
  let portForward: PortForwardHandle;

  // ---------------------------------------------------------------------------
  // Setup — port-forward + apply the ObservabilityAlertRule CR from the fixture
  // ---------------------------------------------------------------------------
  test.beforeAll(async () => {
    test.setTimeout(120_000);
    portForward = await startPortForward(
      OBSERVER_INTERNAL.service,
      OBSERVER_INTERNAL.namespace,
      OBSERVER_INTERNAL.port,
    );
    internalClient = new ObserverApiClient(`http://localhost:${portForward.port}`);

    try {
      execSync("kubectl apply -f observer/fixtures/e2e-notification-channel.yaml", {
        cwd: path.resolve(__dirname, ".."),
        stdio: "pipe",
      });

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

  test.afterAll(async () => {
    portForward?.close();

    try {
      execSync(`kubectl delete observabilityalertrule ${CR_NAME} -n ${CR_NAMESPACE} --ignore-not-found --timeout=10s`, {
        cwd: path.resolve(__dirname, ".."),
        stdio: "pipe",
        timeout: 15_000,
      });
    } catch (error) {
      console.warn("Cleanup warning: alert rule:", String(error).substring(0, 100));
    }

    try {
      execSync("kubectl delete -f observer/fixtures/e2e-notification-channel.yaml --ignore-not-found --timeout=10s", {
        cwd: path.resolve(__dirname, ".."),
        stdio: "pipe",
        timeout: 15_000,
      });
    } catch (error) {
      console.warn("Cleanup warning: channel:", String(error).substring(0, 100));
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

    const { status, body } = await internalClient.sendAlertWebhook(req);

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
    const { status, body } = await internalClient.rawRequest(
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

    const { status } = await internalClient.sendAlertWebhook(req);

    expect(
      status >= 400,
      `missing ruleName should return 4xx error, got ${status}`,
    ).toBe(true);
  });
});
