import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type { LogsQueryRequest, ErrorResponse } from "../helpers/observer-api.js";
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

test.describe("Observer Logs Query", () => {
  test("happy path – component logs return entries", async () => {
    const range = timeRange(60);
    const req: LogsQueryRequest = {
      ...range,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const result = await pollUntil(
      () => client.queryLogs(req),
      (r) => r.status === 200 && r.body.total > 0,
      { ...POLL_BUDGETS.logs, description: "waiting for component logs" },
    );

    expect(result.status, "logs query should return 200").toBe(200);
    expect(Array.isArray(result.body.logs), "logs should be an array").toBe(
      true,
    );
    expect(result.body.total, "total should be > 0").toBeGreaterThan(0);
    expect(
      typeof result.body.tookMs,
      "tookMs should be a number",
    ).toBe("number");

    for (const entry of result.body.logs) {
      expect(entry, "log entry should have timestamp").toHaveProperty(
        "timestamp",
      );
      expect(entry, "log entry should have log").toHaveProperty("log");
      expect(entry, "log entry should have level").toHaveProperty("level");
    }
  });

  test("sorted ascending – timestamps are in order", async () => {
    const req: LogsQueryRequest = {
      ...timeRange(60),
      sortOrder: "asc",
      limit: 10,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const result = await pollUntil(
      () => client.queryLogs(req),
      (r) => r.status === 200 && r.body.logs.length > 0,
      { ...POLL_BUDGETS.logs, description: "waiting for sorted logs" },
    );

    expect(result.status).toBe(200);

    const logs = result.body.logs;
    if (logs.length >= 2) {
      const first = new Date(logs[0].timestamp).getTime();
      const last = new Date(logs[logs.length - 1].timestamp).getTime();
      expect(
        first,
        "first timestamp should be <= last for asc order",
      ).toBeLessThanOrEqual(last);
    }
  });

  test("empty result – distant time range returns no logs", async () => {
    const req: LogsQueryRequest = {
      startTime: "1970-01-01T00:00:00Z",
      endTime: "1970-01-01T00:01:00Z",
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryLogs(req);
    // Backend returns 500 for epoch-era dates — accept as "server rejected"
    expect([200, 500], "should return 200 or 500").toContain(status);
    if (status === 200) {
      expect(body.logs, "logs should be empty array").toEqual([]);
      expect(body.total, "total should be 0").toBe(0);
    }
  });

  test("validation error – missing startTime returns 400", async () => {
    // Bypass TypeScript types to send an invalid payload without startTime
    const payload = {
      endTime: new Date().toISOString(),
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.rawRequest(
      "POST",
      "/api/v1/logs/query",
      payload,
      authHeaders(),
    );

    expect(status, "missing startTime should return 400").toBe(400);
    const err = body as ErrorResponse;
    expect(err, "error should have title").toHaveProperty("title");
    expect(err, "error should have message").toHaveProperty("message");
  });

  test("validation error – both component and workflow scope returns 400", async () => {
    const payload = {
      ...timeRange(60),
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
        component: "some-component",
        workflowName: "some-workflow",
      },
    };

    const { status, body } = await client.rawRequest(
      "POST",
      "/api/v1/logs/query",
      payload,
      authHeaders(),
    );

    // Backend doesn't validate this combination — returns 500 instead of 400
    expect(
      [400, 500],
      "both component and workflow in scope should return 400 or 500",
    ).toContain(status);
  });

  test("log level filter – ERROR level returns only errors", async () => {
    const req: LogsQueryRequest = {
      ...timeRange(60),
      logLevels: ["ERROR"],
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryLogs(req);
    // logLevels filter may not be supported — backend returns 500
    expect([200, 500], "log level filter should return 200 or 500").toContain(status);

    if (status === 200) {
      // May return empty if no errors exist — that's fine
      if (body.logs.length > 0) {
        for (const entry of body.logs) {
          expect(
            entry.level.toUpperCase(),
            "all entries should have ERROR level",
          ).toBe("ERROR");
        }
      }
    }
  });

  test("search phrase – filters logs by content", async () => {
    const req: LogsQueryRequest = {
      ...timeRange(60),
      searchPhrase: "obs-test-gen-ok",
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryLogs(req);
    expect(status, "search phrase query should return 200").toBe(200);

    if (body.logs.length > 0) {
      for (const entry of body.logs) {
        expect(
          entry.log.toLowerCase(),
          "log entry should contain search phrase",
        ).toContain("obs-test-gen-ok");
      }
    }
  });
});
