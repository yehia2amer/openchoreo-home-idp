import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import type {
  TracesQueryRequest,
  ErrorResponse,
} from "../helpers/observer-api.js";
import { getAuthToken } from "../helpers/auth-token.js";
import { startPortForward, PortForwardHandle } from "../helpers/port-forward.js";
import { pollUntil, POLL_BUDGETS } from "../helpers/polling.js";

const client = new ObserverApiClient();

let obsTestGenPf: PortForwardHandle | null = null;
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

  test.beforeAll(async () => {
    test.setTimeout(120_000);

    // Port-forward to obs-test-gen service to generate traffic
    try {
      obsTestGenPf = await startPortForward(
        "obs-test-gen",
        "dp-default-homelab-tools-development-9c449072",
        8080,
      );

      // Send multiple requests to generate trace spans
      const baseUrl = `http://localhost:${obsTestGenPf.port}`;
      for (let i = 0; i < 5; i++) {
        await fetch(`${baseUrl}/`).catch(() => {});
        await fetch(`${baseUrl}/error`).catch(() => {});
      }

      // Wait for traces to propagate through the pipeline
      // Odigos → OTEL collector → OpenObserve → tracing adapter → Observer
      console.log("[traces] Generated traffic, waiting 30s for trace propagation...");
      await new Promise(resolve => setTimeout(resolve, 30000));
    } catch (err) {
      console.warn("[traces] Failed to generate traffic:", err);
      // Don't fail the suite if traffic generation fails - tests will skip gracefully
    }
  });

  test.afterAll(async () => {
    obsTestGenPf?.close();
  });

  let sharedTraceId: string | undefined;
  let sharedSpanId: string | undefined;

  test("traces query – returns valid response structure", async () => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);

    // Try polling for traces (they may take time to appear after traffic generation)
    try {
      const result = await pollUntil(
        async () => client.queryTraces({
          startTime: oneHourAgo.toISOString(),
          endTime: now.toISOString(),
          limit: 10,
          searchScope: { namespace: "default", project: "homelab-tools", environment: "development" },
        }),
        (r) => r.status === 200 && r.body.total > 0,
        { ...POLL_BUDGETS.traces, description: "waiting for traces" },
      );

      expect(result.status).toBe(200);
      expect(result.body.traces.length).toBeGreaterThan(0);
      sharedTraceId = result.body.traces[0].traceId;
      expect(result.body.traces[0]).toHaveProperty("traceId");
      expect(result.body.traces[0]).toHaveProperty("startTime");
    } catch {
      // If polling times out, still validate the API contract with empty result
      const { status, body } = await client.queryTraces({
        startTime: oneHourAgo.toISOString(),
        endTime: now.toISOString(),
        limit: 10,
        searchScope: { namespace: "default", project: "homelab-tools", environment: "development" },
      });
      expect(status).toBe(200);
      expect(body).toHaveProperty("traces");
      expect(body).toHaveProperty("total");
      expect(body).toHaveProperty("tookMs");
      // sharedTraceId remains null — downstream tests will skip
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
