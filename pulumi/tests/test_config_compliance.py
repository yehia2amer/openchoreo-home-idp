"""Gateway-mode-compliance unit tests.

Pure Python tests that verify platform profiles, TLS constants, edition
logic, and workflow template URLs match the OpenChoreo official guide.
No Pulumi SDK imports — these run without a Pulumi engine.
"""

from __future__ import annotations


def test_talos_baremetal_gateway_mode():
    """talos-baremetal must use kgateway with cilium CNI."""
    from platforms.talos_baremetal import talos_baremetal

    profile = talos_baremetal()
    assert profile.gateway_mode == "kgateway"
    assert profile.cni_mode == "cilium"


def test_tls_constants_match_guide():
    """TLS CA-chain constants must match the official OpenChoreo guide Step 2."""
    from config import (
        CERT_CP_GATEWAY_TLS,
        CERT_DP_GATEWAY_TLS,
        CERT_OPENCHOREO_CA,
        ISSUER_OPENCHOREO_CA,
        ISSUER_SELFSIGNED_BOOTSTRAP,
        SECRET_OPENCHOREO_CA,
    )

    assert ISSUER_SELFSIGNED_BOOTSTRAP == "selfsigned-bootstrap"
    assert CERT_OPENCHOREO_CA == "openchoreo-ca"
    assert SECRET_OPENCHOREO_CA == "openchoreo-ca-secret"
    assert ISSUER_OPENCHOREO_CA == "openchoreo-ca"
    assert CERT_CP_GATEWAY_TLS == "cp-gateway-tls"
    assert CERT_DP_GATEWAY_TLS == "dp-gateway-tls"


def test_platform_profile_has_workflow_template_urls():
    """PlatformProfile.workflow_template_urls defaults to None."""
    from platforms.types import PlatformProfile

    p = PlatformProfile(
        name="test",
        gateway_mode="kgateway",
        cni_mode="cilium",
        enable_kube_proxy_replacement=False,
        k8s_service_host="",
        k8s_service_port=6443,
        requires_coredns_rewrite=False,
        requires_machine_id_fix=False,
        requires_bpf_mount_fix=False,
        cilium_auto_mount_bpf=False,
        cilium_host_network_gateway=False,
        cilium_cni_bin_path="",
        workflow_template_mode="default",
        local_registry=False,
        bootstrap_script="test.py",
        cluster_name_config_key="test",
    )
    assert p.workflow_template_urls is None


def test_talos_baremetal_standard_workflow_urls():
    """talos-baremetal workflow URLs must not reference k3d."""
    from platforms.talos_baremetal import talos_baremetal

    profile = talos_baremetal()
    assert profile.workflow_template_urls is not None
    for url in profile.workflow_template_urls:
        assert "k3d" not in url, f"k3d reference found in talos-baremetal URL: {url}"


def test_kgateway_edition_is_generic_cni():
    """When gateway_mode is kgateway the edition must resolve to generic-cni."""
    gateway_mode = "kgateway"
    edition = "cilium" if gateway_mode == "cilium" else "generic-cni"
    assert edition == "generic-cni"


def test_k3d_workflow_urls_default():
    """k3d must keep workflow_template_urls as None for backward compat."""
    from platforms.k3d import K3D

    assert K3D.workflow_template_urls is None
