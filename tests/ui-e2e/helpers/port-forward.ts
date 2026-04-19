import { spawn } from "child_process";

export interface PortForwardHandle {
  port: number;
  close: () => void;
}

/**
 * Starts a kubectl port-forward to a Kubernetes service.
 * Waits for the connection to be established before resolving.
 *
 * @param service - Service name (e.g., "observer-internal")
 * @param namespace - Kubernetes namespace
 * @param remotePort - Remote port to forward
 * @param localPort - Local port (0 = auto-select)
 * @returns Promise with port number and close function
 */
export function startPortForward(
  service: string,
  namespace: string,
  remotePort: number,
  localPort: number = 0,
): Promise<PortForwardHandle> {
  return new Promise((resolve, reject) => {
    // Use port 0 to let the OS pick a free port, or specified port
    const portArg =
      localPort === 0 ? `:${remotePort}` : `${localPort}:${remotePort}`;

    const proc = spawn(
      "kubectl",
      ["port-forward", `svc/${service}`, portArg, "-n", namespace],
      {
        stdio: ["pipe", "pipe", "pipe"],
      },
    );

    let resolved = false;
    let stderr = "";

    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        proc.kill();
        reject(
          new Error(
            `Port-forward to ${service}:${remotePort} timed out after 15s. stderr: ${stderr}`,
          ),
        );
      }
    }, 15000);

    proc.stdout?.on("data", (data: Buffer) => {
      const output = data.toString();
      // kubectl outputs: "Forwarding from 127.0.0.1:PORT -> REMOTE_PORT"
      const match = output.match(/Forwarding from 127\.0\.0\.1:(\d+)/);
      if (match && !resolved) {
        resolved = true;
        clearTimeout(timeout);
        const actualPort = parseInt(match[1], 10);
        resolve({
          port: actualPort,
          close: () => {
            proc.kill("SIGTERM");
          },
        });
      }
    });

    proc.stderr?.on("data", (data: Buffer) => {
      stderr += data.toString();
    });

    proc.on("error", (err) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        reject(new Error(`Failed to start port-forward: ${err.message}`));
      }
    });

    proc.on("exit", (code) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        reject(
          new Error(
            `Port-forward exited with code ${code}. stderr: ${stderr}`,
          ),
        );
      }
    });
  });
}

export const OBSERVER_INTERNAL = {
  service: "observer-internal",
  namespace: "openchoreo-observability-plane",
  port: 8081,
} as const;
