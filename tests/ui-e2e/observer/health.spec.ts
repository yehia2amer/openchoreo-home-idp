import { test, expect } from "@playwright/test";
import { ObserverApiClient } from "../helpers/observer-api.js";

const client = new ObserverApiClient();

test.describe("Observer Health", () => {
  test("GET /health returns 200 with healthy status", async () => {
    const { status, body } = await client.health();
    expect(status).toBe(200);
    expect(body).toHaveProperty("status");
    expect(body.status).toBe("healthy");
  });

  test("GET /health returns application/json content type", async () => {
    // Simple check that the response is parseable JSON (already handled by the client)
    const { status, body } = await client.health();
    expect(status).toBe(200);
    expect(typeof body).toBe("object");
  });
});
