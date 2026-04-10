# Component ↔ Platform Profile Mapping

This document maps Pulumi `PlatformProfile` fields (defined in `pulumi/platforms/types.py`) to Kustomize Components (under `gitops/components/`). It serves as a **Rosetta Stone** between the Phase 1 Pulumi provisioner and the Phase 2 FluxCD GitOps reconciler — clarifying which platform flags drive which GitOps components, and where gaps remain.

## Mapping Table

| PlatformProfile Field | Type | Kustomize Component | Baremetal | k3d | GCP | AWS | Azure |
|---|---|---|---|---|---|---|---|
| `cilium_l2_announcements_enabled` | `bool` | `cilium-l2` | ✅ | ❌ | — | — | — |
| TLS_ENABLED (env var) | `bool` | `issuer-selfsigned` | ✅ | ✅ | — | — | — |
| `local_registry` | `bool` | `registry-self-hosted` | ✅ | ✅ | — | — | — |
| ENABLE_OBSERVABILITY (env var) | `bool` | `observability-self-hosted` | ✅ | ✅ (dead) | — | — | — |
| `cni_mode` | `CniMode` (= cilium) | `network-cilium-policy` | ✅ | ✅ | — | — | — |
| *(always-on)* | — | `kubernetes-replicator` | ✅ | ✅ | — | — | — |

**Legend:** ✅ = active, ❌ = not used, — = planned / not yet implemented

## PlatformProfile Fields (Complete Reference)

### Identity

| Field | Type |
|---|---|
| `name` | `str` |

### Networking

| Field | Type |
|---|---|
| `gateway_mode` | `GatewayMode` |
| `cni_mode` | `CniMode` |
| `enable_kube_proxy_replacement` | `bool` |
| `k8s_service_host` | `str` |
| `k8s_service_port` | `int` |

### Node Fixes

| Field | Type |
|---|---|
| `requires_coredns_rewrite` | `bool` |
| `requires_machine_id_fix` | `bool` |
| `requires_bpf_mount_fix` | `bool` |

### Cilium

| Field | Type |
|---|---|
| `cilium_auto_mount_bpf` | `bool` |
| `cilium_host_network_gateway` | `bool` |
| `cilium_cni_bin_path` | `str` |
| `cilium_bpf_host_legacy_routing` | `bool` |
| `cilium_l2_announcements_enabled` | `bool` |
| `cilium_l2_ip_pool_cidrs` | `Optional[list]` |
| `cilium_l2_interfaces` | `Optional[list]` |

### Workflow

| Field | Type |
|---|---|
| `workflow_template_mode` | `WorkflowTemplateMode` |
| `local_registry` | `bool` |

### Bootstrap

| Field | Type |
|---|---|
| `bootstrap_script` | `str` |
| `cluster_name_config_key` | `str` |
| `workflow_template_urls` | `Optional[dict]` |

### Phase 1 Pre-install Flags

| Field | Type |
|---|---|
| `cilium_pre_installed` | `bool` |
| `gateway_api_crds_pre_installed` | `bool` |

## Pulumi-Only Flags (No GitOps Component Yet)

These fields exist in `PlatformProfile` and are consumed by Pulumi during cluster provisioning, but have **no corresponding Kustomize component**. They configure low-level node/networking behavior that happens before GitOps takes over.

- `requires_coredns_rewrite` — CoreDNS rewrite rule for split-horizon DNS
- `requires_machine_id_fix` — DaemonSet to regenerate `/etc/machine-id` on cloned VMs
- `requires_bpf_mount_fix` — DaemonSet to mount BPF filesystem
- `cilium_auto_mount_bpf` — Cilium Helm value for BPF auto-mount
- `cilium_host_network_gateway` — Cilium host-network gateway mode
- `cilium_cni_bin_path` — Override path to CNI binaries
- `cilium_bpf_host_legacy_routing` — Legacy host routing via BPF
- `enable_kube_proxy_replacement` — Replace kube-proxy with Cilium
- `k8s_service_host` / `k8s_service_port` — API server endpoint for kube-proxy replacement
- `bootstrap_script` — Path to platform-specific bootstrap script
- `cluster_name_config_key` — Config key for cluster name resolution
- `workflow_template_urls` — URLs for Argo workflow templates
- `cilium_pre_installed` — Skip Cilium install (e.g., k3d bundles it)
- `gateway_api_crds_pre_installed` — Skip Gateway API CRD install

## Stub Components (Exist but Empty)

These Kustomize components exist in `gitops/components/` as placeholders for future cloud-provider integrations. They contain no active configuration.

| Component | Purpose |
|---|---|
| `issuer-gcp-cas` | Google Certificate Authority Service issuer |
| `issuer-letsencrypt` | Let's Encrypt ACME issuer |
| `registry-cloud` | Cloud-managed container registry |
| `observability-cloud` | Cloud-managed observability stack |
| `secrets-gcp-sm` | Google Secret Manager integration |
| `secrets-openbao` | OpenBao (Vault fork) secrets backend |
