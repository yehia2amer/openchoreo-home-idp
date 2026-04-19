export interface PollOptions {
  intervalMs: number;
  timeoutMs: number;
  description?: string;
}

export const POLL_BUDGETS = {
  logs: { intervalMs: 10_000, timeoutMs: 120_000 },
  traces: { intervalMs: 10_000, timeoutMs: 120_000 },
  metrics: { intervalMs: 15_000, timeoutMs: 120_000 },
  alerts: { intervalMs: 5_000, timeoutMs: 60_000 },
  incidents: { intervalMs: 5_000, timeoutMs: 60_000 },
} as const;

export async function pollUntil<T>(
  fn: () => Promise<T>,
  predicate: (result: T) => boolean,
  options: PollOptions,
): Promise<T> {
  const { intervalMs, timeoutMs, description } = options;
  const start = Date.now();
  let lastResult: T | undefined;

  while (Date.now() - start < timeoutMs) {
    lastResult = await fn();
    if (predicate(lastResult)) {
      return lastResult;
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  const elapsed = Date.now() - start;
  throw new Error(
    `Polling timed out after ${elapsed}ms${description ? ` (${description})` : ""}. Last result: ${JSON.stringify(lastResult)}`,
  );
}
