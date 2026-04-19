import * as fs from "fs";
import * as path from "path";

type StorageState = {
  cookies?: Array<{ name?: string; value?: string }>;
  origins?: Array<{
    origin?: string;
    localStorage?: Array<{ name?: string; value?: string }>;
  }>;
};

const AUTH_STATE_PATH = path.resolve(__dirname, "..", ".auth", "state.json");

function isJwtLike(value: string | undefined): value is string {
  return typeof value === "string" && value.startsWith("ey");
}

export function getAuthToken(): string {
  if (!fs.existsSync(AUTH_STATE_PATH)) {
    throw new Error(`Auth state file not found at ${AUTH_STATE_PATH}. Run auth setup first.`);
  }

  let raw: string;
  try {
    raw = fs.readFileSync(AUTH_STATE_PATH, "utf8");
  } catch (error) {
    throw new Error(`Failed to read auth state file at ${AUTH_STATE_PATH}: ${(error as Error).message}`);
  }

  let state: StorageState;
  try {
    state = JSON.parse(raw) as StorageState;
  } catch (error) {
    throw new Error(`Failed to parse auth state JSON at ${AUTH_STATE_PATH}: ${(error as Error).message}`);
  }

  for (const origin of state.origins ?? []) {
    for (const entry of origin.localStorage ?? []) {
      const key = entry.name ?? "";
      const value = entry.value;

      if (key.includes("access_token") || key.includes("token")) {
        if (typeof value === "string" && value.length > 0) {
          return value;
        }
      }

      if (isJwtLike(value)) {
        return value;
      }
    }
  }

  for (const cookie of state.cookies ?? []) {
    if (isJwtLike(cookie.value)) {
      return cookie.value;
    }
  }

  throw new Error(
    `No JWT bearer token found in ${AUTH_STATE_PATH}. Checked localStorage entries and cookies for values starting with \"ey\".`,
  );
}
