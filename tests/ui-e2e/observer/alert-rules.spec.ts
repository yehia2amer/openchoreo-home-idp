import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type { AlertRuleRequest } from "../helpers/observer-api.js";
import { makeAlertRuleName } from "../helpers/test-run-id.js";

const client = new ObserverApiClient();

// Placeholder UUIDs — the backend does not validate their existence
const PLACEHOLDER_PROJECT_UID = "00000000-0000-0000-0000-000000000001";
const PLACEHOLDER_ENV_UID = "00000000-0000-0000-0000-000000000002";
const PLACEHOLDER_COMPONENT_UID = "00000000-0000-0000-0000-000000000003";

const logRuleName = makeAlertRuleName("log-test");
const metricRuleName = makeAlertRuleName("metric-test");

function makeLogAlertRule(
  name: string,
  overrides?: Partial<AlertRuleRequest["condition"]>,
): AlertRuleRequest {
  return {
    metadata: {
      name,
      namespace: "default",
      projectUid: PLACEHOLDER_PROJECT_UID,
      environmentUid: PLACEHOLDER_ENV_UID,
      componentUid: PLACEHOLDER_COMPONENT_UID,
    },
    source: { type: "log", query: "error" },
    condition: {
      enabled: true,
      window: "5m",
      interval: "1m",
      operator: "gt",
      threshold: 10,
      ...overrides,
    },
  };
}

function makeMetricAlertRule(name: string): AlertRuleRequest {
  return {
    metadata: {
      name,
      namespace: "default",
      projectUid: PLACEHOLDER_PROJECT_UID,
      environmentUid: PLACEHOLDER_ENV_UID,
      componentUid: PLACEHOLDER_COMPONENT_UID,
    },
    source: { type: "metric", metric: "cpu_usage" },
    condition: {
      enabled: true,
      window: "5m",
      interval: "1m",
      operator: "gt",
      threshold: 80,
    },
  };
}

// Alert rules CRUD endpoints are on the Observer internal port (8081) only.
// They are called by the control plane and Alertmanager, not exposed via the public Gateway.
// See: cmd/observer/main.go - internalRoutes registers these on :8081, publicRoutes on :8080
// To test these, you would need direct access to observer-internal:8081 service.
test.describe.skip("Observer Alert Rules CRUD", () => {
  test.describe.configure({ mode: "serial" });

  // -------------------------------------------------------------------------
  // Cleanup — runs even on failure so subsequent runs start clean
  // -------------------------------------------------------------------------
  test.afterAll(async () => {
    for (const [sourceType, name] of [
      ["log", logRuleName],
      ["metric", metricRuleName],
    ] as const) {
      try {
        await client.deleteAlertRule(sourceType, name);
      } catch (error) {
        console.warn("Cleanup warning:", error);
      }
    }
  });

  // -------------------------------------------------------------------------
  // 1. Create log alert rule
  // -------------------------------------------------------------------------
  test("create log alert rule", async () => {
    const req = makeLogAlertRule(logRuleName);
    const { status, body } = await client.createAlertRule("log", req);

    expect(
      [200, 201].includes(status),
      `create log rule should return 200 or 201, got ${status}`,
    ).toBe(true);
    expect(body.action, "action should be 'created'").toBe("created");
    expect(body.status, "status should be 'synced'").toBe("synced");
  });

  // -------------------------------------------------------------------------
  // 2. Read log alert rule
  // -------------------------------------------------------------------------
  test("read log alert rule", async () => {
    const { status, body } = await client.getAlertRule("log", logRuleName);

    expect(status, "get log rule should return 200").toBe(200);
    expect(body.metadata.name, "name should match").toBe(logRuleName);
    expect(body.metadata.namespace, "namespace should be 'default'").toBe(
      "default",
    );
    expect(body.metadata.projectUid, "projectUid should match").toBe(
      PLACEHOLDER_PROJECT_UID,
    );
    expect(body.metadata.environmentUid, "environmentUid should match").toBe(
      PLACEHOLDER_ENV_UID,
    );
    expect(body.metadata.componentUid, "componentUid should match").toBe(
      PLACEHOLDER_COMPONENT_UID,
    );
    expect(body.source.type, "source type should be 'log'").toBe("log");
    expect(body.source.query, "source query should be 'error'").toBe("error");
    expect(body.condition.threshold, "threshold should be 10").toBe(10);
    expect(body.condition.operator, "operator should be 'gt'").toBe("gt");
    expect(body.condition.enabled, "enabled should be true").toBe(true);
  });

  // -------------------------------------------------------------------------
  // 3. Update log alert rule
  // -------------------------------------------------------------------------
  test("update log alert rule", async () => {
    const req = makeLogAlertRule(logRuleName, { threshold: 20 });
    const { status, body } = await client.updateAlertRule(
      "log",
      logRuleName,
      req,
    );

    expect(
      [200, 201].includes(status),
      `update log rule should return 200 or 201, got ${status}`,
    ).toBe(true);
    expect(body.action, "action should be 'updated'").toBe("updated");
  });

  // -------------------------------------------------------------------------
  // 4. Read updated log alert rule
  // -------------------------------------------------------------------------
  test("read updated log alert rule – threshold changed", async () => {
    const { status, body } = await client.getAlertRule("log", logRuleName);

    expect(status, "get updated rule should return 200").toBe(200);
    expect(body.condition.threshold, "threshold should now be 20").toBe(20);
  });

  // -------------------------------------------------------------------------
  // 5. Create metric alert rule
  // -------------------------------------------------------------------------
  test("create metric alert rule", async () => {
    const req = makeMetricAlertRule(metricRuleName);
    const { status, body } = await client.createAlertRule("metric", req);

    expect(
      [200, 201].includes(status),
      `create metric rule should return 200 or 201, got ${status}`,
    ).toBe(true);
    expect(body.action, "action should be 'created'").toBe("created");
    expect(body.status, "status should be 'synced'").toBe("synced");
  });

  // -------------------------------------------------------------------------
  // 6. Delete both rules
  // -------------------------------------------------------------------------
  test("delete log alert rule", async () => {
    const { status, body } = await client.deleteAlertRule("log", logRuleName);

    expect(
      [200, 201].includes(status),
      `delete log rule should return 200 or 201, got ${status}`,
    ).toBe(true);
    expect(body.action, "action should be 'deleted'").toBe("deleted");
  });

  test("delete metric alert rule", async () => {
    const { status, body } = await client.deleteAlertRule(
      "metric",
      metricRuleName,
    );

    expect(
      [200, 201].includes(status),
      `delete metric rule should return 200 or 201, got ${status}`,
    ).toBe(true);
    expect(body.action, "action should be 'deleted'").toBe("deleted");
  });

  // -------------------------------------------------------------------------
  // 7. Verify deletion — GET should return 404
  // -------------------------------------------------------------------------
  test("verify log rule deleted – GET returns 404", async () => {
    const { status } = await client.getAlertRule("log", logRuleName);
    expect(status, "deleted log rule should return 404").toBe(404);
  });

  test("verify metric rule deleted – GET returns 404", async () => {
    const { status } = await client.getAlertRule("metric", metricRuleName);
    expect(status, "deleted metric rule should return 404").toBe(404);
  });

  // -------------------------------------------------------------------------
  // 8. Validation: sourceType mismatch
  // -------------------------------------------------------------------------
  test("validation – sourceType path/body mismatch returns 400", async () => {
    const req: AlertRuleRequest = {
      metadata: {
        name: makeAlertRuleName("mismatch-test"),
        namespace: "default",
        projectUid: PLACEHOLDER_PROJECT_UID,
        environmentUid: PLACEHOLDER_ENV_UID,
        componentUid: PLACEHOLDER_COMPONENT_UID,
      },
      source: { type: "metric", metric: "cpu_usage" },
      condition: {
        enabled: true,
        window: "5m",
        interval: "1m",
        operator: "gt",
        threshold: 10,
      },
    };

    // Path says "log" but body says source.type: "metric"
    const { status } = await client.createAlertRule("log", req);
    expect(
      status,
      "sourceType mismatch should return 400",
    ).toBe(400);
  });
});
