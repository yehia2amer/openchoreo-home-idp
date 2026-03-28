"""Helper: copy cluster-gateway-ca ConfigMap from control-plane to target namespace."""

from __future__ import annotations

import pulumi

from config import NS_CONTROL_PLANE, SECRET_GATEWAY_CA, OpenChoreoConfig
from helpers.dynamic_providers import CopyCA


def copy_ca(
    name: str,
    target_namespace: str,
    cfg: OpenChoreoConfig,
    opts: pulumi.ResourceOptions | None = None,
) -> CopyCA:
    """Copy cluster-gateway-ca secret from control-plane namespace as a ConfigMap."""
    return CopyCA(
        f"copy-ca-{name}",
        kubeconfig_path=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
        secret_name=SECRET_GATEWAY_CA,
        source_namespace=NS_CONTROL_PLANE,
        configmap_name=SECRET_GATEWAY_CA,
        target_namespace=target_namespace,
        opts=opts,
    )
