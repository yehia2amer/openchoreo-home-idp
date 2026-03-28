"""Helper: wait for TLS secret and register a cluster plane CRD."""

from __future__ import annotations

import pulumi

from config import TIMEOUT_TLS_WAIT, OpenChoreoConfig
from helpers.dynamic_providers import RegisterPlane


def register_plane(
    name: str,
    namespace: str,
    kind: str,
    cfg: OpenChoreoConfig,
    extra_spec: dict | None = None,
    secret_store_ref: dict | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> RegisterPlane:
    """Wait for cluster-agent-tls and register a ClusterXxxPlane CRD.

    Returns a single RegisterPlane dynamic resource (replaces the old (wait_cmd, register_cmd) tuple).
    """
    return RegisterPlane(
        f"register-{name}",
        kubeconfig_path=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
        namespace=namespace,
        kind=kind,
        extra_spec=extra_spec,
        secret_store_ref=secret_store_ref,
        timeout=TIMEOUT_TLS_WAIT,
        opts=opts,
    )
