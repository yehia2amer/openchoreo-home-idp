# Terraform vs Pulumi: Side-by-Side Comparison & Alignment Plan

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Resource Inventory Comparison](#2-resource-inventory-comparison)
3. [Configuration / Variables Comparison](#3-configuration--variables-comparison)
4. [Machine Config Patches Comparison](#4-machine-config-patches-comparison)
5. [Provisioning Flow Comparison](#5-provisioning-flow-comparison)
6. [Outputs Comparison](#6-outputs-comparison)
7. [Phase 2: Post-Install (Terraform) vs Missing (Pulumi)](#7-phase-2-post-install)
8. [Gap Analysis Summary](#8-gap-analysis-summary)
9. [Step-by-Step Alignment Plan](#9-step-by-step-alignment-plan)

---

## 1. Architecture Overview

| Aspect | Terraform (Source of Truth) | Pulumi (Current) |
|--------|----------------------------|-------------------|
| **Tool** | OpenTofu (Terraform-compatible) | Pulumi (Python) |
| **Phases** | Two-phase: `apply-bootstrap/` + `post-install/` | Single-phase (Phase 1 only) |
| **Phase linkage** | File-based handoff (`outputs/kubeconfig`) | N/A (Phase 2 missing) |
| **Talos provider** | `siderolabs/talos ~>0.4` (locked at 0.8.1) | `pulumiverse-talos >=0.7.1` |
| **K8s provider** | `hashicorp/kubernetes ~>2.25` | **MISSING** |
| **Helm provider** | `hashicorp/helm ~>2.12` | **MISSING** |
| **HTTP provider** | `hashicorp/http ~>3.5` | Not needed (Python `urllib`/`requests`) |
| **Language** | HCL | Python 3.12 |
| **Config format** | `terraform.tfvars` | `Pulumi.dev.yaml` |

### Terraform Two-Phase Flow
```
Phase 1 (apply-bootstrap/):
  secrets -> config -> apply -> bootstrap -> kubeconfig
  Writes: outputs/{talosconfig, controlplane.yaml, kubeconfig, machine-secrets.yaml}

Phase 2 (post-install/):
  Reads: outputs/kubeconfig
  Installs: Gateway API CRDs (6) -> Cilium Helm chart -> cilium-secrets namespace labels
```

### Pulumi Current Flow
```
Phase 1 only:
  secrets -> config -> apply -> bootstrap -> kubeconfig
  Writes: ~/.kube/config-{name}-talos-baremetal, ~/.talos/config-{name}-baremetal
  Phase 2: COMPLETELY MISSING
```

### Pulumi Target Flow (After Alignment)
```
Single phase (consolidated):
  secrets -> config -> apply -> bootstrap -> kubeconfig
  -> Gateway API CRDs -> Cilium Helm -> namespace labels
  Writes: outputs/{talosconfig, controlplane.yaml, kubeconfig, machine-secrets.yaml}
```

---

## 2. Resource Inventory Comparison

### Phase 1 Resources

| Resource | Terraform | Pulumi | Status |
|----------|-----------|--------|--------|
| `talos_machine_secrets` | `talos_machine_secrets.this` | `talos.machine.Secrets("machine-secrets")` | **MATCH** |
| `talos_machine_configuration` (data) | `data.talos_machine_configuration.this` | `talos.machine.get_configuration_output(...)` | **MATCH** |
| `talos_client_configuration` (data) | `data.talos_client_configuration.this` | **MISSING** — hand-built in Python | **GAP** |
| `talos_machine_configuration_apply` | `talos_machine_configuration_apply.this` | `talos.machine.ConfigurationApply(...)` | **MATCH** |
| `talos_machine_bootstrap` | `talos_machine_bootstrap.this` | `talos.machine.Bootstrap(...)` | **MATCH** |
| `talos_cluster_kubeconfig` | `talos_cluster_kubeconfig.this` | `talos.cluster.Kubeconfig(...)` | **MATCH** |
| `local_file` (talosconfig) | `local_file.talosconfig` | `.apply()` side-effect | **STRUCTURAL DIFF** |
| `local_file` (controlplane.yaml) | `local_file.controlplane` | **MISSING** | **GAP** |
| `local_file` (kubeconfig) | `local_file.kubeconfig` | `.apply()` side-effect | **STRUCTURAL DIFF** |
| `local_file` (machine-secrets.yaml) | `local_file.machine_secrets` | **MISSING** | **GAP** |

### Phase 2 Resources (ALL MISSING from Pulumi)

| Resource | Terraform | Pulumi | Status |
|----------|-----------|--------|--------|
| `data.http.gateway_api_crds` (x6) | Fetches 6 CRD YAMLs from GitHub | **MISSING** | **GAP** |
| `kubernetes_manifest.gateway_api_crds` (x6) | Deploys 6 Gateway API CRDs | **MISSING** | **GAP** |
| `helm_release.cilium` | Cilium Helm chart | **MISSING** | **GAP** |
| `kubernetes_labels.cilium_secrets_namespace` | Labels cilium-secrets namespace | **MISSING** | **GAP** |

---

## 3. Configuration / Variables Comparison

### Variables Present in Both

| Variable | Terraform | Pulumi Config Key | Match? |
|----------|-----------|-------------------|--------|
| `cluster_name` | `var.cluster_name` ("example-cluster") | `cluster_name` ("openchoreo") | Yes (different defaults OK) |
| `cluster_endpoint` | `var.cluster_endpoint` ("https://cluster.local:6443") | Computed: `f"https://{kubernetes_api_host}:{kubernetes_api_port}"` | **STRUCTURAL DIFF** — TF is single string, Pulumi computes from host+port |
| `control_plane_nodes` | `var.control_plane_nodes` (list) | `control_plane_node` (single string) | **GAP** — TF uses list, Pulumi single node |
| `talos_version` | `var.talos_version` | `talos_version` | Yes |
| `schematic_id` | `var.schematic_id` | `schematic_id` | Yes |
| `network_interface` | `var.network_interface` | `network_interface` | Yes |
| `network_addresses` | `var.network_addresses` (list(string)) | `network_address` (single string) | **GAP** — TF list vs Pulumi single |
| `network_gateway` | `var.network_gateway` | `network_gateway` | Yes |
| `cert_sans` | `var.cert_sans` (list(string)) | `cert_sans` (JSON string parsed to list) | Yes (different encoding) |
| `install_disk_selector` | `var.install_disk_selector` | `install_disk_wwid` | Yes (renamed) |
| `longhorn_disk` | `var.longhorn_disk` | `longhorn_disk` | Yes |
| `enable_cloudflared` | `var.enable_cloudflared` | `enable_cloudflared` | Yes |
| `cloudflare_tunnel_token` | `var.cloudflare_tunnel_token` (sensitive) | `cloudflared_token` | Yes (but token committed in Pulumi.dev.yaml) |
| `enable_nvidia_gpu` | `var.enable_nvidia_gpu` | `enable_nvidia` | Yes (renamed) |

### Variables in Terraform but MISSING from Pulumi

| Variable | Terraform | Purpose | Action |
|----------|-----------|---------|--------|
| `dns_servers` | `var.dns_servers` (list, default ["8.8.8.8","8.8.4.4"]) | Configurable DNS | **ADD** — Pulumi hardcodes ["1.1.1.1","8.8.8.8"] |
| `enable_zfs` | `var.enable_zfs` (bool, default false) | Conditional ZFS kernel module | **ADD** |
| `wipe_install_disk` | `var.wipe_install_disk` (bool, default false) | Configurable wipe behavior | **ADD** — Pulumi hardcodes `True` |
| `worker_nodes` | `var.worker_nodes` (list) | Worker node IPs | SKIP (unused in TF too) |
| `control_plane_ip` | `var.control_plane_ip` | Standalone CP IP | SKIP (unused in TF) |
| `kubernetes_version` | `var.kubernetes_version` | K8s version | Already in Pulumi |
| `enable_bootstrap` | `var.enable_bootstrap` | Bootstrap toggle | SKIP (unused in TF) |
| `cilium_version` | Phase 2: `var.cilium_version` (default "1.17.6") | Cilium version | **ADD** |
| `gateway_api_version` | Phase 2: `var.gateway_api_version` (default "v1.3.0") | Gateway API CRD version | **ADD** |

### Variables in Pulumi but NOT in Terraform

| Config Key | Pulumi | Purpose | Action |
|------------|--------|---------|--------|
| `kubernetes_api_host` | Computed from `control_plane_node` | API host | Keep (convenience) |
| `kubernetes_api_port` | Default 6443 | API port | Keep (convenience) |
| `control_plane_install_disk` | In Pulumi.dev.yaml | Unused by code | **REMOVE** |
| `control_plane_hostname` | Default computed | Unused downstream | **REMOVE** |
| `control_plane_endpoint` | In Pulumi.dev.yaml | Not read by code | **REMOVE** (orphaned key) |
| `talos_api_endpoint` | Defaults to control_plane_node | Talos API endpoint | Keep (useful) |

---

## 4. Machine Config Patches Comparison

### Patch Organization

| Terraform Patch | Pulumi Equivalent | Match? |
|----------------|-------------------|--------|
| `install_image_patch` | `render_factory_image_patch()` | **PARTIAL** — content differs |
| `network_patch` | `render_install_patch()` + `render_network_patch()` | **SPLIT** — TF is one patch, Pulumi is two |
| `storage_patch` | `render_storage_patch()` | **PARTIAL** — close but differs |
| `kernel_drivers_patch` | `render_kernel_patch()` | **PARTIAL** — missing items |
| `cluster_settings_patch` | `render_cluster_settings_patch()` | **PARTIAL** — missing fields |
| `logging_patch` | **MISSING** | **GAP** |
| `cloudflared_patch` | `render_cloudflared_patch()` | **MATCH** |
| `nvidia_pci_patch` | `render_nvidia_patch()` | **MATCH** |

### Patch Aggregation

| Aspect | Terraform | Pulumi |
|--------|-----------|--------|
| Common patches | `[install_image, cluster_settings, kernel_drivers, logging]` | N/A — flat list |
| Control plane patches | `common + [network, storage, cloudflared?, nvidia?]` | `[install, factory_image, network, storage, kernel, cluster_settings, cloudflared?, nvidia?]` |
| Worker patches | `common + [storage, nvidia?]` | N/A (no worker support) |
| Empty filtering | `compact()` strips empty strings | List comprehension `if p` |

### Detailed Patch-by-Patch Comparison

#### A. Install Image / Factory Image Patch

**Terraform (`install_image_patch`):**
```yaml
machine:
  install:
    image: "factory.talos.dev/metal-installer/${schematic_id}:${talos_version}"
    wipe: var.wipe_install_disk  # Configurable
```

**Pulumi (`render_factory_image_patch`):**
```yaml
machine:
  install:
    image: "factory.talos.dev/metal-installer/{schematic_id}:{talos_version}"
    wipe: True  # HARDCODED
```

**Differences:**
- `wipe` is configurable in TF (`var.wipe_install_disk`), hardcoded `True` in Pulumi
- Pulumi returns empty string if `schematic_id` is empty; TF always includes

#### B. Network Patch

**Terraform (`network_patch`):**
```yaml
machine:
  features:
    hostDNS:
      enabled: true
      forwardKubeDNSToHost: false
  certSANs: var.cert_sans                    # <-- HERE
  network:
    interfaces:
      - interface: var.network_interface
        addresses: var.network_addresses       # <-- LIST
        routes:
          - network: "0.0.0.0/0"
            gateway: var.network_gateway
            metric: 1024                       # <-- MISSING from Pulumi
        mtu: 1500                              # <-- MISSING from Pulumi
cluster:
  network:
    cni:
      name: "none"                             # <-- In TF network_patch, in Pulumi install_patch
  proxy:
    disabled: true                             # <-- In TF network_patch, in Pulumi install_patch
  apiServer:
    certSANs: var.cert_sans                    # <-- In TF network_patch, in Pulumi install_patch
```

**Pulumi (`render_network_patch`):**
```yaml
machine:
  network:
    nameservers: ["1.1.1.1", "8.8.8.8"]       # <-- HARDCODED, TF uses var.dns_servers
    interfaces:
      - interface: network_interface
        addresses: [network_address]            # <-- SINGLE STRING in list
        routes:
          - network: "0.0.0.0/0"
            gateway: network_gateway
            # MISSING: metric: 1024
        # MISSING: mtu: 1500
  features:
    hostDNS:
      enabled: true
      forwardKubeDNSToHost: false
  # MISSING: certSANs (it's in install_patch instead)
# MISSING: cluster.network.cni (it's in install_patch instead)
# MISSING: cluster.proxy (it's in install_patch instead)
# MISSING: cluster.apiServer.certSANs (it's in install_patch instead)
```

**Differences:**
1. `machine.certSANs` — in TF network_patch, in Pulumi install_patch
2. `cluster.network.cni`, `cluster.proxy`, `cluster.apiServer.certSANs` — in TF network_patch, in Pulumi install_patch
3. `nameservers` — hardcoded in Pulumi, missing from TF (TF uses `dns_servers` var but doesn't include it in patch!)
4. `network_addresses` — TF uses list variable directly, Pulumi wraps single string in list
5. Route `metric: 1024` — present in TF, **MISSING** from Pulumi
6. Interface `mtu: 1500` — present in TF, **MISSING** from Pulumi

> **NOTE**: The nameservers field IS in Pulumi's network patch but NOT in Terraform's network_patch. However, TF has a `dns_servers` variable that is never used in any patch — it's an unused variable. So nameservers is actually a Pulumi ADDITION. For alignment, we should make it configurable but keep it.

#### C. Storage Patch

**Terraform (`storage_patch`):**
```yaml
machine:
  kubelet:
    extraMounts:
      - destination: "/var/lib/longhorn"
        type: "bind"
        source: "/var/lib/longhorn"
        options: ["bind", "rshared", "rw"]
  install:
    diskSelector:
      wwid: var.install_disk_selector
  disks:
    - device: var.longhorn_disk
      partitions:
        - mountpoint: "/var/lib/longhorn"
```

**Pulumi (`render_storage_patch`):**
```yaml
machine:
  kubelet:
    extraMounts:
      - destination: "/var/lib/longhorn"
        type: "bind"
        source: "/var/lib/longhorn"
        options: ["bind", "rshared", "rw"]
  install:                                      # <-- Only if install_disk_wwid is set
    diskSelector:
      wwid: install_disk_wwid
  disks:
    - device: longhorn_disk
      partitions:
        - mountpoint: "/var/lib/longhorn"
```

**Differences:**
- TF always includes `install.diskSelector`; Pulumi conditionally includes it (minor, acceptable)
- TF always renders the patch; Pulumi returns empty if `longhorn_disk` is empty (minor, acceptable)
- Otherwise: **MATCH**

#### D. Kernel / Drivers Patch

**Terraform (`kernel_drivers_patch`):**
```yaml
machine:
  files:
    - content: |
        [plugins]
          [plugins."io.containerd.grpc.v1.cri"]
            device_ownership_from_security_context = true
          [plugins."io.containerd.cri.v1.runtime"]
            device_ownership_from_security_context = true
      path: "/etc/cri/conf.d/20-customization.part"
      op: "create"
  registries: {}                                # <-- MISSING from Pulumi
  kernel:
    modules:
      - name: vfio_pci
      - name: vfio_iommu_type1
      - name: cx23885                           # <-- MISSING from Pulumi
      # Conditional ZFS:
      - name: zfs  (if enable_zfs)              # <-- MISSING from Pulumi
```

**Pulumi (`render_kernel_patch`):**
```yaml
machine:
  kernel:
    modules:
      - name: vfio_pci
      - name: vfio_iommu_type1
      # MISSING: cx23885
      # MISSING: conditional zfs
  files:
    - content: <same containerd config>
      path: "/etc/cri/conf.d/20-customization.part"
      op: "create"
  # MISSING: registries: {}
```

**Differences:**
1. `registries: {}` — present in TF, **MISSING** from Pulumi
2. `cx23885` kernel module — present in TF, **MISSING** from Pulumi
3. Conditional `zfs` kernel module — present in TF (via `enable_zfs`), **MISSING** from Pulumi
4. `files` content leading whitespace differs slightly (TF uses heredoc indentation)

#### E. Cluster Settings Patch

**Terraform (`cluster_settings_patch`):**
```yaml
machine:
  kubelet:
    extraArgs:
      max-pods: "250"
cluster:
  allowSchedulingOnControlPlanes: true
  controlPlane:
    endpoint: var.cluster_endpoint              # <-- MISSING from Pulumi
  clusterName: var.cluster_name                 # <-- MISSING from Pulumi
```

**Pulumi (`render_cluster_settings_patch`):**
```yaml
machine:
  kubelet:
    extraArgs:
      max-pods: "250"
cluster:
  allowSchedulingOnControlPlanes: true
  # MISSING: controlPlane.endpoint
  # MISSING: clusterName
```

**Differences:**
1. `cluster.controlPlane.endpoint` — present in TF, **MISSING** from Pulumi
2. `cluster.clusterName` — present in TF, **MISSING** from Pulumi

> **NOTE**: These are also set via `get_configuration_output()` params, so they may be redundant in the patch. However, for exact alignment with TF, they should be present.

#### F. Logging Patch

**Terraform (`logging_patch`):**
```yaml
machine:
  logging:
    destinations:
      - endpoint: "tcp://127.0.0.1:6001/"
        format: "json_lines"
        extraTags:
          cluster: "talos-amer-cluster"
```

**Pulumi:** **COMPLETELY MISSING**

#### G. Cloudflared Patch — MATCH

Both produce identical YAML when enabled.

#### H. NVIDIA PCI Patch — MATCH

Both produce identical YAML when enabled.

#### I. Pulumi's `render_install_patch()` — NO TERRAFORM EQUIVALENT

```yaml
cluster:
  apiServer:
    certSANs: [sorted set of control_plane_node, localhost, cert_sans_extra]
  network:
    cni:
      name: "none"
  proxy:
    disabled: true
  allowSchedulingOnControlPlanes: true
machine:
  certSANs: [same sorted set]
```

This combines content that in Terraform is distributed across:
- `network_patch` (certSANs, cni=none, proxy=disabled, apiServer.certSANs)
- `cluster_settings_patch` (allowSchedulingOnControlPlanes)

---

## 5. Provisioning Flow Comparison

| Step | Terraform | Pulumi | Match? |
|------|-----------|--------|--------|
| 1. Generate secrets | `talos_machine_secrets.this` | `talos.machine.Secrets(...)` | **MATCH** |
| 2. Generate machine config | `data.talos_machine_configuration.this` | `talos.machine.get_configuration_output(...)` | **MATCH** |
| 3. Generate client config | `data.talos_client_configuration.this` | Hand-built in Python | **GAP** — should use provider |
| 4. Apply config | `talos_machine_configuration_apply.this` | `talos.machine.ConfigurationApply(...)` | **MATCH** |
| 5. Bootstrap | `talos_machine_bootstrap.this` | `talos.machine.Bootstrap(...)` | **MATCH** |
| 6. Get kubeconfig | `talos_cluster_kubeconfig.this` | `talos.cluster.Kubeconfig(...)` | **MATCH** |
| 7. Write output files | 4x `local_file` resources | 2x `.apply()` side-effects | **PARTIAL** — missing 2 files, side-effects not tracked |
| 8. Install Gateway API CRDs | 6x `kubernetes_manifest` | **MISSING** | **GAP** |
| 9. Install Cilium | `helm_release.cilium` | **MISSING** | **GAP** |
| 10. Label namespace | `kubernetes_labels.cilium_secrets_namespace` | **MISSING** | **GAP** |

### Dependency Chain

**Terraform:**
```
secrets -> machine_config (data) \
        -> client_config (data)   -> config_apply -> bootstrap -> kubeconfig
                                                                     |
                                                              [Phase 2 reads kubeconfig file]
                                                                     |
                                                              gateway_api_crds -> cilium -> namespace_labels
```

**Pulumi (Current):**
```
secrets -> machine_config (data) -> config_apply -> bootstrap -> kubeconfig -> [ENDS]
```

**Pulumi (Target):**
```
secrets -> machine_config (data) -> config_apply -> bootstrap -> kubeconfig
                                                                     |
                                                              k8s_provider (from kubeconfig_raw)
                                                                     |
                                                              gateway_api_crds -> cilium -> namespace_labels
```

---

## 6. Outputs Comparison

### Exported Values

| Output | Terraform | Pulumi | Match? |
|--------|-----------|--------|--------|
| Written files map | `output.written_files` (sensitive) | N/A | **GAP** |
| cluster_name | Not exported | `pulumi.export("cluster_name")` | Pulumi-only (OK) |
| control_plane_ip | Not exported | `pulumi.export("control_plane_ip")` | Pulumi-only (OK) |
| kubeconfig_raw | Via `local_file` | `pulumi.export("kubeconfig_raw")` — **NOT SECRET** | **GAP** — should be secret |
| kubeconfig_path | Via `written_files` | `pulumi.export("kubeconfig_path")` | Structural diff |
| kubeconfig_context | Not exported | `pulumi.export("kubeconfig_context")` | Pulumi-only (OK) |
| talosconfig_raw | Via `local_file` | `pulumi.export("talosconfig_raw")` — secret | Match |
| talosconfig_path | Via `written_files` | `pulumi.export("talosconfig_path")` | Structural diff |
| talos_version | Not exported | `pulumi.export("talos_version")` | Pulumi-only (OK) |

### Written Files

| File | Terraform | Pulumi | Match? |
|------|-----------|--------|--------|
| `outputs/talosconfig` | `local_file.talosconfig` (mode 0600) | `~/.talos/config-{name}-baremetal` | **DIFF** — different path |
| `outputs/controlplane.yaml` | `local_file.controlplane` (mode 0644) | **MISSING** | **GAP** |
| `outputs/kubeconfig` | `local_file.kubeconfig` (mode 0600) | `~/.kube/config-{name}-talos-baremetal` | **DIFF** — different path |
| `outputs/machine-secrets.yaml` | `local_file.machine_secrets` (mode 0600) | **MISSING** | **GAP** |

---

## 7. Phase 2: Post-Install

### Terraform Phase 2 Components

#### A. Gateway API CRDs (6 total)

| CRD | URL Pattern |
|-----|-------------|
| gatewayclasses | `.../standard/gateway.networking.k8s.io_gatewayclasses.yaml` |
| gateways | `.../standard/gateway.networking.k8s.io_gateways.yaml` |
| httproutes | `.../standard/gateway.networking.k8s.io_httproutes.yaml` |
| referencegrants | `.../standard/gateway.networking.k8s.io_referencegrants.yaml` |
| grpcroutes | `.../standard/gateway.networking.k8s.io_grpcroutes.yaml` |
| tlsroutes | `.../experimental/gateway.networking.k8s.io_tlsroutes.yaml` |

Base URL: `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/${version}/config/crd/`

TF fetches these via `data.http` and deploys via `kubernetes_manifest` (strips `status` key).

#### B. Cilium Helm Chart

```yaml
name: cilium
repository: https://helm.cilium.io/
chart: cilium
version: var.cilium_version  # default "1.17.6"
namespace: kube-system
values:
  ipam:
    mode: kubernetes
  kubeProxyReplacement: true
  bpf:
    hostLegacyRouting: true
  securityContext:
    capabilities:
      ciliumAgent: [CHOWN, KILL, NET_ADMIN, NET_RAW, IPC_LOCK, SYS_ADMIN, SYS_RESOURCE, DAC_OVERRIDE, FOWNER, SETGID, SETUID]
      cleanCiliumState: [NET_ADMIN, SYS_ADMIN, SYS_RESOURCE]
  cgroup:
    autoMount:
      enabled: false
    hostRoot: /sys/fs/cgroup
  k8sServiceHost: localhost
  k8sServicePort: "7445"
  l2announcements:
    enabled: true
  gatewayAPI:
    enabled: true
    enableAlpn: true
    enableAppProtocol: true
  operator:
    replicas: 1
  hubble:
    enabled: true
    relay:
      enabled: true
    ui:
      enabled: true
```

#### C. Namespace Label

```
Resource: cilium-secrets (Namespace)
Labels:
  pod-security.kubernetes.io/enforce: privileged
Depends on: helm_release.cilium
```

### Pulumi Implementation Plan for Phase 2

In Pulumi, this consolidates into the same program:
1. Create a `pulumi_kubernetes.Provider` using `kubeconfig.kubeconfig_raw`
2. Fetch CRD YAMLs via Python `urllib` (no HTTP provider needed)
3. Deploy CRDs via `pulumi_kubernetes.yaml.ConfigFile` or raw manifests
4. Deploy Cilium via `pulumi_kubernetes.helm.v4.Chart`
5. Label namespace via `pulumi_kubernetes.core.v1.NamespacePatch`

---

## 8. Gap Analysis Summary

### Critical Gaps (Must Fix)

| # | Gap | Impact |
|---|-----|--------|
| 1 | **Phase 2 completely missing** (Gateway API CRDs, Cilium, namespace label) | Cluster has no CNI — pods won't schedule |
| 2 | **Logging patch missing** | No machine-level log forwarding |
| 3 | **`cx23885` kernel module missing** | TV tuner/video capture driver not loaded |
| 4 | **`registries: {}` missing** from kernel patch | Registry config not reset |
| 5 | **Route metric (1024) missing** from network patch | Route priority not set |
| 6 | **Interface MTU (1500) missing** from network patch | MTU not explicitly set |
| 7 | **`cluster.controlPlane.endpoint` missing** from cluster_settings | Endpoint not in patch |
| 8 | **`cluster.clusterName` missing** from cluster_settings | Cluster name not in patch |
| 9 | **`enable_zfs` variable and conditional ZFS module missing** | Can't enable ZFS |
| 10 | **`wipe_install_disk` hardcoded True** | Can't disable wipe |
| 11 | **DNS nameservers hardcoded** | Can't configure DNS servers |
| 12 | **`kubeconfig_raw` not marked as secret** | Sensitive data exposed in state |
| 13 | **controlplane.yaml output file missing** | Machine config not saved |
| 14 | **machine-secrets.yaml output file missing** | Secrets not saved |

### Structural Differences (Align for Consistency)

| # | Difference | Decision |
|---|-----------|----------|
| 15 | certSANs/CNI/proxy in Pulumi's `install_patch` vs TF's `network_patch` | **Restructure** — move to network_patch for alignment |
| 16 | `allowSchedulingOnControlPlanes` duplicated (install_patch + cluster_settings) | **Deduplicate** — keep only in cluster_settings |
| 17 | Pulumi has `render_install_patch()` with no TF equivalent | **Remove** — distribute content to correct patches |
| 18 | File output paths: `~/.kube/` vs `outputs/` | **Change** to `outputs/` for alignment, optionally keep home dir copies |
| 19 | Talosconfig hand-built vs provider `talos_client_configuration` | **Investigate** if Pulumi provider has equivalent; if not, keep Python build |
| 20 | `network_address` single string vs `network_addresses` list | **Change** to list for alignment |

### Low Priority (Nice to Have)

| # | Item | Decision |
|---|------|----------|
| 21 | Remove unused config: `control_plane_install_disk`, `control_plane_hostname` | Clean up |
| 22 | Remove orphaned Pulumi.dev.yaml key: `control_plane_endpoint` | Clean up |
| 23 | Module-level mutable state pattern (`patches.foo = bar`) | **Refactor** to function parameters |

---

## 9. Step-by-Step Alignment Plan

### Step 1: Add Dependencies

**File:** `pyproject.toml`
- Add `pulumi-kubernetes>=4.0.0,<5.0.0`
- Add `pulumi-helm>=4.0.0,<5.0.0` (or use pulumi_kubernetes Helm support)

### Step 2: Add Missing Config Variables

**File:** `__main__.py`
- Add `dns_servers` config (default `["8.8.8.8", "8.8.4.4"]`)
- Add `enable_zfs` config (default `False`)
- Add `wipe_install_disk` config (default `False`)
- Add `cilium_version` config (default `"1.17.6"`)
- Add `gateway_api_version` config (default `"v1.3.0"`)
- Change `network_address` to `network_addresses` (list)
- Remove unused: `control_plane_install_disk`, `control_plane_hostname`

**File:** `Pulumi.dev.yaml`
- Add new config keys for `dns_servers`, `enable_zfs`, `wipe_install_disk`, `cilium_version`, `gateway_api_version`
- Change `network_address` to `network_addresses` (as JSON list)
- Remove `control_plane_endpoint`, `control_plane_install_disk`

### Step 3: Restructure Patches

**File:** `patches.py`

#### 3a. Remove `render_install_patch()`
- Distribute its content to the correct patches (network and cluster_settings)

#### 3b. Update `render_factory_image_patch()` → rename to `render_install_image_patch()`
- Make `wipe` use the new `wipe_install_disk` config variable
- Always render (don't skip when schematic_id is empty — match TF behavior)

#### 3c. Update `render_network_patch()`
Add:
- `machine.certSANs` (from cert_sans)
- `cluster.network.cni.name = "none"`
- `cluster.proxy.disabled = True`
- `cluster.apiServer.certSANs` (from cert_sans)
- Route `metric: 1024`
- Interface `mtu: 1500`
- Make `nameservers` use configurable `dns_servers` variable
- Change `network_address` to use `network_addresses` list

#### 3d. Update `render_kernel_patch()` → rename to `render_kernel_drivers_patch()`
Add:
- `{ name: "cx23885" }` to kernel modules
- Conditional `{ name: "zfs" }` when `enable_zfs` is True
- `registries: {}` to machine config

#### 3e. Update `render_cluster_settings_patch()`
Add:
- `cluster.controlPlane.endpoint` (from kubernetes_endpoint)
- `cluster.clusterName` (from cluster_name)
Remove:
- `cluster.allowSchedulingOnControlPlanes` is already here — keep it

#### 3f. Add `render_logging_patch()`
New patch:
```python
def render_logging_patch() -> str:
    return json.dumps({
        "machine": {
            "logging": {
                "destinations": [{
                    "endpoint": "tcp://127.0.0.1:6001/",
                    "format": "json_lines",
                    "extraTags": {
                        "cluster": f"talos-{cluster_name}"
                    }
                }]
            }
        }
    })
```

#### 3g. Refactor module-level mutable state
Change from `patches.foo = bar` pattern to passing a config dataclass/dict to each render function.

### Step 4: Update Patch List in `__main__.py`

```python
config_patches = [
    p for p in [
        patches.render_install_image_patch(),
        patches.render_cluster_settings_patch(),
        patches.render_kernel_drivers_patch(),
        patches.render_logging_patch(),
        patches.render_network_patch(),
        patches.render_storage_patch(),
        patches.render_cloudflared_patch(),
        patches.render_nvidia_patch(),
    ] if p
]
```

This matches Terraform's aggregation order:
- common: `[install_image, cluster_settings, kernel_drivers, logging]`
- control_plane: common + `[network, storage, cloudflared?, nvidia?]`

### Step 5: Add Missing Output Files

**File:** `__main__.py`

Add writing of:
- `outputs/controlplane.yaml` — from `machine_config.machine_configuration`
- `outputs/machine-secrets.yaml` — from `machine_secrets.machine_secrets` (yamlencode)
- Change kubeconfig output to `outputs/kubeconfig` (keep home dir copy as convenience)
- Change talosconfig output to `outputs/talosconfig`

### Step 6: Mark kubeconfig_raw as Secret

```python
pulumi.export("kubeconfig_raw", pulumi.Output.secret(kubeconfig.kubeconfig_raw))
```

### Step 7: Implement Phase 2 — Gateway API CRDs

**File:** `__main__.py` (or new `post_install.py` module)

```python
import pulumi_kubernetes as k8s

# Create K8s provider from kubeconfig
k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=kubeconfig.kubeconfig_raw,
    opts=pulumi.ResourceOptions(depends_on=[kubeconfig]),
)

# Gateway API CRDs
GATEWAY_API_CRDS = {
    "gatewayclasses": "standard",
    "gateways": "standard",
    "httproutes": "standard",
    "referencegrants": "standard",
    "grpcroutes": "standard",
    "tlsroutes": "experimental",
}

gateway_crd_resources = []
for name, channel in GATEWAY_API_CRDS.items():
    url = f"https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/{gateway_api_version}/config/crd/{channel}/gateway.networking.k8s.io_{name}.yaml"
    crd = k8s.yaml.ConfigFile(
        f"gateway-api-{name}",
        file=url,
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[kubeconfig]),
    )
    gateway_crd_resources.append(crd)
```

### Step 8: Implement Phase 2 — Cilium Helm Chart

```python
cilium = k8s.helm.v4.Chart(
    "cilium",
    k8s.helm.v4.ChartArgs(
        chart="cilium",
        version=cilium_version,
        namespace="kube-system",
        repository_opts=k8s.helm.v4.RepositoryOptsArgs(
            repo="https://helm.cilium.io/",
        ),
        values={...cilium_values...},
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=gateway_crd_resources,
    ),
)
```

### Step 9: Implement Phase 2 — Namespace Label

```python
k8s.core.v1.NamespacePatch(
    "cilium-secrets-labels",
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
```

### Step 10: Update Pulumi.dev.yaml

Add new config keys:
```yaml
config:
  openchoreo-talos-cluster-baremetal:dns_servers: '["8.8.8.8", "8.8.4.4"]'
  openchoreo-talos-cluster-baremetal:enable_zfs: "true"
  openchoreo-talos-cluster-baremetal:wipe_install_disk: "true"
  openchoreo-talos-cluster-baremetal:cilium_version: "1.17.6"
  openchoreo-talos-cluster-baremetal:gateway_api_version: "v1.3.0"
  openchoreo-talos-cluster-baremetal:network_addresses: '["192.168.0.100/24"]'
```

Remove orphaned keys:
- `control_plane_endpoint`
- `control_plane_install_disk`

### Step 11: Update Tests

Update `tests/test_config_patches.py`:
- Test renamed patch functions
- Test new `render_logging_patch()`
- Test `enable_zfs` conditional in kernel patch
- Test `wipe_install_disk` in install image patch
- Test configurable DNS servers
- Test `cx23885` kernel module presence
- Test `registries: {}` presence
- Test route metric and MTU
- Test `controlPlane.endpoint` and `clusterName` in cluster_settings

### Step 12: Final Verification

- Run `pulumi preview` to verify no errors
- Run `ruff check` and `ruff format` for code quality
- Run `pytest` for test suite
- Compare generated patch YAML output between Terraform and Pulumi
- Confirm all 14 critical gaps from Section 8 are resolved

---

## Appendix: Cilium Helm Values (for copy-paste into Pulumi)

```python
CILIUM_VALUES = {
    "ipam": {"mode": "kubernetes"},
    "kubeProxyReplacement": True,
    "bpf": {"hostLegacyRouting": True},
    "securityContext": {
        "capabilities": {
            "ciliumAgent": [
                "CHOWN", "KILL", "NET_ADMIN", "NET_RAW", "IPC_LOCK",
                "SYS_ADMIN", "SYS_RESOURCE", "DAC_OVERRIDE", "FOWNER",
                "SETGID", "SETUID",
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
```
