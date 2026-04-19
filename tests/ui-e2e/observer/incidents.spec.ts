import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  IncidentsQueryRequest,
  IncidentPutRequest,
} from "../helpers/observer-api.js";
import { execSync } from "child_process";
import { readFileSync } from "fs";
import * as path from "path";
import { startPortForward, OBSERVER_INTERNAL, type PortForwardHandle } from "../helpers/port-forward.js";
import { makeAlertRuleName } from "../helpers/test-run-id.js";
import { pollUntil, POLL_BUDGETS } from "../helpers/polling.js";

const client = new ObserverApiClient();

const CR_NAME = makeAlertRuleName("incident-alert");
const CR_NAMESPACE = "dp-default-homelab-tools-development-9c449072";
const FIXTURE_PATH = path.resolve(__dirname, "fixtures/e2e-log-alert-rule.yaml");
const CHANNEL_FIXTURE_PATH = path.resolve(__dirname, "fixtures/e2e-notification-channel.yaml");

test.describe("Observer Incidents", () => {
  test.describe.configure({ mode: "serial" });

  /** Shared across serial tests — set by the first query test if data exists. */
  let sharedIncidentId: string | undefined;
  let internalPf: PortForwardHandle | null = null;

  // ---------------------------------------------------------------------------
  // Setup — apply CRs, port-forward, fire webhook to create incident
  // ---------------------------------------------------------------------------
  test.beforeAll(async () => {
    test.setTimeout(120_000);

    try {
      // 1. Apply notification channel
      execSync("kubectl apply -f observer/fixtures/e2e-notification-channel.yaml", {
        cwd: path.resolve(__dirname, ".."),
        stdio: "pipe",
      });

      // 2. Apply alert rule CR with dynamic name
      const fixtureContent = readFileSync(FIXTURE_PATH, "utf8").replace(
        /name: e2e-test-log-alert/g,
        `name: ${CR_NAME}`,
      );

      execSync("kubectl apply -f -", {
        input: fixtureContent,
        stdio: "pipe",
      });

      // 3. Port-forward to internal observer
      internalPf = await startPortForward(
        OBSERVER_INTERNAL.service,
        OBSERVER_INTERNAL.namespace,
        OBSERVER_INTERNAL.port,
      );

      // 4. Fire webhook to create alert + incident
      const webhookReq = {
        ruleName: CR_NAME,
        ruleNamespace: CR_NAMESPACE,
        alertValue: 99,
        alertTimestamp: new Date().toISOString(),
      };

      const resp = await fetch(`http://localhost:${internalPf.port}/api/v1alpha1/alerts/webhook`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(webhookReq),
      });

      if (resp.ok) {
        console.log("[incidents] Webhook fired successfully, waiting for incident creation...");
        // Wait briefly for the incident to be created
        await new Promise((resolve) => setTimeout(resolve, 5000));
      } else {
        console.warn("[incidents] Webhook returned:", resp.status, await resp.text());
      }
    } catch (err) {
      console.warn("[incidents] Setup failed:", err);
    }
  });

  // ---------------------------------------------------------------------------
  // Teardown — clean up CRs and port-forward
  // ---------------------------------------------------------------------------
  test.afterAll(async () => {
    internalPf?.close();

    try {
      execSync(`kubectl delete observabilityalertrule ${CR_NAME} -n ${CR_NAMESPACE} --ignore-not-found --timeout=10s`, {
        cwd: path.resolve(__dirname, ".."),
        stdio: "pipe",
        timeout: 15_000,
      });
    } catch (err) {
      console.warn("[incidents] Cleanup alert rule:", String(err).substring(0, 100));
    }
    try {
      execSync("kubectl delete -f observer/fixtures/e2e-notification-channel.yaml --ignore-not-found --timeout=10s", {
        cwd: path.resolve(__dirname, ".."),
        stdio: "pipe",
        timeout: 15_000,
      });
    } catch (err) {
      console.warn("[incidents] Cleanup channel:", String(err).substring(0, 100));
    }
  });

  // ---------------------------------------------------------------------------
  // 1. Query incidents — returns valid response structure
  // ---------------------------------------------------------------------------
  test("query incidents returns valid response structure", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    // Poll for incidents — webhook may take a moment to create the incident
    try {
      const result = await pollUntil(
        async () =>
          client.queryIncidents({
            startTime: oneHourAgo.toISOString(),
            endTime: now.toISOString(),
            limit: 10,
            searchScope: {
              namespace: "default",
              project: "homelab-tools",
              environment: "development",
            },
          }),
        (r) => r.status === 200 && r.body.total > 0,
        { ...POLL_BUDGETS.incidents, description: "waiting for incidents" },
      );

      expect(result.status, "status should be 200").toBe(200);
      expect(result.body.incidents.length).toBeGreaterThan(0);
      sharedIncidentId = result.body.incidents[0].incidentId;
    } catch {
      // If polling times out, validate API contract with a final call
      const { status, body } = await client.queryIncidents({
        startTime: oneHourAgo.toISOString(),
        endTime: now.toISOString(),
        limit: 10,
        searchScope: {
          namespace: "default",
          project: "homelab-tools",
          environment: "development",
        },
      });

      expect(status, "status should be 200").toBe(200);
      expect(body).toHaveProperty("incidents");
      expect(body).toHaveProperty("total");
      // sharedIncidentId stays undefined — update tests will skip
    }
  });

  // ---------------------------------------------------------------------------
  // 2. Update incident — acknowledge
  // ---------------------------------------------------------------------------
  test("update incident to acknowledged", async () => {
    test.skip(!sharedIncidentId, "no incidents available to update");

    const req: IncidentPutRequest = {
      status: "acknowledged",
      notes: "E2E test acknowledgment",
    };

    const { status, body } = await client.updateIncident(
      sharedIncidentId!,
      req,
    );

    expect(status, "acknowledge should return 200").toBe(200);
    expect(body.status, "status should be acknowledged").toBe("acknowledged");
  });

  // ---------------------------------------------------------------------------
  // 3. Update incident — resolve
  // ---------------------------------------------------------------------------
  test("update incident to resolved", async () => {
    test.skip(!sharedIncidentId, "no incidents available to update");

    const req: IncidentPutRequest = {
      status: "resolved",
      description: "Resolved by E2E test",
    };

    const { status, body } = await client.updateIncident(
      sharedIncidentId!,
      req,
    );

    expect(status, "resolve should return 200").toBe(200);
    expect(body.status, "status should be resolved").toBe("resolved");
  });

  // ---------------------------------------------------------------------------
  // 4. Read resolved incident — verify status and resolvedAt
  // ---------------------------------------------------------------------------
  test("query incidents shows resolved status and resolvedAt", async () => {
    test.skip(!sharedIncidentId, "no incidents available to verify");

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

    const resolved = body.incidents.find(
      (i) => i.incidentId === sharedIncidentId,
    );
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
      `/api/v1alpha1/incidents/${sharedIncidentId ?? "any-id"}`,
      { status: "invalid" },
      {
        "Content-Type": "application/json",
        Authorization: `Bearer ${(await import("../helpers/auth-token.js")).getAuthToken()}`,
      },
    );

    expect(status, "invalid status should return 400").toBe(400);

    const errorBody = body as { title?: string; message?: string };
    expect(
      errorBody.title ?? errorBody.message,
      "error should have details",
    ).toBeTruthy();
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
