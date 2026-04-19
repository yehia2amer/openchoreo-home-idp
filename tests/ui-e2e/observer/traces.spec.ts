import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  TracesQueryRequest,
  ErrorResponse,
} from "../helpers/observer-api.js";
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

test.describe("Observer Traces & Spans", () => {
  test.describe.configure({ mode: "serial" });

  let sharedTraceId: string | undefined;
  let sharedSpanId: string | undefined;

  // Skip until obs-test-gen is deployed and instrumented on GKE
  test.skip("traces query – returns traces for homelab-tools namespace", async () => {
    const range = timeRange(60);
    const req: TracesQueryRequest = {
      ...range,
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const result = await pollUntil(
      () => client.queryTraces(req),
      (r) => r.status === 200 && r.body.total > 0,
      { ...POLL_BUDGETS.traces, description: "waiting for traces" },
    );

    expect(result.status, "traces query should return 200").toBe(200);
    expect(Array.isArray(result.body.traces), "traces should be an array").toBe(
      true,
    );
    expect(result.body.total, "total should be > 0").toBeGreaterThan(0);
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

    // Store for chained tests
    sharedTraceId = result.body.traces[0].traceId;
  });

  // Skip until obs-test-gen is deployed and instrumented on GKE
  test.skip("spans query – returns spans for a discovered trace", async () => {
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

  // Skip until obs-test-gen is deployed and instrumented on GKE
  test.skip("span details – returns attributes for a discovered span", async () => {
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

  // Skip until obs-test-gen is deployed and instrumented on GKE
  test.skip("empty result – epoch time range returns no traces", async () => {
    const req: TracesQueryRequest = {
      startTime: "1970-01-01T00:00:00Z",
      endTime: "1970-01-01T00:01:00Z",
      searchScope: {
        namespace: "default",
        project: "homelab-tools",
        environment: "development",
      },
    };

    const { status, body } = await client.queryTraces(req);
    expect(status, "should return 200 for empty result").toBe(200);
    expect(body.traces, "traces should be empty array").toEqual([]);
    expect(body.total, "total should be 0").toBe(0);
  });

  // Skip until obs-test-gen is deployed and instrumented on GKE
  test.skip("validation error – missing namespace in searchScope returns 400", async () => {
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
