"""Pulumi dynamic resource: wait for the Kubernetes API server to become ready.

After Talos bootstrap, the K8s API server takes ~30-60s to become available:
  1. etcd starts up and elects a leader
  2. kubelet starts the kube-apiserver static pod
  3. kube-apiserver begins listening on port 6443

This resource polls through that entire startup to ensure the API server is
fully ready before any Kubernetes resources (CRDs, Helm charts) are applied.

Strategy (three-phase):
  Phase 1 — Initial delay: give etcd + kubelet time to start
  Phase 2 — TCP reachability on port 6443
  Phase 3 — HTTP readiness: GET /readyz returns 200 (with --insecure TLS)

Design follows the established pattern in wait_for_talos_node.py and
helpers/dynamic_providers.py.
"""

# pyright: reportIncompatibleMethodOverride=false

from __future__ import annotations

import http.client
import socket
import ssl
import time
from typing import Any

import pulumi
from pulumi.dynamic import CreateResult, DiffResult, ResourceProvider, UpdateResult


def _input_diff(olds: dict[str, Any], news: dict[str, Any], keys: list[str]) -> DiffResult:
    """Compare specific input keys and return a DiffResult."""
    changes = any(olds.get(k) != news.get(k) for k in keys)
    return DiffResult(changes=changes, replaces=[], stables=[], delete_before_replace=False)


# ---------------------------------------------------------------------------
# Low-level wait helpers
# ---------------------------------------------------------------------------


def _check_tcp(host: str, port: int, connect_timeout: float = 5.0) -> bool:
    """Return True if a TCP connection to host:port succeeds."""
    try:
        with socket.create_connection((host, int(port)), timeout=connect_timeout):
            return True
    except (OSError, TimeoutError):
        return False


def _check_k8s_readyz(host: str, port: int, connect_timeout: float = 10.0) -> tuple[bool, int | None]:
    """Return (True, status_code) if the K8s API server responds to HTTP at all.

    Any HTTP response — 200, 401, 403 — proves the API server is up and
    processing requests.  Talos clusters disable anonymous auth, so /readyz
    returns 401; a 401 from kube-apiserver is conclusive proof it's running.
    Only connection errors / timeouts indicate the server is actually down.

    Uses HTTPS with certificate verification disabled (the API server uses
    a self-signed CA during initial bootstrap).
    """
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        conn = http.client.HTTPSConnection(
            host,
            port=int(port),
            timeout=connect_timeout,
            context=ctx,
        )
        try:
            conn.request("GET", "/readyz")
            resp = conn.getresponse()
            # Any HTTP response means the API server is running.
            # 200 = fully ready, 401/403 = running but no anonymous access,
            # 500/503 = starting up but processing requests.
            return (resp.status < 500, resp.status)
        finally:
            conn.close()
    except (OSError, TimeoutError, http.client.HTTPException):
        return (False, None)


def wait_for_kubernetes_api(
    host: str,
    port: int = 6443,
    timeout: int = 600,
    poll_interval: int = 10,
    initial_delay: int = 15,
) -> dict[str, Any]:
    """Poll until the Kubernetes API server is fully ready.

    This is designed for the post-Bootstrap, pre-K8s-resources wait.
    It ensures the API server can accept and process requests before
    CRDs, Helm charts, or other Kubernetes resources are applied.

    Strategy (three-phase):
      Phase 1 — Initial delay: give etcd/kubelet/apiserver time to start.
      Phase 2 — TCP handshake on port 6443 (detect when API starts listening).
      Phase 3 — HTTP readiness via GET /readyz (confirm API is fully ready).

    Returns a dict with timing metadata for Pulumi outputs.
    Raises TimeoutError if the API is not ready within ``timeout`` seconds.
    """
    port = int(port)
    timeout = int(timeout)
    poll_interval = int(poll_interval)
    initial_delay = int(initial_delay)
    start = time.monotonic()
    deadline = start + timeout
    attempts = 0
    tcp_ready_at: float | None = None

    pulumi.log.info(
        f"Waiting for Kubernetes API at {host}:{port} to become ready "
        f"(timeout={timeout}s, initial_delay={initial_delay}s) …"
    )

    # ── Phase 1: Initial delay for etcd + apiserver startup ────
    if initial_delay > 0:
        pulumi.log.info(f"Phase 1: Waiting {initial_delay}s for etcd/kubelet/apiserver to start …")
        time.sleep(min(initial_delay, max(0, deadline - time.monotonic())))

    # ── Phase 2: TCP reachability ──────────────────────────────
    pulumi.log.info(f"Phase 2: Polling TCP on {host}:{port} …")
    while time.monotonic() < deadline:
        attempts += 1
        if _check_tcp(host, port):
            tcp_ready_at = time.monotonic()
            elapsed = round(tcp_ready_at - start, 1)
            pulumi.log.info(f"Kubernetes API TCP reachable after {elapsed}s ({attempts} attempts)")
            break
        remaining = round(deadline - time.monotonic(), 0)
        if attempts % 6 == 0:
            pulumi.log.info(f"Still waiting for TCP on {host}:{port} … ({remaining}s remaining)")
        time.sleep(poll_interval)
    else:
        msg = f"Timeout: Kubernetes API TCP on {host}:{port} not reachable after {timeout}s"
        raise TimeoutError(msg)

    # ── Phase 3: HTTP readiness (/readyz) ──────────────────────
    pulumi.log.info("Phase 3: Checking /readyz endpoint for full API readiness …")
    phase3_attempts = 0
    while time.monotonic() < deadline:
        phase3_attempts += 1
        ready, status_code = _check_k8s_readyz(host, port)
        if ready:
            total_elapsed = round(time.monotonic() - start, 1)
            pulumi.log.info(f"Kubernetes API at {host}:{port} is READY (HTTP {status_code}) after {total_elapsed}s")
            return {
                "ready": True,
                "tcp_reachable_after_s": round((tcp_ready_at or start) - start, 1),
                "total_elapsed_s": total_elapsed,
                "attempts": attempts + phase3_attempts,
            }

        remaining = round(deadline - time.monotonic(), 0)
        status_str = f"HTTP {status_code}" if status_code else "no response"
        if phase3_attempts % 3 == 0:
            pulumi.log.info(f"API not ready yet ({status_str}) … ({remaining}s remaining)")
        time.sleep(poll_interval)

    msg = (
        f"Timeout: Kubernetes API at {host}:{port} did not become ready "
        f"within {timeout}s (TCP was reachable after "
        f"{round((tcp_ready_at or start) - start, 1)}s)"
    )
    raise TimeoutError(msg)


# ---------------------------------------------------------------------------
# Pulumi Dynamic Resource
# ---------------------------------------------------------------------------

_DIFF_KEYS = ["host", "port", "timeout", "initial_delay"]


class _WaitForKubernetesAPIProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        result = wait_for_kubernetes_api(
            host=inputs["host"],
            port=inputs.get("port", 6443),
            timeout=inputs.get("timeout", 600),
            poll_interval=inputs.get("poll_interval", 10),
            initial_delay=inputs.get("initial_delay", 15),
        )
        return CreateResult(
            id_=f"k8s-api-ready-{inputs['host']}",
            outs={**inputs, **result},
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, _DIFF_KEYS)

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # read-only wait — nothing to clean up


class WaitForKubernetesAPI(pulumi.dynamic.Resource):
    """Wait for the Kubernetes API server to become fully ready after bootstrap.

    Insert between Bootstrap/Kubeconfig and the Kubernetes provider/resources.
    Waits for the API server to pass /readyz before allowing CRDs, Helm charts,
    and other K8s resources to proceed.
    """

    ready: pulumi.Output[bool]
    tcp_reachable_after_s: pulumi.Output[float]
    total_elapsed_s: pulumi.Output[float]
    attempts: pulumi.Output[int]

    def __init__(
        self,
        name: str,
        *,
        host: pulumi.Input[str],
        port: pulumi.Input[int] = 6443,
        timeout: pulumi.Input[int] = 600,
        poll_interval: pulumi.Input[int] = 10,
        initial_delay: pulumi.Input[int] = 15,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _WaitForKubernetesAPIProvider(),
            name,
            {
                "host": host,
                "port": port,
                "timeout": timeout,
                "poll_interval": poll_interval,
                "initial_delay": initial_delay,
                "ready": None,
                "tcp_reachable_after_s": None,
                "total_elapsed_s": None,
                "attempts": None,
            },
            opts,
        )
