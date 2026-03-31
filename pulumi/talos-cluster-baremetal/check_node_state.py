"""Pre-flight detection of Talos node state.

Determines whether a Talos node is:
  - UNREACHABLE: TCP port 50000 is not open (node down or rebooting)
  - MAINTENANCE: Talos API accepts insecure (no TLS) connections (ready for config apply)
  - RUNNING: Talos API requires mutual TLS (already configured and booted)

This is used by the main Pulumi program to decide whether ConfigurationApply
and Bootstrap should run, or whether they should be skipped because the node
is already operational.
"""

from __future__ import annotations

import enum
import shutil
import socket
import ssl
import subprocess
from typing import NamedTuple

import pulumi


class NodeState(enum.Enum):
    """Possible states of a Talos node."""

    UNREACHABLE = "unreachable"
    MAINTENANCE = "maintenance"
    RUNNING = "running"


class NodeStatus(NamedTuple):
    """Result of a pre-flight node state check."""

    state: NodeState
    message: str


def _tcp_open(host: str, port: int, timeout: float = 5.0) -> bool:
    """Return True if a TCP connection to host:port succeeds."""
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except (OSError, TimeoutError):
        return False


def _try_insecure_connect(host: str, port: int, timeout: float = 5.0) -> tuple[bool, str]:
    """Attempt a TLS handshake with no client cert (insecure mode).

    In maintenance mode, Talos accepts connections without client certificates.
    In running mode, Talos requires mutual TLS and rejects with:
      "tls: certificate required" or similar handshake error.

    Returns:
        (True, message) if insecure connect succeeded (maintenance mode)
        (False, error_message) if it failed (running mode or other error)
    """
    try:
        # Create a permissive SSL context — no client cert, don't verify server
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        raw = socket.create_connection((host, int(port)), timeout=timeout)
        with ctx.wrap_socket(raw, server_hostname=host) as _:
            return True, "TLS handshake succeeded without client cert (maintenance mode)"
    except ssl.SSLError as e:
        return False, f"TLS rejected: {e}"
    except (OSError, TimeoutError) as e:
        return False, f"Connection error: {e}"


def _try_talosctl_insecure(host: str, timeout: float = 10.0) -> tuple[bool, str]:
    """Try `talosctl get machinestatus --insecure` as a secondary check.

    This is more reliable than raw TLS probing because it uses the actual
    Talos gRPC protocol. In maintenance mode, this returns machine status.
    In running mode, it fails with a TLS error.

    Falls back to TLS-based detection if talosctl is not available.
    """
    talosctl = shutil.which("talosctl")
    if talosctl is None:
        return False, "talosctl not found on PATH"

    try:
        result = subprocess.run(
            [talosctl, "get", "machinestatus", "--insecure", "--nodes", host, "--endpoints", host],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, f"talosctl insecure succeeded: {result.stdout[:200].strip()}"
        return False, f"talosctl insecure failed (rc={result.returncode}): {result.stderr[:200].strip()}"
    except subprocess.TimeoutExpired:
        return False, "talosctl insecure timed out"
    except OSError as e:
        return False, f"talosctl error: {e}"


def _try_talosctl_authenticated(
    host: str,
    talosconfig_path: str,
    timeout: float = 10.0,
) -> tuple[bool, str]:
    """Try `talosctl get machinestatus` with our talosconfig (authenticated).

    If this succeeds, the node is RUNNING and our certificates match
    (i.e., this Pulumi state's certs are the ones the node is using).
    """
    talosctl = shutil.which("talosctl")
    if talosctl is None:
        return False, "talosctl not found on PATH"

    try:
        result = subprocess.run(
            [
                talosctl,
                "get",
                "machinestatus",
                "--nodes",
                host,
                "--endpoints",
                host,
                "--talosconfig",
                talosconfig_path,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, f"Authenticated access succeeded: {result.stdout[:200].strip()}"
        return False, f"Authenticated access failed (rc={result.returncode}): {result.stderr[:200].strip()}"
    except subprocess.TimeoutExpired:
        return False, "talosctl authenticated timed out"
    except OSError as e:
        return False, f"talosctl error: {e}"


def _auth_detail(host: str, talosconfig_path: str | None) -> str:
    if not talosconfig_path:
        return ""
    auth_ok, auth_msg = _try_talosctl_authenticated(host, talosconfig_path)
    if auth_ok:
        return " — our talosconfig authenticates successfully"
    return f" — our talosconfig does NOT authenticate ({auth_msg})"


def detect_node_state(
    host: str,
    port: int = 50000,
    talosconfig_path: str | None = None,
) -> NodeStatus:
    """Detect the current state of a Talos node.

    Detection strategy:
      1. TCP port check — is the node reachable at all?
      2. talosctl insecure — does insecure mode work? (maintenance mode)
      3. TLS probe fallback — raw SSL handshake without client cert
      4. If both fail — node is RUNNING (requires mutual TLS)

    Args:
        host: Node IP address.
        port: Talos API port (default 50000).
        talosconfig_path: Optional path to talosconfig for authenticated check.

    Returns:
        NodeStatus with state and human-readable message.
    """
    port = int(port)

    # Step 1: TCP reachability
    if not _tcp_open(host, port):
        return NodeStatus(
            state=NodeState.UNREACHABLE,
            message=f"Node {host}:{port} is not reachable (TCP connection failed)",
        )

    # Step 2: Try talosctl insecure (most reliable maintenance mode detection)
    talosctl_ok, talosctl_msg = _try_talosctl_insecure(host)
    if talosctl_ok:
        return NodeStatus(
            state=NodeState.MAINTENANCE,
            message=f"Node {host} is in maintenance mode ({talosctl_msg})",
        )

    # TLS 1.3 caveat: raw ssl.CERT_NONE handshakes succeed on RUNNING nodes
    # because mTLS enforcement happens at gRPC application layer, not TLS transport.
    # When talosctl is available, trust its result over the raw TLS probe.
    talosctl_available = "talosctl not found" not in talosctl_msg
    cert_required = "certificate required" in talosctl_msg.lower()

    if talosctl_available and cert_required:
        return NodeStatus(
            state=NodeState.RUNNING,
            message=f"Node {host} is running (talosctl confirms mTLS required: {talosctl_msg})"
            f"{_auth_detail(host, talosconfig_path)}",
        )

    if talosctl_available:
        return NodeStatus(
            state=NodeState.RUNNING,
            message=f"Node {host} appears running (talosctl insecure failed unexpectedly: {talosctl_msg})"
            f"{_auth_detail(host, talosconfig_path)}",
        )

    tls_ok, tls_msg = _try_insecure_connect(host, port)
    if tls_ok:
        return NodeStatus(
            state=NodeState.MAINTENANCE,
            message=(
                f"Node {host} is in maintenance mode ({tls_msg})"
                " [WARNING: TLS probe only — install talosctl for reliable detection]"
            ),
        )

    return NodeStatus(
        state=NodeState.RUNNING,
        message=f"Node {host} is running (requires mutual TLS: {tls_msg}){_auth_detail(host, talosconfig_path)}",
    )


def log_node_state(status: NodeStatus) -> None:
    """Log the detected node state via Pulumi logging."""
    if status.state == NodeState.UNREACHABLE:
        pulumi.log.warn(f"[pre-flight] {status.message}")
    elif status.state == NodeState.MAINTENANCE:
        pulumi.log.info(f"[pre-flight] {status.message}")
    elif status.state == NodeState.RUNNING:
        pulumi.log.warn(f"[pre-flight] {status.message}")
