# Component Platform Profile Mapping

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

## GCP Cloud Components (Active)

These components were previously listed as stubs. As of the platform abstraction alignment work (Tasks 1-7), they are fully implemented and verified.

| Component | Status | Notes |
|---|---|---|
| `issuer-gcp-cas` | ✅ ACTIVE | `GoogleCASClusterIssuer` implemented; uses Workload Identity auth via `openchoreo-cas` GSA |
| `registry-cloud` | ✅ ACTIVE | Verified complete with 6 files; ExternalSecrets pull AR push key from GCP SM. **Note**: AR-push authentication migrated from SA key ExternalSecrets to Workload Identity (2026-04-18). SA key ExternalSecrets removed from this component. |
| `observability-cloud` | ✅ ACTIVE | Verified and fixed; 17 files including 6 Odigos resources added in Task 5 |
| `secrets-gcp-sm` | ✅ ACTIVE | `ClusterSecretStore` migrated to Workload Identity auth; secretRef fallback documented |
| `secrets-openbao` | ✅ ACTIVE | Verified via standalone render; ClusterSecretStore (vault/openbao) now wired for baremetal |
| `issuer-letsencrypt` | 🔲 STUB | Placeholder only; no active configuration |

### Verification Evidence

Task 7 deep render of `clusters/gke/` confirmed:

- 1 `ClusterSecretStore` (gcpsm provider, Workload Identity auth)
- 5 `ExternalSecret` resources
- 3 `Certificate` resources
- 1 `GoogleCASClusterIssuer`
- Zero cross-platform leakage (no cilium-l2, keepalived, openbao, or letsencrypt-staging references)

## Target State vs Exception State

### Target State: Workload Identity for All GCP Service Accounts

The intended auth model for all GCP service accounts is **Workload Identity (WI)**. Under WI, a Kubernetes Service Account (KSA) is annotated to impersonate a GCP Service Account (GSA) without any static key files. The GCP metadata server handles token exchange transparently.

The four GSAs and their target KSA bindings:

| GSA | Target KSA | Namespace |
|---|---|---|
| `openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com` | `external-secrets` | `external-secrets` |
| `openchoreo-cas@pg-ae-n-app-173978.iam.gserviceaccount.com` | `google-cas-issuer` | `cert-manager` |
| `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com` | ExternalDNS + cert-manager SA | `kube-system` / `cert-manager` |
| `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com` | Argo Workflow execution SA | `workflows-default` |

All four GSAs now use Workload Identity. DNS and AR-push migrated on 2026-04-18 — SA key ExternalSecrets removed from ExternalDNS and registry-cloud components.

### Exception State: secretRef Auth via SA Keys + GCP Secret Manager (RETIRED 2026-04-18)

PwC's GCP org policy (`constraints/iam.disableServiceAccountKeyCreation`) prevents self-service SA key creation. The `iam.workloadIdentityUser` binding for DNS and AR-push GSAs was requested through the Global Cloud Requests portal and confirmed active on 2026-04-18. DNS and AR-push now use Workload Identity.

Until those portal requests were approved, DNS and AR-push used SA key files:

1. Portal creates the SA key
2. Developer uploads the key JSON to GCP Secret Manager (`openchoreo-dns-key`, `openchoreo-ar-push-key`)
3. ESO `ExternalSecret` syncs the key from GCP SM into a Kubernetes `Secret`
4. The consuming workload (ExternalDNS, cert-manager DNS-01 solver, Argo Workflows) mounts the K8s secret

This path is documented in `docs/gcp-org-policy-guide.md` and the break-glass fallback file `secrets-gcp-sm/clustersecretstore-secretref-fallback.yaml`.

### Retirement Criteria — MET (items 1-5 complete)

The secretRef exception path is retired when:

1. ✅ WI bindings for `openchoreo-dns` and `openchoreo-ar-push` approved and active (2026-04-18)
2. ✅ ExternalDNS and cert-manager DNS-01 solver KSAs annotated with `iam.gke.io/gcp-service-account`
3. ✅ Argo Workflow execution SA annotated with `iam.gke.io/gcp-service-account`
4. ✅ `ClusterSecretStore` auth switched from `secretRef` to `workloadIdentity` for DNS and AR-push
5. ✅ SA key-based `ExternalSecret` resources for DNS and AR-push removed
6. ⏳ 30 days pass with no fallback usage observed in ESO sync logs (window closes 2026-05-18)

See `docs/gcp-org-policy-guide.md#wi-migration-path` for the step-by-step migration procedure.

## Platform Capability Matrix (Formal Contract)

| Capability Family | PlatformProfile Field | Baremetal Pulumi Value | Baremetal GitOps Component | GCP Pulumi Value | GCP GitOps Component | Alignment Status |
|---|---|---|---|---|---|---|
| `secrets_backend` | `secrets_backend` | `openbao` | `secrets-openbao` | `gcp-sm` | `secrets-gcp-sm` | ✅ ALIGNED |
| `registry_mode` | `registry_mode` | `local` | `registry-self-hosted` | `cloud` | `registry-cloud` | ✅ GCP ALIGNED |
| `tls_issuer_mode` | `tls_issuer_mode` | `self-signed` | `issuer-selfsigned` | `gcp-cas` | `issuer-gcp-cas` | ✅ GCP ALIGNED |
| `observability_mode` | `observability_mode` | `self-hosted` | `observability-self-hosted` | `cloud` | `observability-cloud` | ✅ GCP ALIGNED |
| `load_balancer_mode` | `load_balancer_mode` | `cilium-l2` | `cilium-l2` | `cloud` | `—` | ✅ BY DESIGN |
| `cni_mode` | `cni_mode` | `cilium` | `network-cilium-policy` | `cloud` | `network-k8s-policy` | ✅ ALIGNED |

> **Note on `load_balancer_mode`**: GCP native Load Balancer requires no GitOps component — provisioned automatically by GKE when Service type LoadBalancer or Gateway resource is created.

### Platform-Specific Waves
- **GKE Wave 06 (Namespaces)**: Deploys OpenChoreo app resources (projects, components, releases) as sample workloads. Includes: `oc-namespaces`, `oc-platform-shared`, `oc-platform`, `oc-demo-projects`. Baremetal does not include this wave — sample apps are deployed manually or via separate workflow. This is intentional, not a gap.

## Remaining Gaps

- GCP `load_balancer_mode=cloud` has no dedicated GitOps component in the current platform kustomization.
- Base wildcard certs (`base/02-tls/wildcard-certs/*.yaml`) still hardcode `issuerRef.name: openchoreo-ca` and `kind: ClusterIssuer`. GCP CAS requires `name: ${CLUSTER_ISSUER_NAME}`, `kind: GoogleCASClusterIssuer`, `group: cas-issuer.jetstack.io`. This needs a Kustomize Component patch or Flux substitution parameterization.
