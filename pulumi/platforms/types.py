"""Typed platform profile — describes infrastructure capabilities and quirks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformProfile:
    """Normalized description of what the target platform requires.

    Components should branch on these fields instead of raw booleans
    like ``is_k3d`` or ``enable_cilium``.
    """

    # ── Identity ──
    name: str
    """Canonical platform name (e.g. ``k3d``, ``rancher-desktop``, ``talos``)."""

    # ── Networking / CNI ──
    gateway_mode: str
    """Which gateway controller to use: ``kgateway``, ``cilium``, or ``cloud``."""

    cni_mode: str
    """CNI strategy: ``flannel`` (k3d default), ``cilium``, or ``cloud``."""

    enable_kube_proxy_replacement: bool
    """Whether Cilium should replace kube-proxy (unsafe on k3d)."""

    k8s_service_host: str
    """Direct API-server IP for Cilium kube-proxy replacement. Empty if unneeded."""

    k8s_service_port: int
    """API-server port for Cilium kube-proxy replacement (default 6443, Talos KubePrism: 7445)."""

    # ── Node / host fixes ──
    requires_coredns_rewrite: bool
    """Apply k3d-style CoreDNS ConfigMap rewrite."""

    requires_machine_id_fix: bool
    """Generate ``/etc/machine-id`` inside container nodes (k3d Fluent Bit fix)."""

    requires_bpf_mount_fix: bool
    """Run a privileged Job to make ``/sys/fs/bpf`` a shared mount (Rancher Desktop)."""

    # ── Cilium tuning ──
    cilium_auto_mount_bpf: bool
    """Let Cilium auto-mount BPF and cgroup file systems."""

    cilium_host_network_gateway: bool
    """Enable ``hostNetwork`` on the Cilium gateway envoy proxy."""

    cilium_cni_bin_path: str
    """Override path for CNI binaries (Rancher Desktop uses ``/usr/libexec/cni``)."""

    # ── Bootstrap ──
    bootstrap_script: str
    """Name of the bootstrap helper (e.g. ``bootstrap_k3d.py``), or empty if external."""

    # ── Cluster ──
    cluster_name_config_key: str
    """Stack config key that carries the cluster name, or empty."""

    # ── Workflow / registry ──
    workflow_template_mode: str
    """How workflow templates handle registry/gateway URLs: ``k3d-patch`` or ``default``."""

    local_registry: bool
    """Whether a local Docker registry is expected to be part of the stack."""

    # ── Platform strategies ──
    cloud_provider: str = "none"
    """Infrastructure provider: ``none``, ``gcp``, ``aws``, ``azure``."""

    registry_mode: str = "local"
    """Container registry strategy: ``local`` or ``cloud``."""

    secrets_backend: str = "openbao"
    """Secrets strategy: ``openbao`` or ``gcp-sm``."""

    tls_issuer_mode: str = "self-signed"
    """TLS issuer strategy: ``self-signed``, ``gcp-cas``, etc."""

    observability_mode: str = "self-hosted"
    """Observability strategy: ``self-hosted`` or ``cloud``."""

    load_balancer_mode: str = "local"
    """Load balancer strategy: ``local``, ``cilium-l2``, or ``cloud``."""

    storage_class: str = ""
    """Default storage class expected by the platform."""

    longhorn_enabled: bool = False
    """Whether Longhorn storage is part of the platform bootstrap."""

    external_snapshotter_enabled: bool = False
    """Whether CSI external-snapshotter is expected on the cluster."""

    # ── Workflow template overrides ───────────────────────────────
    workflow_template_urls: tuple[str, ...] | None = None
    """Platform-specific workflow template filenames; None falls back to k3d defaults."""

    # ── Bare-metal Cilium L2 ──────────────────────────────────────
    cilium_bpf_host_legacy_routing: bool = False
    cilium_l2_announcements_enabled: bool = False
    cilium_l2_ip_pool_cidrs: tuple[str, ...] = ()
    cilium_l2_interfaces: tuple[str, ...] = ()

    # ── Phase 1 pre-install flags ─────────────────────────────────
    # Whether Cilium was pre-installed by Phase 1 (e.g. talos-cluster-baremetal)
    cilium_pre_installed: bool = False
    gateway_api_crds_pre_installed: bool = False
