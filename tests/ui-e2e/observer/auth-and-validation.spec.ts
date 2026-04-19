import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";
import { getAuthToken } from "../helpers/auth-token.js";

const client = new ObserverApiClient();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function assertErrorResponse(body: unknown) {
  const obj = body as Record<string, unknown>;
  // Auth middleware returns {error, message}, validation returns {title, message}
  const hasErrorField = "error" in obj || "title" in obj;
  expect(hasErrorField).toBe(true);
  expect(body).toHaveProperty("message");
}

function timeRange(minutesAgo = 60): { startTime: string; endTime: string } {
  const now = new Date();
  const start = new Date(now.getTime() - minutesAgo * 60 * 1000);
  return { startTime: start.toISOString(), endTime: now.toISOString() };
}

const defaultSearchScope = { namespace: "default" };

/** Minimal valid bodies for each protected endpoint. */
const PROTECTED_ENDPOINTS = [
  {
    name: "logs/query",
    method: "POST",
    path: "/api/v1/logs/query",
    body: { ...timeRange(), searchScope: defaultSearchScope },
  },
  {
    name: "metrics/query",
    method: "POST",
    path: "/api/v1/metrics/query",
    body: {
      ...timeRange(),
      metric: "resource",
      searchScope: defaultSearchScope,
    },
  },
  {
    name: "traces/query",
    method: "POST",
    path: "/api/v1alpha1/traces/query",
    body: { ...timeRange(), searchScope: defaultSearchScope },
  },
  {
    name: "alerts/query",
    method: "POST",
    path: "/api/v1alpha1/alerts/query",
    body: { ...timeRange(), searchScope: defaultSearchScope },
  },
  {
    name: "incidents/query",
    method: "POST",
    path: "/api/v1alpha1/incidents/query",
    body: { ...timeRange(), searchScope: defaultSearchScope },
  },
] as const;

// ---------------------------------------------------------------------------
// Auth Failure Tests
// ---------------------------------------------------------------------------

test.describe("Auth failure – no token", () => {
  for (const ep of PROTECTED_ENDPOINTS) {
    test(`${ep.name} returns 401 without Authorization header`, async () => {
      const res = await client.rawRequest(ep.method, ep.path, ep.body, {
        "Content-Type": "application/json",
      });
      expect(res.status, `${ep.name} should reject missing token`).toBe(401);
      assertErrorResponse(res.body);
    });
  }
});

test.describe("Auth failure – invalid token", () => {
  for (const ep of PROTECTED_ENDPOINTS) {
    test(`${ep.name} returns 401 with invalid Bearer token`, async () => {
      const res = await client.rawRequest(ep.method, ep.path, ep.body, {
        "Content-Type": "application/json",
        Authorization: "Bearer invalid-token",
      });
      expect(res.status, `${ep.name} should reject invalid token`).toBe(401);
      assertErrorResponse(res.body);
    });
  }
});

// ---------------------------------------------------------------------------
// Validation Error Tests
// ---------------------------------------------------------------------------

test.describe("Validation errors", () => {
  function authHeaders(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getAuthToken()}`,
    };
  }

  test("missing required fields – no startTime/endTime", async () => {
    const res = await client.rawRequest(
      "POST",
      "/api/v1/logs/query",
      { searchScope: defaultSearchScope },
      authHeaders(),
    );
    expect(res.status, "missing required fields should return 400").toBe(400);
    assertErrorResponse(res.body);
  });

  test("invalid sortOrder value", async () => {
    const res = await client.rawRequest(
      "POST",
      "/api/v1/logs/query",
      {
        ...timeRange(),
        searchScope: defaultSearchScope,
        sortOrder: "random",
      },
      authHeaders(),
    );
    expect(res.status, "invalid sortOrder should return 400").toBe(400);
    assertErrorResponse(res.body);
  });

  test("negative limit", async () => {
    const res = await client.rawRequest(
      "POST",
      "/api/v1/logs/query",
      {
        ...timeRange(),
        searchScope: defaultSearchScope,
        limit: -1,
      },
      authHeaders(),
    );
    expect(res.status, "negative limit should return 400").toBe(400);
    assertErrorResponse(res.body);
  });

  test("time range exceeds 30-day limit", async () => {
    const now = new Date();
    const start = new Date(now.getTime() - 32 * 24 * 60 * 60 * 1000); // 32 days ago
    const res = await client.rawRequest(
      "POST",
      "/api/v1/logs/query",
      {
        startTime: start.toISOString(),
        endTime: now.toISOString(),
        searchScope: defaultSearchScope,
      },
      authHeaders(),
    );
    expect(res.status, "time range > 30 days should return 400").toBe(400);
    assertErrorResponse(res.body);
  });
});
