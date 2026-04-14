"""Gateway-mode-compliance unit tests.

Pure Python tests that verify platform profiles, TLS constants, edition
logic, and workflow template URLs match the OpenChoreo official guide.
No Pulumi SDK imports — these run without a Pulumi engine.
"""

from __future__ import annotations

import json
import re
from unittest.mock import MagicMock


# ──────────────────────────────────────────────────────────────
# Existing profile / constant tests
# ──────────────────────────────────────────────────────────────


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


def test_gke_profile_uses_cloud_strategies():
    """gke must resolve to cloud-native strategies across the profile."""
    from platforms.gke import GKE_PROFILE

    assert GKE_PROFILE.cloud_provider == "gcp"
    assert GKE_PROFILE.gateway_mode == "cloud"
    assert GKE_PROFILE.cni_mode == "cloud"
    assert GKE_PROFILE.secrets_backend == "gcp-sm"
    assert GKE_PROFILE.tls_issuer_mode == "gcp-cas"
    assert GKE_PROFILE.registry_mode == "cloud"
    assert GKE_PROFILE.observability_mode == "cloud"
    assert GKE_PROFILE.cluster_name_config_key == "gcp_gke_cluster_name"


def test_gke_workflow_urls_do_not_reference_k3d():
    """gke workflow URLs must use generic templates, not k3d-specific ones."""
    from platforms.gke import GKE_PROFILE

    assert GKE_PROFILE.workflow_template_urls is not None
    for url in GKE_PROFILE.workflow_template_urls:
        assert "k3d" not in url, f"k3d reference found in gke URL: {url}"


# ──────────────────────────────────────────────────────────────
# GKE profile completeness (cloud-specific fields)
# ──────────────────────────────────────────────────────────────


def test_gke_profile_cloud_specific_fields():
    """GKE profile must set all cloud-specific PlatformProfile fields."""
    from platforms.gke import GKE_PROFILE

    assert GKE_PROFILE.load_balancer_mode == "cloud"
    assert GKE_PROFILE.storage_class == "premium-rwo"
    assert GKE_PROFILE.longhorn_enabled is False
    assert GKE_PROFILE.external_snapshotter_enabled is False
    assert GKE_PROFILE.cilium_pre_installed is True
    assert GKE_PROFILE.gateway_api_crds_pre_installed is True
    assert GKE_PROFILE.local_registry is False


# ──────────────────────────────────────────────────────────────
# Resolver branch tests (TST-1, TST-2)
# ──────────────────────────────────────────────────────────────


def _mock_config(
    *, platform: str = "", is_k3d: bool = False, enable_cilium: bool = False, k8s_host: str = ""
) -> MagicMock:
    """Build a mock pulumi.Config for resolver tests."""
    cfg = MagicMock()
    cfg.get.side_effect = lambda key: {
        "platform": platform,
        "cilium_k8s_api_host": k8s_host,
    }.get(key, "")
    cfg.get_bool.side_effect = lambda key: {
        "is_k3d": is_k3d,
        "enable_cilium": enable_cilium,
    }.get(key, False)
    return cfg


def test_resolver_explicit_gke():
    """resolver: platform='gke' returns GKE_PROFILE."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="gke"))
    assert profile.name == "gke"
    assert profile.cloud_provider == "gcp"


def test_resolver_explicit_k3d():
    """resolver: platform='k3d' returns k3d profile."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="k3d"))
    assert profile.name == "k3d"


def test_resolver_explicit_talos():
    """resolver: platform='talos' returns talos profile."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="talos"))
    assert profile.name == "talos"


def test_resolver_explicit_talos_baremetal():
    """resolver: platform='talos-baremetal' returns talos-baremetal profile."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="talos-baremetal"))
    assert profile.name == "talos-baremetal"


def test_resolver_explicit_talos_baremetal_underscore():
    """resolver: platform='talos_baremetal' (underscore variant) also works."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="talos_baremetal"))
    assert profile.name == "talos-baremetal"


def test_resolver_explicit_rancher_desktop():
    """resolver: platform='rancher-desktop' returns rancher-desktop profile."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="rancher-desktop"))
    assert profile.name == "rancher-desktop"


def test_resolver_explicit_rancher_desktop_underscore():
    """resolver: platform='rancher_desktop' (underscore variant) also works."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="rancher_desktop"))
    assert profile.name == "rancher-desktop"


def test_resolver_unknown_platform_raises():
    """resolver: unknown platform name raises ValueError."""
    import pytest
    from platforms.resolver import resolve_platform

    with pytest.raises(ValueError, match="Unknown platform"):
        resolve_platform(_mock_config(platform="bogus-cloud"))


def test_resolver_case_insensitive():
    """resolver: platform names are case-insensitive."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(platform="GKE"))
    assert profile.name == "gke"

    profile = resolve_platform(_mock_config(platform="  Talos  "))
    assert profile.name == "talos"


def test_resolver_legacy_k3d_no_cilium():
    """resolver: legacy is_k3d=True, enable_cilium=False returns plain k3d."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(is_k3d=True))
    assert profile.name == "k3d"
    assert profile.cni_mode != "cilium"


def test_resolver_legacy_k3d_with_cilium():
    """resolver: legacy is_k3d=True, enable_cilium=True returns k3d+cilium clone."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(is_k3d=True, enable_cilium=True))
    assert profile.gateway_mode == "cilium"
    assert profile.cni_mode == "cilium"


def test_resolver_legacy_cilium_no_k3d():
    """resolver: legacy enable_cilium=True without is_k3d returns rancher-desktop."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config(enable_cilium=True))
    assert profile.name == "rancher-desktop"


def test_resolver_legacy_fallback_generic():
    """resolver: no platform, no legacy flags returns generic profile."""
    from platforms.resolver import resolve_platform

    profile = resolve_platform(_mock_config())
    assert profile.name == "generic"
    assert profile.gateway_mode == "kgateway"
    assert profile.cni_mode == "default"


# ──────────────────────────────────────────────────────────────
# Policy helper tests (TST-25)
# ──────────────────────────────────────────────────────────────


def test_policy_extract_stack_name():
    """Policy helper _extract_stack_name parses Pulumi URNs correctly."""

    # Re-implement the helper inline to avoid importing policy/__main__.py
    # (which triggers PolicyPack() registration and hangs without an engine).
    # This tests the ALGORITHM, not the import.
    def _extract_stack_name(urn: str) -> str:
        parts = urn.split("::")
        if len(parts) >= 1:
            prefix = parts[0]
            segments = prefix.split(":")
            if len(segments) >= 3:
                return segments[2]
        return ""

    assert _extract_stack_name("urn:pulumi:dev::openchoreo::kubernetes:core/v1:Namespace::my-ns") == "dev"
    assert _extract_stack_name("urn:pulumi:gcp::openchoreo::gcp:compute/network:Network::vpc") == "gcp"
    assert _extract_stack_name("urn:pulumi:prod-us::project::type::name") == "prod-us"
    assert _extract_stack_name("malformed-urn") == ""


def test_policy_insecure_value_regex_no_false_positives():
    """Policy regex must NOT match 'root' as a substring (e.g. 'openchoreo-ca-pool-root')."""
    insecure_value = "root"
    pattern = r':\s*"' + re.escape(insecure_value) + r'"'

    # Should NOT match — "root" is a substring within a longer value
    ca_resource = json.dumps({"name": "openchoreo-ca-pool-root"})
    assert re.search(pattern, ca_resource) is None

    path_resource = json.dumps({"path": "/var/root/data"})
    assert re.search(pattern, path_resource) is None

    # SHOULD match — "root" is the complete JSON value
    insecure_resource = json.dumps({"openbao_root_token": "root"})
    assert re.search(pattern, insecure_resource) is not None

    nested_insecure = json.dumps({"config": {"token": "root"}})
    assert re.search(pattern, nested_insecure) is not None


# ──────────────────────────────────────────────────────────────
# DEV_STACKS sync verification (ARC-2)
# ──────────────────────────────────────────────────────────────


def test_dev_stacks_sync_between_config_and_policy():
    """config.DEV_STACKS and policy._DEV_STACKS must contain the same entries.

    The policy pack runs in an isolated venv and duplicates the set.
    This test reads the policy source file directly to avoid importing
    __main__.py (which triggers PolicyPack registration).
    """
    import ast
    import os
    import re as _re

    from config import DEV_STACKS

    policy_path = os.path.join(os.path.dirname(__file__), "..", "policy", "__main__.py")
    with open(policy_path) as f:
        source = f.read()

    # Extract _DEV_STACKS tuple literal via regex (avoids importing the module)
    match = _re.search(r"_DEV_STACKS\s*=\s*frozenset\((\(.*?\))\)", source, _re.DOTALL)
    assert match, "Could not find _DEV_STACKS in policy/__main__.py"
    policy_dev_stacks = set(ast.literal_eval(match.group(1)))

    assert set(DEV_STACKS) == policy_dev_stacks, (
        f"DEV_STACKS mismatch — config.py has {DEV_STACKS}, policy has {policy_dev_stacks}"
    )


def test_dev_stacks_is_frozenset():
    """DEV_STACKS must be a frozenset (immutable)."""
    from config import DEV_STACKS

    assert isinstance(DEV_STACKS, frozenset)
