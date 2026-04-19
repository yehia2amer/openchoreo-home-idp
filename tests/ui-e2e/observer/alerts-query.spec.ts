import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  AlertsQueryRequest,
} from "../helpers/observer-api.js";

const client = new ObserverApiClient();

test.describe("Observer Alerts Query", () => {
  // ---------------------------------------------------------------------------
  // 1. Happy path — query returns valid response structure
  // ---------------------------------------------------------------------------
  test("query alerts returns valid response structure", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1_000);

    const { status, body } = await client.queryAlerts({
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
    expect(body).toHaveProperty("alerts");
    expect(body).toHaveProperty("total");
    expect(body).toHaveProperty("tookMs");
    expect(Array.isArray(body.alerts), "alerts should be an array").toBe(true);
    expect(typeof body.total, "total should be a number").toBe("number");

    // If alerts exist, validate structure
    if (body.alerts.length > 0) {
      const alert = body.alerts[0];
      expect(alert, "alert should have timestamp").toHaveProperty("timestamp");
      expect(alert, "alert should have alertId").toHaveProperty("alertId");
    }
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
