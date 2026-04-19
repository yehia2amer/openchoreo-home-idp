import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  IncidentsQueryRequest,
  IncidentPutRequest,
} from "../helpers/observer-api.js";

const client = new ObserverApiClient();

test.describe("Observer Incidents", () => {
  test.describe.configure({ mode: "serial" });

  /** Shared across serial tests — set by the first query test if data exists. */
  let sharedIncidentId: string | undefined;

  // ---------------------------------------------------------------------------
  // 1. Query incidents — returns valid response structure
  // ---------------------------------------------------------------------------
  test("query incidents returns valid response structure", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

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
    expect(body).toHaveProperty("tookMs");
    expect(Array.isArray(body.incidents), "incidents should be an array").toBe(
      true,
    );

    // Store incidentId if any exist, for update tests
    if (body.incidents.length > 0) {
      sharedIncidentId = body.incidents[0].incidentId;
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
