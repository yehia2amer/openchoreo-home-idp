from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, cast

import pulumi
import pulumi_kubernetes as k8s
import pulumiverse_talos as talos
import yaml

from check_node_state import NodeState, detect_node_state, log_node_state
from patches import PatchConfig, build_control_plane_patches
from wait_for_k8s_api import WaitForKubernetesAPI
from wait_for_talos_node import WaitForTalosNodeReady

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
cfg = pulumi.Config()

cluster_name = cfg.get("cluster_name") or "openchoreo"
cluster_endpoint_override = cfg.get("cluster_endpoint") or ""
talos_version = cfg.get("talos_version") or "v1.12.5"
kubernetes_version = cfg.get("kubernetes_version") or "1.33.0"

control_plane_node = cfg.get("control_plane_node") or "127.0.0.1"
talos_api_endpoint = cfg.get("talos_api_endpoint") or control_plane_node
kubernetes_api_host = cfg.get("kubernetes_api_host") or control_plane_node
kubernetes_api_port = cfg.get_int("kubernetes_api_port") or 6443

schematic_id = cfg.get("schematic_id") or ""
wipe_install_disk = cfg.get_bool("wipe_install_disk") or False

network_interface = cfg.get("network_interface") or "enp0s1"
network_addresses_raw = cfg.get("network_addresses") or "[]"
network_addresses: list[str] = json.loads(network_addresses_raw) if network_addresses_raw else []
network_gateway = cfg.get("network_gateway") or ""
dns_servers_raw = cfg.get("dns_servers") or '["8.8.8.8", "8.8.4.4"]'
dns_servers: list[str] = json.loads(dns_servers_raw)
cert_sans_raw = cfg.get("cert_sans") or "[]"
cert_sans: list[str] = json.loads(cert_sans_raw) if cert_sans_raw else []

longhorn_disk = cfg.get("longhorn_disk") or ""
install_disk_wwid = cfg.get("install_disk_wwid") or ""

enable_cloudflared = cfg.get_bool("enable_cloudflared") or False
cloudflared_token = cfg.get("cloudflared_token") or ""
enable_nvidia = cfg.get_bool("enable_nvidia") or False
enable_zfs = cfg.get_bool("enable_zfs") or False

cilium_version = cfg.get("cilium_version") or "1.17.6"
gateway_api_version = cfg.get("gateway_api_version") or "v1.3.0"
longhorn_version = cfg.get("longhorn_version") or "1.9.1"

# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------
kubernetes_endpoint = cluster_endpoint_override or f"https://{kubernetes_api_host}:{kubernetes_api_port}"

outputs_dir = str(Path(__file__).resolve().parent / "outputs")

# ---------------------------------------------------------------------------
# Build machine config patches via PatchConfig dataclass
# ---------------------------------------------------------------------------
patch_cfg = PatchConfig(
    cluster_name=cluster_name,
    cluster_endpoint=kubernetes_endpoint,
    schematic_id=schematic_id,
    talos_version=talos_version,
    wipe_install_disk=wipe_install_disk,
    network_interface=network_interface,
    network_addresses=network_addresses,
    network_gateway=network_gateway,
    dns_servers=dns_servers,
    cert_sans=cert_sans,
    longhorn_disk=longhorn_disk,
    install_disk_wwid=install_disk_wwid,
    control_plane_node=control_plane_node,
    enable_cloudflared=enable_cloudflared,
    cloudflared_token=cloudflared_token,
    enable_nvidia=enable_nvidia,
    enable_zfs=enable_zfs,
)

config_patches = build_control_plane_patches(patch_cfg)


# ---------------------------------------------------------------------------
# Helper: unwrap Talos provider opaque types
# ---------------------------------------------------------------------------
def as_client_configuration(config: pulumi.Input[object]) -> pulumi.Output[dict[str, pulumi.Input[str]]]:
    config_output = cast("pulumi.Output[object]", pulumi.Output.from_input(config))
    return config_output.apply(
        lambda value: {
            "ca_certificate": cast(dict[str, pulumi.Input[str]], value)["ca_certificate"],
            "client_certificate": cast(dict[str, pulumi.Input[str]], value)["client_certificate"],
            "client_key": cast(dict[str, pulumi.Input[str]], value)["client_key"],
        }
    )


def as_machine_client_configuration_input(
    config: pulumi.Input[object],
) -> pulumi.Output[talos.machine.ClientConfigurationArgs]:
    return as_client_configuration(config).apply(
        lambda value: talos.machine.ClientConfigurationArgs(
            ca_certificate=value["ca_certificate"],
            client_certificate=value["client_certificate"],
            client_key=value["client_key"],
        )
    )


def as_cluster_client_configuration_input(
    config: pulumi.Input[object],
) -> pulumi.Output[talos.cluster.KubeconfigClientConfigurationArgs]:
    return as_client_configuration(config).apply(
        lambda value: talos.cluster.KubeconfigClientConfigurationArgs(
            ca_certificate=value["ca_certificate"],
            client_certificate=value["client_certificate"],
            client_key=value["client_key"],
        )
    )


def as_machine_secrets(secrets: pulumi.Input[object]) -> pulumi.Output[dict[str, pulumi.Input[object]]]:
    secrets_output = cast("pulumi.Output[object]", pulumi.Output.from_input(secrets))
    return secrets_output.apply(
        lambda value: {
            "certs": cast(dict[str, pulumi.Input[object]], value)["certs"],
            "cluster": cast(dict[str, pulumi.Input[object]], value)["cluster"],
            "secrets": cast(dict[str, pulumi.Input[object]], value)["secrets"],
            "trustdinfo": cast(dict[str, pulumi.Input[object]], value)["trustdinfo"],
        }
    )


def as_machine_secrets_input(secrets: pulumi.Input[object]) -> pulumi.Output[talos.machine.MachineSecretsArgs]:
    return as_machine_secrets(secrets).apply(
        lambda value: talos.machine.MachineSecretsArgs(
            certs=cast(Any, value["certs"]),
            cluster=cast(Any, value["cluster"]),
            secrets=cast(Any, value["secrets"]),
            trustdinfo=cast(Any, value["trustdinfo"]),
        )
    )


# ---------------------------------------------------------------------------
# Output file helpers — write to project-local outputs/ (matching Terraform)
# ---------------------------------------------------------------------------
def render_talosconfig(client_config: talos.machine.ClientConfigurationArgs) -> str:
    talosconfig = {
        "context": cluster_name,
        "contexts": {
            cluster_name: {
                "endpoints": [talos_api_endpoint],
                "nodes": [control_plane_node],
                "ca": client_config.ca_certificate,
                "crt": client_config.client_certificate,
                "key": client_config.client_key,
            }
        },
    }
    return yaml.safe_dump(talosconfig, sort_keys=False)


def _write_file(path: str, content: str, mode: int = 0o600) -> str:
    """Write content to path with specified permissions, creating parent dirs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    os.chmod(path, mode)
    return path


def persist_talosconfig(client_config: talos.machine.ClientConfigurationArgs) -> str:
    raw = render_talosconfig(client_config)
    return _write_file(os.path.join(outputs_dir, "talosconfig"), raw, 0o600)


def persist_kubeconfig(raw: str) -> str:
    return _write_file(os.path.join(outputs_dir, "kubeconfig"), raw, 0o600)


def persist_controlplane_yaml(machine_configuration: str) -> str:
    return _write_file(os.path.join(outputs_dir, "controlplane.yaml"), machine_configuration, 0o644)


def persist_machine_secrets(secrets_dict: dict[str, Any]) -> str:
    return _write_file(
        os.path.join(outputs_dir, "machine-secrets.yaml"), yaml.safe_dump(secrets_dict, sort_keys=False), 0o600
    )


# ===================================================================
# PRE-FLIGHT — Detect node state before declaring resources
# ===================================================================
# This runs at program-time (before Pulumi creates resources) to determine
# whether the node is in maintenance mode (needs full bootstrap) or already
# running (skip config apply + bootstrap, go straight to kubeconfig).
#
# States:
#   MAINTENANCE  → full pipeline: config_apply → wait → bootstrap → kubeconfig
#   RUNNING      → skip config_apply/wait/bootstrap, get kubeconfig directly
#   UNREACHABLE  → full pipeline (node may be booting / rebooting into maintenance)

node_status = detect_node_state(
    host=control_plane_node,
    port=50000,
    talosconfig_path=os.path.join(outputs_dir, "talosconfig"),
)
log_node_state(node_status)

node_needs_bootstrap = node_status.state in (NodeState.MAINTENANCE, NodeState.UNREACHABLE)

if node_status.state == NodeState.RUNNING:
    pulumi.log.info(
        "[pre-flight] Node is already running — will skip ConfigurationApply and Bootstrap. "
        "Machine secrets and kubeconfig will still be managed."
    )
elif node_status.state == NodeState.UNREACHABLE:
    pulumi.log.warn(
        "[pre-flight] Node is unreachable — assuming it will come up in maintenance mode. "
        "Full bootstrap pipeline will run."
    )

# ===================================================================
# PHASE 1 — Talos Cluster Bootstrap (matches Terraform apply-bootstrap)
# ===================================================================
machine_secrets = talos.machine.Secrets("machine-secrets", talos_version=talos_version)
machine_client_configuration = as_machine_client_configuration_input(machine_secrets.client_configuration)
cluster_client_configuration = as_cluster_client_configuration_input(machine_secrets.client_configuration)
machine_secrets_input = as_machine_secrets_input(machine_secrets.machine_secrets)

machine_config = talos.machine.get_configuration_output(
    cluster_name=cluster_name,
    machine_type="controlplane",
    cluster_endpoint=kubernetes_endpoint,
    machine_secrets=machine_secrets_input,
    talos_version=talos_version,
    kubernetes_version=kubernetes_version,
    config_patches=config_patches,
)

# ---------------------------------------------------------------------------
# Conditional: only apply config + bootstrap if node needs it
# ---------------------------------------------------------------------------
# These variables hold the resources (or None) so downstream deps can reference them.
config_apply: talos.machine.ConfigurationApply | None = None
wait_node_ready: WaitForTalosNodeReady | None = None
bootstrap: talos.machine.Bootstrap | None = None

if node_needs_bootstrap:
    config_apply = talos.machine.ConfigurationApply(
        "control-plane-config",
        client_configuration=machine_client_configuration,
        machine_configuration_input=machine_config.machine_configuration,
        node=control_plane_node,
        endpoint=talos_api_endpoint,
        apply_mode="auto",
        timeouts={"create": "20m", "update": "20m"},
    )

    # Wait for node to come back online after config apply (reboot)
    # Phase 1: TCP check on Talos gRPC port 50000 (fast, no deps)
    # Phase 2: talosctl health for full readiness (etcd, kubelet, time sync)
    wait_node_ready = WaitForTalosNodeReady(
        "wait-talos-node-ready",
        node=control_plane_node,
        endpoint=talos_api_endpoint,
        talosconfig_path=os.path.join(outputs_dir, "talosconfig"),
        timeout=600,
        poll_interval=10,
        opts=pulumi.ResourceOptions(depends_on=[config_apply]),
    )

    bootstrap = talos.machine.Bootstrap(
        "bootstrap",
        node=control_plane_node,
        endpoint=talos_api_endpoint,
        client_configuration=machine_client_configuration,
        opts=pulumi.ResourceOptions(depends_on=[wait_node_ready]),
    )

# Kubeconfig always runs — depends on bootstrap when bootstrapping, otherwise
# just on machine_secrets (the node is already running and has a working API).
kubeconfig_deps: list[pulumi.Resource] = []
if bootstrap is not None:
    kubeconfig_deps.append(bootstrap)
else:
    kubeconfig_deps.append(machine_secrets)

kubeconfig = talos.cluster.Kubeconfig(
    "kubeconfig",
    client_configuration=cluster_client_configuration,
    node=control_plane_node,
    endpoint=talos_api_endpoint,
    timeouts={"create": "20m", "update": "20m"},
    opts=pulumi.ResourceOptions(depends_on=kubeconfig_deps),
)

# ---------------------------------------------------------------------------
# Phase 1 output files — written to outputs/ directory (matching Terraform)
# ---------------------------------------------------------------------------
talosconfig_file = machine_client_configuration.apply(persist_talosconfig)
talosconfig_raw = machine_client_configuration.apply(render_talosconfig)
kubeconfig_file = kubeconfig.kubeconfig_raw.apply(persist_kubeconfig)
controlplane_file = machine_config.machine_configuration.apply(persist_controlplane_yaml)
machine_secrets_file = as_machine_secrets(machine_secrets.machine_secrets).apply(persist_machine_secrets)

# ===================================================================
# PHASE 2 — Post-Install (matches Terraform post-install)
# ===================================================================

# ---------------------------------------------------------------------------
# Wait for Kubernetes API to become ready after bootstrap
# ---------------------------------------------------------------------------
# After bootstrap the K8s API server takes ~30-60s to come up (etcd → kubelet
# → kube-apiserver static pod). Without this wait, K8s resources fail with
# "connection refused" on port 6443.
wait_k8s_api: WaitForKubernetesAPI | None = None
if node_needs_bootstrap:
    wait_k8s_api = WaitForKubernetesAPI(
        "wait-k8s-api-ready",
        host=kubernetes_api_host,
        port=kubernetes_api_port,
        timeout=600,
        poll_interval=10,
        initial_delay=15,
        opts=pulumi.ResourceOptions(depends_on=[kubeconfig]),
    )

# Build dynamic dependency list for k8s_provider:
#   - After bootstrap: depend on wait_k8s_api (which transitively depends on kubeconfig → bootstrap)
#   - Already running: depend directly on kubeconfig (no wait needed)
k8s_provider_deps: list[pulumi.Resource] = []
if wait_k8s_api is not None:
    k8s_provider_deps.append(wait_k8s_api)
else:
    k8s_provider_deps.append(kubeconfig)

# Kubernetes provider using the kubeconfig from Phase 1
k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=kubeconfig.kubeconfig_raw,
    opts=pulumi.ResourceOptions(depends_on=k8s_provider_deps),
)

# ---------------------------------------------------------------------------
# Step 7: Gateway API CRDs
# ---------------------------------------------------------------------------
GATEWAY_API_CRDS = {
    "gatewayclasses": f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/standard/gateway.networking.k8s.io_gatewayclasses.yaml",
    "gateways": f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/standard/gateway.networking.k8s.io_gateways.yaml",
    "httproutes": f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/standard/gateway.networking.k8s.io_httproutes.yaml",
    "referencegrants": f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/standard/gateway.networking.k8s.io_referencegrants.yaml",
    "grpcroutes": f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/standard/gateway.networking.k8s.io_grpcroutes.yaml",
    "tlsroutes": f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/experimental/gateway.networking.k8s.io_tlsroutes.yaml",
}

gateway_api_crd_resources: list[k8s.yaml.ConfigFile] = []
for name, url in GATEWAY_API_CRDS.items():
    crd = k8s.yaml.ConfigFile(
        f"gateway-api-crd-{name}",
        file=url,
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[kubeconfig]),
    )
    gateway_api_crd_resources.append(crd)

# ---------------------------------------------------------------------------
# Step 8: Cilium Helm chart
# ---------------------------------------------------------------------------
CILIUM_VALUES: dict[str, Any] = {
    "ipam": {"mode": "kubernetes"},
    "kubeProxyReplacement": True,
    "bpf": {"hostLegacyRouting": True},
    "securityContext": {
        "capabilities": {
            "ciliumAgent": [
                "CHOWN",
                "KILL",
                "NET_ADMIN",
                "NET_RAW",
                "IPC_LOCK",
                "SYS_ADMIN",
                "SYS_RESOURCE",
                "DAC_OVERRIDE",
                "FOWNER",
                "SETGID",
                "SETUID",
            ],
            "cleanCiliumState": ["NET_ADMIN", "SYS_ADMIN", "SYS_RESOURCE"],
        }
    },
    "cgroup": {
        "autoMount": {"enabled": False},
        "hostRoot": "/sys/fs/cgroup",
    },
    "k8sServiceHost": "localhost",
    "k8sServicePort": "7445",
    "l2announcements": {"enabled": True},
    "gatewayAPI": {
        "enabled": True,
        "enableAlpn": True,
        "enableAppProtocol": True,
    },
    "operator": {"replicas": 1},
    "hubble": {
        "enabled": True,
        "relay": {"enabled": True},
        "ui": {"enabled": True},
    },
}

cilium = k8s.helm.v3.Release(
    "cilium",
    name="cilium",
    chart="cilium",
    version=cilium_version,
    namespace="kube-system",
    repository_opts=k8s.helm.v3.RepositoryOptsArgs(
        repo="https://helm.cilium.io/",
    ),
    values=CILIUM_VALUES,
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=gateway_api_crd_resources,
    ),
)

# ---------------------------------------------------------------------------
# Step 9: cilium-secrets namespace — privileged pod security label
# ---------------------------------------------------------------------------
cilium_secrets_ns_labels = k8s.core.v1.NamespacePatch(
    "cilium-secrets-namespace-labels",
    metadata=k8s.meta.v1.ObjectMetaPatchArgs(
        name="cilium-secrets",
        labels={
            "pod-security.kubernetes.io/enforce": "privileged",
        },
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[cilium],
    ),
)

# ---------------------------------------------------------------------------
# Step 10: Longhorn storage
# ---------------------------------------------------------------------------
longhorn_ns = k8s.core.v1.Namespace(
    "longhorn-system",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="longhorn-system",
        labels={
            "pod-security.kubernetes.io/enforce": "privileged",
            "pod-security.kubernetes.io/audit": "privileged",
            "pod-security.kubernetes.io/warn": "privileged",
        },
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[cilium],
    ),
)

# ---------------------------------------------------------------------------
# Step 11: External snapshotter (CRDs + controller)
# ---------------------------------------------------------------------------
SNAPSHOT_CRD_VERSION = "v8.3.0"

snapshot_crds = k8s.yaml.v2.ConfigGroup(
    "external-snapshotter-crds",
    files=[
        f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml",
        f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml",
        f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml",
    ],
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[longhorn_ns],
    ),
)

snapshot_controller = k8s.yaml.v2.ConfigGroup(
    "snapshot-controller",
    files=[
        f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml",
        f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml",
    ],
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[snapshot_crds],
    ),
)

# ---------------------------------------------------------------------------
# Step 12: Longhorn storage (Helm release)
# ---------------------------------------------------------------------------
LONGHORN_VALUES: dict[str, Any] = {
    "preUpgradeChecker": {
        "jobEnabled": False,
    },
    "defaultSettings": {
        "defaultReplicaCount": 1,
        "defaultDataPath": "/var/lib/longhorn",
    },
    "persistence": {
        "defaultFsType": "ext4",
        "reclaimPolicy": "Retain",
        "defaultClassReplicaCount": 1,
    },
}

longhorn = k8s.helm.v3.Release(
    "longhorn",
    name="longhorn",
    chart="longhorn",
    version=longhorn_version,
    namespace="longhorn-system",
    repository_opts=k8s.helm.v3.RepositoryOptsArgs(
        repo="https://charts.longhorn.io",
    ),
    values=LONGHORN_VALUES,
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[longhorn_ns, snapshot_controller],
    ),
)

# ===================================================================
# Exports
# ===================================================================
pulumi.export("cluster_name", cluster_name)
pulumi.export("control_plane_ip", control_plane_node)
pulumi.export("kubeconfig_raw", pulumi.Output.secret(kubeconfig.kubeconfig_raw))
pulumi.export("talosconfig_raw", pulumi.Output.secret(talosconfig_raw))
pulumi.export("talos_version", talos_version)
pulumi.export("kubernetes_version", kubernetes_version)
pulumi.export("kubernetes_endpoint", kubernetes_endpoint)
pulumi.export(
    "written_files",
    {
        "talosconfig": talosconfig_file,
        "controlplane": controlplane_file,
        "kubeconfig": kubeconfig_file,
        "machine_secrets": machine_secrets_file,
    },
)
