import * as crypto from "crypto";

const RUN_ID = `e2e-${formatDate()}-${randomSuffix()}`;

function formatDate(): string {
  const now = new Date();
  return `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}`;
}

function randomSuffix(): string {
  return crypto.randomBytes(3).toString("hex");
}

export function getRunId(): string {
  return RUN_ID;
}

export function makeAlertRuleName(base: string): string {
  return `${RUN_ID}-${base}`;
}
