import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  TracesQueryRequest,
  ErrorResponse,
} from "../helpers/observer-api.js";
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

test.describe("Observer Traces & Spans", () => {
  test.describe.configure({ mode: "serial" });

  let sharedTraceId: string | undefined;
  let sharedSpanId: string | undefined;

  test("traces query – returns valid response structure", async () => {
    const range = timeRange(60);
    const req: TracesQueryRequest = {
      ...range,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const result = await client.queryTraces(req);

    expect(result.status, "traces query should return 200").toBe(200);
    expect(result.body, "response should have traces").toHaveProperty("traces");
    expect(result.body, "response should have total").toHaveProperty("total");
    expect(result.body, "response should have tookMs").toHaveProperty("tookMs");
    expect(Array.isArray(result.body.traces), "traces should be an array").toBe(
      true,
    );
    expect(typeof result.body.total, "total should be a number").toBe(
      "number",
    );
    expect(typeof result.body.tookMs, "tookMs should be a number").toBe(
      "number",
    );

    for (const trace of result.body.traces) {
      expect(trace, "trace should have traceId").toHaveProperty("traceId");
      expect(trace, "trace should have spanCount").toHaveProperty("spanCount");
      expect(trace, "trace should have startTime").toHaveProperty("startTime");
      expect(trace, "trace should have endTime").toHaveProperty("endTime");
      expect(trace, "trace should have durationNs").toHaveProperty(
        "durationNs",
      );
    }

    if (result.body.traces.length > 0) {
      // Store for chained tests
      sharedTraceId = result.body.traces[0].traceId;
    }
  });

  test("spans query – returns spans for a discovered trace", async () => {
    test.skip(!sharedTraceId, "no traceId available from traces query");

    const range = timeRange(60);
    const req: TracesQueryRequest = {
      ...range,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const result = await client.queryTraceSpans(sharedTraceId!, req);

    expect(result.status, "spans query should return 200").toBe(200);
    expect(Array.isArray(result.body.spans), "spans should be an array").toBe(
      true,
    );
    expect(result.body.total, "total should be > 0").toBeGreaterThan(0);
    expect(typeof result.body.tookMs, "tookMs should be a number").toBe(
      "number",
    );

    for (const span of result.body.spans) {
      expect(span, "span should have spanId").toHaveProperty("spanId");
      expect(span, "span should have spanName").toHaveProperty("spanName");
      expect(span, "span should have spanKind").toHaveProperty("spanKind");
      expect(span, "span should have status").toHaveProperty("status");
    }

    // Store for chained tests
    sharedSpanId = result.body.spans[0].spanId;
  });

  test("span details – returns attributes for a discovered span", async () => {
    test.skip(
      !sharedTraceId || !sharedSpanId,
      "no traceId/spanId available from previous queries",
    );

    const result = await client.getSpanDetails(
      sharedTraceId!,
      sharedSpanId!,
    );

    expect(result.status, "span details should return 200").toBe(200);
    expect(result.body, "response should have spanId").toHaveProperty("spanId");
    expect(result.body.spanId, "spanId should match requested").toBe(
      sharedSpanId,
    );
    expect(result.body, "response should have spanName").toHaveProperty(
      "spanName",
    );
    expect(
      Array.isArray(result.body.attributes),
      "attributes should be an array",
    ).toBe(true);

    for (const attr of result.body.attributes) {
      expect(attr, "attribute should have key").toHaveProperty("key");
      expect(attr, "attribute should have value").toHaveProperty("value");
    }
  });

  test("empty result – epoch time range returns no traces", async () => {
    const { status, body } = await client.queryTraces({
      startTime: "1970-01-01T00:00:00Z",
      endTime: "1970-01-01T00:01:00Z",
      limit: 10,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    });

    expect([200, 500]).toContain(status);
    if (status === 200) {
      expect(body.total, "total should be 0").toBe(0);
    }
  });

  test("validation error – missing namespace in searchScope returns 400", async () => {
    const payload = {
      ...timeRange(60),
      searchScope: {},
    };

    const { status, body } = await client.rawRequest(
      "POST",
      "/api/v1alpha1/traces/query",
      payload,
      authHeaders(),
    );

    expect(status, "missing namespace should return 400").toBe(400);
    const err = body as ErrorResponse;
    expect(err, "error should have title").toHaveProperty("title");
    expect(err, "error should have message").toHaveProperty("message");
  });

});
