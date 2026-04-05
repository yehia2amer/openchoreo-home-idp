# Talos Bare-Metal Cluster

Nested Pulumi project for bootstrapping bare-metal Talos Linux clusters.

## Overview

This project handles the full lifecycle of a bare-metal Talos cluster:
- Phase 1: Talos bootstrap (machine secrets, config apply, bootstrap)
- Phase 2: Post-install (Cilium CNI, Longhorn storage, Gateway API)

## Architecture

```
talos-cluster-baremetal/
├── __main__.py              # Main orchestration (2 phases)
├── patches.py               # PatchConfig dataclass + patch builders
├── check_node_state.py      # Pre-flight node state detection
├── wait_for_talos_node.py   # Dynamic provider: wait for Talos API
├── wait_for_k8s_api.py      # Dynamic provider: wait for K8s API
├── tests/                   # pytest tests for patch generation
├── outputs/                 # Generated credentials (gitignored)
│   ├── talosconfig          # Talos client config
│   ├── kubeconfig           # Kubernetes kubeconfig
│   ├── controlplane.yaml    # Generated machine config
│   └── machine-secrets.yaml # Cluster secrets
└── Pulumi.dev.yaml          # Stack config with node details
```

## Node State Detection

Before declaring resources, `check_node_state.py` probes the node:

| State | Meaning | Action |
|-------|---------|--------|
| `MAINTENANCE` | Node in maintenance mode | Full bootstrap pipeline |
| `RUNNING` | Cluster already running | Skip config apply + bootstrap |
| `UNREACHABLE` | Node not responding | Assume maintenance, full pipeline |

This enables idempotent `pulumi up` - re-running after a successful deploy skips bootstrap.

## Deployment Phases

### Phase 1: Talos Bootstrap

1. Generate machine secrets
2. Build machine config with patches
3. Apply config to node (triggers reboot)
4. Wait for Talos API (50000/tcp)
5. Bootstrap cluster (etcd init)
6. Generate kubeconfig

### Phase 2: Post-Install

7. Wait for Kubernetes API (6443/tcp)
8. Install Gateway API CRDs
9. Install Cilium CNI (with L2 announcements)
10. Create Longhorn namespace
11. Install external-snapshotter CRDs
12. Install Longhorn storage
13. Create VolumeSnapshotClass

## Configuration

### Required Settings

```yaml
# Pulumi.dev.yaml
config:
  openchoreo:control_plane_node: "192.168.1.100"
  openchoreo:network_addresses: '["192.168.1.100/24"]'
  openchoreo:network_gateway: "192.168.1.1"
  openchoreo:cluster_endpoint: "https://192.168.1.100:6443"
```

### Optional Settings

| Config | Default | Description |
|--------|---------|-------------|
| `cluster_name` | `openchoreo` | Talos cluster name |
| `talos_version` | `v1.12.5` | Talos Linux version |
| `kubernetes_version` | `1.33.0` | Kubernetes version |
| `schematic_id` | (none) | Image Factory schematic |
| `wipe_install_disk` | `false` | Wipe disk on install |
| `longhorn_disk` | (none) | Dedicated Longhorn disk |
| `enable_cloudflared` | `false` | Install Cloudflare tunnel |
| `enable_nvidia` | `false` | Enable NVIDIA GPU support |
| `enable_zfs` | `false` | Enable ZFS storage |

## Patch System

`patches.py` builds Talos machine config patches using a `PatchConfig` dataclass:

```python
from patches import PatchConfig, build_control_plane_patches

cfg = PatchConfig(
    cluster_name="openchoreo",
    cluster_endpoint="https://192.168.1.100:6443",
    network_interface="enp0s1",
    network_addresses=["192.168.1.100/24"],
    # ... more settings
)

patches = build_control_plane_patches(cfg)
```

### Patch Categories

| Patch | Purpose |
|-------|---------|
| `cluster_name_patch` | Sets cluster name in Talos config |
| `install_disk_patch` | Configures install disk (WWID or auto) |
| `static_network_patch` | Static IP, gateway, DNS |
| `cert_sans_patch` | Additional SANs for API cert |
| `kubelet_extra_mounts_patch` | Mounts for containerd/kubelet |
| `longhorn_disk_patch` | Dedicated disk for Longhorn |
| `cloudflared_patch` | Cloudflare tunnel sidecar |
| `nvidia_patch` | NVIDIA container runtime |
| `zfs_patch` | ZFS kernel module |

## Dynamic Providers

### WaitForTalosNodeReady

Waits for Talos API on port 50000, then runs `talosctl health`:

```python
WaitForTalosNodeReady(
    "wait-talos",
    node="192.168.1.100",
    endpoint="192.168.1.100",
    talosconfig_path="outputs/talosconfig",
    timeout=600,
)
```

### WaitForKubernetesAPI

Waits for Kubernetes API on port 6443:

```python
WaitForKubernetesAPI(
    "wait-k8s",
    host="192.168.1.100",
    port=6443,
    timeout=600,
)
```

## Testing

```bash
# Run patch generation tests
uv run pytest tests/

# Test with specific config
uv run pytest tests/test_config_patches.py -v
```

Tests use fixtures from `conftest.py` that provide `PatchConfig` instances.

## Outputs

After successful deployment:

| Output | Description |
|--------|-------------|
| `cluster_name` | Talos cluster name |
| `control_plane_ip` | Node IP address |
| `kubeconfig_raw` | Kubeconfig (secret) |
| `talosconfig_raw` | Talosconfig (secret) |
| `kubernetes_endpoint` | API server URL |
| `written_files` | Paths to generated files |

## Files Written

Credentials are written to `outputs/` (gitignored):

| File | Mode | Purpose |
|------|------|---------|
| `talosconfig` | 0600 | `talosctl` configuration |
| `kubeconfig` | 0600 | `kubectl` configuration |
| `controlplane.yaml` | 0644 | Generated machine config |
| `machine-secrets.yaml` | 0600 | Cluster bootstrap secrets |

## Component Versions

| Component | Version | Purpose |
|-----------|---------|---------|
| Cilium | 1.17.6 | CNI with L2 announcements |
| Longhorn | 1.9.1 | Distributed block storage |
| Gateway API | v1.3.0 | Gateway API CRDs |
| external-snapshotter | v8.3.0 | CSI snapshot controller |

## Conventions

### Naming
- Pulumi resources: kebab-case (`wait-talos-node-ready`)
- Python variables: snake_case (`control_plane_node`)
- Config keys: snake_case (`control_plane_node`)

### Dependencies
- Always use `opts=pulumi.ResourceOptions(depends_on=[...])` for ordering
- Phase 2 resources depend on kubeconfig or wait resources

### Secrets
- Credentials written with mode 0600
- Outputs marked as `pulumi.Output.secret()`
- `outputs/` directory is gitignored
