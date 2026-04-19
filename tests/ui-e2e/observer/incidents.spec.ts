import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  IncidentsQueryRequest,
  IncidentPutRequest,
} from "../helpers/observer-api.js";
import { readFileSync } from "fs";
import { pollUntil, POLL_BUDGETS } from "../helpers/polling.js";
import { execSync } from "child_process";
import * as path from "path";
import { makeAlertRuleName } from "../helpers/test-run-id.js";

const client = new ObserverApiClient();

const CR_NAME = makeAlertRuleName("incident-alert");
const CR_NAMESPACE = "oc-system-homelab-tools-development";
const FIXTURE_PATH = path.resolve(
  __dirname,
  "fixtures/e2e-log-alert-rule.yaml",
);

// SKIP: Depends on webhook which returns 404 on GKE. Namespace oc-system-homelab-tools-development doesn't exist yet.
test.describe.skip("Observer Incidents", () => {
  test.describe.configure({ mode: "serial" });

  /** Shared across serial tests — set by the first query test. */
  let incidentId: string | undefined;

  // ---------------------------------------------------------------------------
  // Setup — apply CR and fire webhook to trigger alert + incident creation
  // ---------------------------------------------------------------------------
  test.beforeAll(async () => {
    // 1. Apply the ObservabilityAlertRule CR (incident.enabled: true)
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

    // 2. Fire the webhook to create an alert + incident
    const { status } = await client.sendAlertWebhook({
      ruleName: CR_NAME,
      ruleNamespace: CR_NAMESPACE,
      alertValue: 99,
      alertTimestamp: new Date().toISOString(),
    });

    if (status !== 200) {
      console.warn(`Webhook returned status ${status} during setup`);
    }

    // 3. Brief wait for incident to be persisted
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
  // 1. Query incidents — poll until at least one appears
  // ---------------------------------------------------------------------------
  test("query incidents returns incident created by webhook", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    const req: IncidentsQueryRequest = {
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

    // Poll until at least one incident appears
    const { body } = await pollUntil(
      () => client.queryIncidents(req),
      (res) => res.body.total > 0,
      {
        ...POLL_BUDGETS.incidents,
        description: "waiting for incident to appear",
      },
    );

    // If polling succeeded but no incidents, skip the rest of the suite
    if (body.incidents.length === 0) {
      test.skip(true, "No incidents found — skipping incident lifecycle tests");
      return;
    }

    expect(body.total, "total should be > 0").toBeGreaterThan(0);
    expect(
      body.incidents.length,
      "incidents array should have items",
    ).toBeGreaterThan(0);
    expect(typeof body.tookMs, "tookMs should be a number").toBe("number");

    const incident = body.incidents[0];
    expect(incident.incidentId, "incident should have incidentId").toBeTruthy();
    expect(incident.status, "incident should have status").toBeTruthy();
    expect(
      incident.triggeredAt,
      "incident should have triggeredAt",
    ).toBeTruthy();
    expect(incident.labels, "incident should have labels").toBeTruthy();

    // Store for subsequent tests
    incidentId = incident.incidentId;
  });

  // ---------------------------------------------------------------------------
  // 2. Update incident — acknowledge
  // ---------------------------------------------------------------------------
  test("update incident to acknowledged", async () => {
    test.skip(!incidentId, "No incidentId from previous test — skipping");

    const req: IncidentPutRequest = {
      status: "acknowledged",
      notes: "E2E test acknowledgment",
    };

    const { status, body } = await client.updateIncident(incidentId!, req);

    expect(status, "acknowledge should return 200").toBe(200);
    expect(body.status, "status should be acknowledged").toBe("acknowledged");
  });

  // ---------------------------------------------------------------------------
  // 3. Update incident — resolve
  // ---------------------------------------------------------------------------
  test("update incident to resolved", async () => {
    test.skip(!incidentId, "No incidentId from previous test — skipping");

    const req: IncidentPutRequest = {
      status: "resolved",
      description: "Resolved by E2E test",
    };

    const { status, body } = await client.updateIncident(incidentId!, req);

    expect(status, "resolve should return 200").toBe(200);
    expect(body.status, "status should be resolved").toBe("resolved");
  });

  // ---------------------------------------------------------------------------
  // 4. Read resolved incident — verify status and resolvedAt
  // ---------------------------------------------------------------------------
  test("query incidents shows resolved status and resolvedAt", async () => {
    test.skip(!incidentId, "No incidentId from previous test — skipping");

    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    const req: IncidentsQueryRequest = {
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

    const { status, body } = await client.queryIncidents(req);

    expect(status, "query should return 200").toBe(200);

    const resolved = body.incidents.find((i) => i.incidentId === incidentId);
    expect(resolved, "resolved incident should be in results").toBeTruthy();
    expect(resolved!.status, "status should be resolved").toBe("resolved");
    expect(resolved!.resolvedAt, "resolvedAt should be set").toBeTruthy();
  });

  // ---------------------------------------------------------------------------
  // 5. Validation error — invalid status value
  // ---------------------------------------------------------------------------
  test("update incident with invalid status returns 400", async () => {
    const { status, body } = await client.rawRequest(
      "PUT",
      `/api/v1alpha1/incidents/${incidentId ?? "any-id"}`,
      { status: "invalid" },
      {
        "Content-Type": "application/json",
        Authorization: `Bearer ${(await import("../helpers/auth-token.js")).getAuthToken()}`,
      },
    );

    expect(status, "invalid status should return 400").toBe(400);

    const errorBody = body as { title?: string; message?: string };
    expect(errorBody.title ?? errorBody.message, "error should have details").toBeTruthy();
  });

  // ---------------------------------------------------------------------------
  // 6. Not found — non-existent incidentId
  // ---------------------------------------------------------------------------
  test("update non-existent incident returns 404", async () => {
    const req: IncidentPutRequest = {
      status: "acknowledged",
      notes: "Should not exist",
    };

    const { status } = await client.updateIncident(
      "non-existent-id-12345",
      req,
    );

    expect(status, "non-existent incident should return 404").toBe(404);
  });

  // ---------------------------------------------------------------------------
  // 7. Empty result — query with epoch time range
  // ---------------------------------------------------------------------------
  test("query incidents with epoch time range returns empty result", async () => {
    const req: IncidentsQueryRequest = {
      startTime: "1970-01-01T00:00:00Z",
      endTime: "1970-01-01T00:00:01Z",
      limit: 10,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryIncidents(req);

    expect(status, "status should be 200").toBe(200);
    expect(body.incidents, "incidents should be empty array").toEqual([]);
    expect(body.total, "total should be 0").toBe(0);
  });
});
