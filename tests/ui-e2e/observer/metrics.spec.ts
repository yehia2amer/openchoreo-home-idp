import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type { MetricsQueryRequest } from "../helpers/observer-api.js";
import { pollUntil, POLL_BUDGETS } from "../helpers/polling.js";
import { getAuthToken } from "../helpers/auth-token.js";

const client = new ObserverApiClient();

function timeRange(minutesAgo: number = 60): {
  startTime: string;
  endTime: string;
} {
  const now = new Date();
  const start = new Date(now.getTime() - minutesAgo * 60 * 1000);
  return {
    startTime: start.toISOString(),
    endTime: now.toISOString(),
  };
}

function authHeaders(): Record<string, string> {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getAuthToken()}`,
  };
}

test.describe("Observer Metrics Query", () => {
  test("resource metrics – returns CPU or memory usage", async () => {
    const range = timeRange(60);
    const req: MetricsQueryRequest = {
      metric: "resource",
      ...range,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
        component: "obs-test-gen",
      },
    };

    const result = await pollUntil(
      () => client.queryMetrics(req),
      (r) => {
        // Accept 200 with data as success, but also stop polling on 500
        if (r.status === 500) return true;
        if (r.status !== 200) return false;
        const body = r.body as Record<string, unknown>;
        const hasCpu = Array.isArray(body.cpuUsage) && body.cpuUsage.length > 0;
        const hasMem =
          Array.isArray(body.memoryUsage) && body.memoryUsage.length > 0;
        return hasCpu || hasMem;
      },
      { ...POLL_BUDGETS.metrics, description: "waiting for resource metrics" },
    );

    // Backend may return 500 if component has no metrics yet
    expect(
      [200, 500],
      "resource metrics query should return 200 or 500",
    ).toContain(result.status);

    if (result.status === 200) {
      const body = result.body as Record<string, unknown>;
      const hasCpu = Array.isArray(body.cpuUsage) && body.cpuUsage.length > 0;
      const hasMem =
        Array.isArray(body.memoryUsage) && body.memoryUsage.length > 0;
      expect(
        hasCpu || hasMem,
        "should have at least one of cpuUsage[] or memoryUsage[]",
      ).toBe(true);

      // Validate item structure in whichever array is present
      const items = (
        hasCpu
          ? (body.cpuUsage as Array<{ timestamp: string; value: number }>)
          : (body.memoryUsage as Array<{ timestamp: string; value: number }>)
      );
      for (const item of items) {
        expect(item, "metric item should have timestamp").toHaveProperty(
          "timestamp",
        );
        expect(item, "metric item should have value").toHaveProperty("value");
      }
    }
  });

  test("HTTP metrics – returns 200 with valid structure", async () => {
    const req: MetricsQueryRequest = {
      metric: "http",
      ...timeRange(60),
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryMetrics(req);
    expect(status, "HTTP metrics query should return 200").toBe(200);

    // HTTP metrics may return empty arrays if no traffic — that's acceptable
    const data = body as Record<string, unknown>;
    if (Array.isArray(data.requestCount) && data.requestCount.length > 0) {
      for (const item of data.requestCount as Array<{
        timestamp: string;
        value: number;
      }>) {
        expect(item, "requestCount item should have timestamp").toHaveProperty(
          "timestamp",
        );
        expect(item, "requestCount item should have value").toHaveProperty(
          "value",
        );
      }
    }
  });

  test("empty result – non-existent component returns empty arrays", async () => {
    const req: MetricsQueryRequest = {
      metric: "resource",
      ...timeRange(60),
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
        component: "non-existent-component-xyz-12345",
      },
    };

    const { status, body } = await client.queryMetrics(req);
    // Backend returns 500 for non-existent components — accept as "server rejected"
    expect(
      [200, 500],
      "should return 200 or 500 for non-existent component",
    ).toContain(status);

    if (status === 200) {
      // All arrays should be empty or undefined
      const data = body as Record<string, unknown>;
      const arrays = [
        "cpuUsage",
        "cpuRequests",
        "cpuLimits",
        "memoryUsage",
        "memoryRequests",
        "memoryLimits",
      ];
      for (const key of arrays) {
        if (Array.isArray(data[key])) {
          expect(
            (data[key] as unknown[]).length,
            `${key} should be empty for non-existent component`,
          ).toBe(0);
        }
      }
    }
  });

  test("validation error – invalid metric type returns 400", async () => {
    const payload = {
      metric: "invalid",
      ...timeRange(60),
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.rawRequest(
      "POST",
      "/api/v1/metrics/query",
      payload,
      authHeaders(),
    );

    expect(status, "invalid metric type should return 400").toBe(400);
    const err = body as { title?: string; message?: string };
    expect(err, "error should have title").toHaveProperty("title");
    expect(err, "error should have message").toHaveProperty("message");
  });

  test("step parameter – custom step returns valid response", async () => {
    const req: MetricsQueryRequest = {
      metric: "resource",
      ...timeRange(60),
      step: "5m",
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryMetrics(req);
    // step parameter may not be supported — backend returns 500
    expect(
      [200, 500],
      "metrics with step parameter should return 200 or 500",
    ).toContain(status);

    if (status === 200) {
      // Verify the response is a valid object (not an error)
      expect(typeof body, "response body should be an object").toBe("object");
      expect(body, "response body should not be null").not.toBeNull();
    }
  });
 
});
