"""Pulumi dynamic resource: wait for a Talos node to become ready after config apply.

After ConfigurationApply with apply_mode="auto" in maintenance mode, the Talos
node goes through an INSTALL sequence (not a reboot):
  1. Config is applied with NO_REBOOT (Talos forces this in maintenance mode)
  2. The node writes the OS to disk (API goes down — "black screen" phase)
  3. The node reboots internally and comes up in RUNNING stage
  4. The Talos gRPC API becomes reachable again, now requiring mutual TLS

This resource polls through that entire transition to ensure the node has
reached RUNNING stage before bootstrap proceeds.

Strategy (three-phase):
  Phase 1 — Initial delay: wait for the install-to-disk + internal reboot
  Phase 2 — TCP reachability on port 50000
  Phase 3 — Verify node has left maintenance mode (TLS probe / talosctl)

NOTE: `talosctl health` (etcd, kubelet, etc.) is NOT used here because those
services only start AFTER bootstrap. This resource sits BEFORE bootstrap.

Design follows the established pattern in helpers/dynamic_providers.py.
"""

# pyright: reportIncompatibleMethodOverride=false

from __future__ import annotations

import shutil
import socket
import ssl
import subprocess
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


def _check_node_left_maintenance(host: str, port: int) -> bool:
    """Return True if the node is no longer in maintenance mode.

    In maintenance mode, Talos accepts TLS connections without client certs.
    In running mode, Talos requires mutual TLS and rejects bare connections.

    We detect the transition by attempting an insecure TLS handshake:
      - Succeeds → still in maintenance mode → return False
      - Fails with TLS error → node now requires mTLS → return True (RUNNING)
      - Connection refused / timeout → node is still rebooting → return False
    """
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        raw = socket.create_connection((host, int(port)), timeout=5.0)
        with ctx.wrap_socket(raw, server_hostname=host):
            # TLS handshake succeeded without client cert → still maintenance
            return False
    except ssl.SSLError:
        # TLS rejected our no-cert connection → node requires mTLS → RUNNING
        return True
    except (OSError, TimeoutError):
        # Connection failed entirely → node still rebooting
        return False


def _check_talosctl_running(host: str) -> bool | None:
    """Use talosctl to definitively check if node has left maintenance mode.

    Tries `talosctl get machinestatus --insecure` — if it fails, the node
    is no longer in maintenance mode (running mode rejects insecure calls).

    Returns:
        True  — node is confirmed NOT in maintenance (insecure rejected)
        False — node is still in maintenance (insecure succeeded)
        None  — talosctl not available or inconclusive
    """
    talosctl = shutil.which("talosctl")
    if talosctl is None:
        return None

    try:
        result = subprocess.run(
            [talosctl, "get", "machinestatus", "--insecure", "--nodes", host, "--endpoints", host],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Insecure access worked (rc=0) → still in maintenance → False
        # Insecure access failed (rc!=0) → left maintenance → True
        return result.returncode != 0
    except (subprocess.TimeoutExpired, OSError):
        return None


def wait_for_talos_api(
    node: str,
    endpoint: str,
    port: int = 50000,
    talosconfig_path: str | None = None,
    timeout: int = 600,
    poll_interval: int = 10,
    initial_delay: int = 0,
) -> dict[str, Any]:
    """Poll until the Talos node has finished installing and reached RUNNING stage.

    This is designed for the post-ConfigurationApply, pre-Bootstrap wait.
    It does NOT check cluster health (etcd/kubelet) — those require bootstrap first.

    Strategy (three-phase):
      Phase 1 — Initial delay: give the node time to start the install sequence.
                During this phase the API goes down as the node writes to disk.
      Phase 2 — TCP handshake on port 50000 (detect when API comes back up).
      Phase 3 — Verify node has left maintenance mode via TLS probe.
                A running node requires mutual TLS, so a bare TLS handshake fails.

    Returns a dict with timing metadata for Pulumi outputs.
    Raises TimeoutError if the node is not ready within ``timeout`` seconds.
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
        f"Waiting for Talos node {endpoint} to reach RUNNING stage "
        f"(timeout={timeout}s, initial_delay={initial_delay}s) …"
    )

    # ── Phase 1: Initial delay for disk install ────────────────
    if initial_delay > 0:
        pulumi.log.info(
            f"Phase 1: Waiting {initial_delay}s for disk install to begin "
            f"(node will be unreachable during this phase) …"
        )
        time.sleep(min(initial_delay, max(0, deadline - time.monotonic())))

    # ── Phase 2: TCP reachability ──────────────────────────────
    pulumi.log.info(f"Phase 2: Polling TCP on {endpoint}:{port} …")
    while time.monotonic() < deadline:
        attempts += 1
        if _check_tcp(endpoint, port):
            tcp_ready_at = time.monotonic()
            elapsed = round(tcp_ready_at - start, 1)
            pulumi.log.info(f"Talos API TCP reachable after {elapsed}s ({attempts} attempts)")
            break
        remaining = round(deadline - time.monotonic(), 0)
        if attempts % 6 == 0:
            pulumi.log.info(f"Still waiting for TCP on {endpoint}:{port} … ({remaining}s remaining)")
        time.sleep(poll_interval)
    else:
        msg = f"Timeout: Talos API TCP on {endpoint}:{port} not reachable after {timeout}s"
        raise TimeoutError(msg)

    # ── Phase 3: Verify node has left maintenance mode ─────────
    pulumi.log.info("Phase 3: Verifying node has left maintenance mode …")
    phase3_attempts = 0
    while time.monotonic() < deadline:
        phase3_attempts += 1

        # Primary check: talosctl insecure (most reliable)
        talosctl_result = _check_talosctl_running(endpoint)
        if talosctl_result is True:
            total_elapsed = round(time.monotonic() - start, 1)
            pulumi.log.info(f"Node {node} confirmed RUNNING (talosctl insecure rejected) after {total_elapsed}s")
            return {
                "healthy": True,
                "tcp_reachable_after_s": round(tcp_ready_at - start, 1),
                "total_elapsed_s": total_elapsed,
                "attempts": attempts + phase3_attempts,
                "stage": "running",
            }
        if talosctl_result is False:
            remaining = round(deadline - time.monotonic(), 0)
            if phase3_attempts % 3 == 0:
                pulumi.log.info(f"Node still in maintenance mode … ({remaining}s remaining)")
            time.sleep(poll_interval)
            continue

        # Fallback: TLS probe (if talosctl unavailable)
        if _check_node_left_maintenance(endpoint, port):
            total_elapsed = round(time.monotonic() - start, 1)
            pulumi.log.info(f"Node {node} confirmed RUNNING (TLS probe: requires mTLS) after {total_elapsed}s")
            return {
                "healthy": True,
                "tcp_reachable_after_s": round(tcp_ready_at - start, 1),
                "total_elapsed_s": total_elapsed,
                "attempts": attempts + phase3_attempts,
                "stage": "running",
            }

        remaining = round(deadline - time.monotonic(), 0)
        if phase3_attempts % 3 == 0:
            pulumi.log.info(f"Node still in maintenance mode … ({remaining}s remaining)")
        time.sleep(poll_interval)

    msg = (
        f"Timeout: Node {endpoint} did not leave maintenance mode within {timeout}s "
        f"(TCP was reachable after {round((tcp_ready_at or start) - start, 1)}s)"
    )
    raise TimeoutError(msg)


# ---------------------------------------------------------------------------
# Pulumi Dynamic Resource
# ---------------------------------------------------------------------------

_DIFF_KEYS = ["node", "endpoint", "port", "timeout", "initial_delay"]


class _WaitForTalosNodeReadyProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        result = wait_for_talos_api(
            node=inputs["node"],
            endpoint=inputs["endpoint"],
            port=inputs.get("port", 50000),
            talosconfig_path=inputs.get("talosconfig_path"),
            timeout=inputs.get("timeout", 600),
            poll_interval=inputs.get("poll_interval", 10),
            initial_delay=inputs.get("initial_delay", 0),
        )
        return CreateResult(
            id_=f"talos-ready-{inputs['node']}",
            outs={**inputs, **result},
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, _DIFF_KEYS)

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass


class WaitForTalosNodeReady(pulumi.dynamic.Resource):
    """Wait for a Talos node to reach RUNNING stage after ConfigurationApply.

    Insert between ConfigurationApply and Bootstrap. Waits for the node to
    complete its install-to-disk sequence and leave maintenance mode.
    Does NOT check cluster health (etcd/kubelet) — those start after bootstrap.
    """

    healthy: pulumi.Output[bool]
    tcp_reachable_after_s: pulumi.Output[float]
    total_elapsed_s: pulumi.Output[float]
    attempts: pulumi.Output[int]
    stage: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        *,
        node: pulumi.Input[str],
        endpoint: pulumi.Input[str],
        port: pulumi.Input[int] = 50000,
        talosconfig_path: pulumi.Input[str] | None = None,
        timeout: pulumi.Input[int] = 600,
        poll_interval: pulumi.Input[int] = 10,
        initial_delay: pulumi.Input[int] = 30,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _WaitForTalosNodeReadyProvider(),
            name,
            {
                "node": node,
                "endpoint": endpoint,
                "port": port,
                "talosconfig_path": talosconfig_path,
                "timeout": timeout,
                "poll_interval": poll_interval,
                "initial_delay": initial_delay,
                "healthy": None,
                "tcp_reachable_after_s": None,
                "total_elapsed_s": None,
                "attempts": None,
                "stage": None,
            },
            opts,
        )
