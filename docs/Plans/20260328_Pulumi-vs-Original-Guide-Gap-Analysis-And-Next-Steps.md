# Pulumi vs Original OpenChoreo K3d Guide: Gap Analysis And Next Steps

Date: 2026-03-28

## Goal

Compare the original installation flow in `docs/Plans/OpenChoreo-v1.0-K3d-Installation-Guide.md` against the Pulumi implementation under `pulumi/`, identify what is already automated, what is partially covered, what is still manual or missing, and define the next remediation steps.

Also evaluate how the current Pulumi code handles environment-specific behavior across supported Kubernetes platforms, and define a modular configuration model that can scale beyond k3d and Rancher Desktop to Talos and future cloud targets.

## Executive Summary

The Pulumi implementation already covers most of the original guide end to end, including:

- Platform prerequisites
- OpenBao installation and base secret seeding
- ClusterSecretStore creation
- Thunder installation and bootstrap orchestration
- Control plane, data plane, workflow plane, and observability plane deployment
- Plane registration
- Flux installation and Flux object creation
- k3d-specific CoreDNS rewrite
- k3d-specific machine-id initialization for Fluent Bit
- GitHub PAT seeding into OpenBao when `github_pat` is configured

The biggest gaps are not broad missing components. They are narrower operational and validation gaps:

- Pulumi does not create the cluster as part of the stack itself; cluster bootstrapping is still outside the stack and handled by a helper script.
- Pulumi does not strongly enforce that a real `github_pat` is provided when workflow builds and GitOps flows depend on it.
- Pulumi creates OpenBao secrets and ExternalSecret resources, but it does not explicitly wait for or validate all critical secret sync outcomes before later steps proceed.
- Pulumi installs Flux resources, but it does not wait for Flux `Kustomization` resources to report Ready.
- The guide does not document several Pulumi-specific runtime fixes that were required to make the stack work reliably, especially around Cilium, workflow template patching, and internal service endpoints.

There is also a structural scaling issue in the current configuration model:

- The stack currently handles platform differences mostly through global booleans and ad hoc fields such as `is_k3d`, `enable_cilium`, `cilium_k8s_api_host`, and `k3d_cluster_name`.
- Platform-specific decisions are spread across multiple components instead of being represented as a single platform profile.
- The current project and config naming still imply a k3d-first world even though Rancher Desktop is already supported and Talos/cloud platforms are planned.

That works for two local platforms, but it will become hard to maintain once Talos, AWS, GCP, and Azure-specific behavior is added.

## Current Multi-Platform Handling

The current Pulumi model supports multiple environments, but it does so implicitly rather than through a first-class platform abstraction.

### What exists today

Current environment handling is spread across:

- `pulumi/config.py`
- `pulumi/__main__.py`
- `pulumi/components/prerequisites.py`
- `pulumi/components/cilium.py`
- `pulumi/components/data_plane.py`
- `pulumi/components/workflow_plane.py`
- `pulumi/components/observability_plane.py`
- `pulumi/scripts/bootstrap_k3d.py`
- stack config files such as `pulumi/Pulumi.dev.yaml` and `pulumi/Pulumi.rancher-desktop.yaml`

### How the branching currently works

Current branching is mostly driven by a small set of global config fields:

- `kubeconfig_context`
- `is_k3d`
- `enable_cilium`
- `cilium_k8s_api_host`
- `k3d_cluster_name`
- generic feature flags such as `enable_flux` and `enable_observability`

Examples of current environment-specific handling:

- `pulumi/__main__.py` conditionally installs the Cilium component based on `enable_cilium`
- `pulumi/components/prerequisites.py` switches between deploying a real `kgateway` controller and creating a `GatewayClass` backed by Cilium
- `pulumi/components/prerequisites.py` applies CoreDNS rewrite only when `is_k3d = true`
- `pulumi/components/cilium.py` treats `is_k3d` as the switch for kube-proxy replacement, BPF mount behavior, and `hostNetwork` settings
- `pulumi/components/observability_plane.py` runs the machine-id fix only when `is_k3d = true`
- `pulumi/scripts/bootstrap_k3d.py` is a platform-specific bootstrap path that lives outside the Pulumi graph
- `pulumi/Pulumi.dev.yaml` and `pulumi/Pulumi.rancher-desktop.yaml` differentiate environments by manually setting different raw config values

### Strengths of the current model

- It is simple enough for the first two platforms
- It allowed fast iteration while debugging k3d and Rancher Desktop differences
- It keeps one shared deployment graph for all environments

### Weaknesses of the current model

- Platform identity is implicit rather than explicit
- `is_k3d` is already overloaded as a proxy for several unrelated behaviors
- Cilium choice and platform choice are partially entangled even though they are not the same concern
- Component code needs to know too much about individual platform quirks
- New platforms will likely add more booleans and one-off fields unless the model changes
- The project/config namespace `openchoreo-k3d` ~~is already misleading for non-k3d deployments~~ has been renamed to `openchoreo`

## Recommended Modular Direction

The next step should be to move from scattered booleans to an explicit platform-profile model.

### Recommendation summary

Introduce a first-class `platform` concept in config and resolve it into a typed `PlatformProfile` object before any component logic runs.

Instead of asking each component questions like:

- Is this k3d?
- Is Cilium enabled?
- Do I need CoreDNS rewrite?
- Do I need machine-id fix?
- Which gateway controller model applies here?

the component should receive a normalized answer from the platform layer.

### Proposed shape

Add a new config key:

- `platform = k3d | rancher-desktop | talos | aws | gcp | azure`

Then resolve it into a typed profile, for example:

```python
@dataclass
class PlatformProfile:
  name: str
  bootstrap_kind: str
  gateway_mode: str
  cni_mode: str
  requires_coredns_rewrite: bool
  requires_machine_id_fix: bool
  requires_cilium_bpf_fix: bool
  requires_k8s_service_host: bool
  workflow_template_mode: str
  local_registry_mode: str
  ingress_exposure_mode: str
  storage_class_mode: str
```

Possible layout:

- `pulumi/platforms/base.py`
- `pulumi/platforms/types.py`
- `pulumi/platforms/k3d.py`
- `pulumi/platforms/rancher_desktop.py`
- `pulumi/platforms/talos.py`
- `pulumi/platforms/aws.py`
- `pulumi/platforms/gcp.py`
- `pulumi/platforms/azure.py`

Then `pulumi/config.py` would:

1. load generic stack config
2. read `platform`
3. construct the matching `PlatformProfile`
4. expose both generic config and normalized platform capabilities to components

### Why this is better

- Platform identity becomes explicit
- Local-platform quirks are isolated in one place
- Components stop encoding platform-specific rules directly
- Talos support becomes a new profile rather than a new wave of booleans
- Future cloud platforms can override ingress, registry, DNS, storage, and gateway behavior without contaminating every component

## Recommended Separation Of Concerns

To keep the model maintainable, platform handling should be split into three layers.

### 1. Core product config

This stays global and platform-agnostic.

Examples:

- OpenChoreo version
- feature flags like observability and Flux
- repo URLs and Git branch
- credentials like `github_pat`

### 2. Platform profile

This defines infrastructure behavior and quirks.

Examples:

- cluster type
- ingress strategy
- gateway controller strategy
- whether CoreDNS rewrite is needed
- whether local VM or node fixes are needed
- whether local registry assumptions are valid

### 3. Bootstrap strategy

This should stay outside the Pulumi stack graph, but it should be modularized per platform.

Examples:

- `bootstrap_k3d.py`
- future `bootstrap_talos.py`
- potentially no bootstrap script for cloud providers if those clusters are assumed to exist already

That means the supported path becomes:

1. bootstrap or select cluster for the chosen platform
2. set `platform=<target>` in stack config
3. run the shared Pulumi deployment graph

## Concrete Guidance For Upcoming Platforms

### k3d

Keep this as the closest-to-upstream OpenChoreo profile.

Platform characteristics:

- uses OpenChoreo default assumptions most closely
- can keep `kgateway` as the default gateway controller path
- needs k3d-specific CoreDNS rewrite
- may need special workflow endpoint and bootstrap treatment

### Rancher Desktop

Treat this as a separate local-vm profile, not a partial variant of k3d.

Platform characteristics:

- Linux VM backed Kubernetes
- no k3d DNS rewrite flow
- different Cilium behavior
- may need explicit API server host for kube-proxy replacement
- different host networking and BPF expectations

### Talos

Treat Talos as its own platform profile from the start.

Likely characteristics:

- immutable OS assumptions
- potentially different bootstrap lifecycle
- likely no k3d-specific fixes
- may need different storage, CNI, or host-operation constraints

The key point is that Talos should not become another set of `if not is_k3d` branches.

### AWS, GCP, Azure

Treat these as cloud platform families that may later branch further.

Likely differences:

- load balancer behavior
- DNS and hostname exposure
- registry strategy
- storage class assumptions
- cloud-native ingress and gateway options
- secret backend evolution later if desired

The platform-profile model lets cloud differences be represented as capabilities instead of special cases in component code.

## Recommended Code Refactor Path

This should be done incrementally rather than as a full rewrite.

### Phase A: Introduce platform identity

Add:

- `platform` config key
- typed platform enum or string constants
- `PlatformProfile` object

Keep existing booleans temporarily, but derive them from the chosen platform where possible.

### Phase B: Move current k3d and Rancher Desktop behavior behind profiles

First migrations:

- CoreDNS rewrite decision
- Cilium kube-proxy replacement decision
- BPF and host-network tuning
- machine-id fix decision
- gateway controller mode

### Phase C: Remove overloaded booleans from component logic

Components should stop branching on raw `is_k3d` except during the migration period.

They should instead use profile fields such as:

- `cfg.platform.gateway_mode`
- `cfg.platform.requires_coredns_rewrite`
- `cfg.platform.requires_machine_id_fix`
- `cfg.platform.requires_cilium_bpf_fix`

### Phase D: Split bootstrap support by platform

Create a small bootstrap layer per platform instead of embedding all local-cluster assumptions into one script.

### Phase E: Rename project/config vocabulary  ✅ DONE

The project/config prefix has been renamed from `openchoreo-k3d` to `openchoreo` across Pulumi.yaml, pyproject.toml, all stack YAML files, and bootstrap scripts.

## Direct Answers

### Do we just need a token and push it to OpenBao?

Yes. In the original architecture, the source of truth for workflow Git credentials is OpenBao.

Specifically, the workflow-generated `ExternalSecret` resources read these keys from OpenBao:

- `secret/git-token`
- `secret/gitops-token`

Those provider-side secrets are then materialized into Kubernetes `Secret` objects inside workflow namespaces.

### How do we do that in Pulumi?

Pulumi already has this mechanism.

Current implementation:

- `pulumi/config.py` exposes `github_pat`
- `pulumi/components/prerequisites.py` conditionally writes it into OpenBao
- `pulumi/values/openbao.py` also seeds placeholder defaults during OpenBao bootstrap

Current Pulumi behavior:

- If `github_pat` is set, Pulumi writes:
  - `secret/git-token` with field `git-token`
  - `secret/gitops-token` with field `git-token`
- If `github_pat` is not set, OpenBao bootstrap still seeds fake development values

### Can we do that using External Secrets?

Not as a replacement for the OpenBao write in the current design.

External Secrets Operator is the consumer in this architecture, not the upstream source of truth. It reads from OpenBao and creates Kubernetes secrets. It does not solve the problem of initially getting the PAT into OpenBao unless the architecture is changed to use a different secret backend flow.

In this repo's current model:

1. Put PAT into OpenBao.
2. `ClusterSecretStore/default` points ESO at OpenBao.
3. Workflow-created `ExternalSecret` resources read `git-token` and `gitops-token`.
4. ESO creates runtime Kubernetes secrets for workflow pods.

### What was the original way?

The original guide uses a manual OpenBao write.

Guide step:

- Step 7.2 in `docs/Plans/OpenChoreo-v1.0-K3d-Installation-Guide.md`

Original command shape:

```bash
kubectl exec -n openbao openbao-0 -- sh -c "
  export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=root
  bao kv put secret/git-token git-token='${GITHUB_PAT}'
  bao kv put secret/gitops-token git-token='${GITHUB_PAT}'
"
```

Pulumi replaces that manual step with automated OpenBao writes when `github_pat` is configured.

## Step-by-Step Comparison

## Step 1: Create the K3d Cluster

Guide expectations:

- Download upstream k3d config
- Create cluster with `k3d cluster create`
- Verify cluster with `kubectl cluster-info` and `kubectl get nodes`

Pulumi coverage:

- Not part of the stack itself
- There is helper automation in `pulumi/scripts/bootstrap_k3d.py`

Status:

- Partially covered

What exists:

- `pulumi/scripts/bootstrap_k3d.py` downloads and patches the upstream k3d config
- It can optionally patch for Cilium
- It creates the cluster if needed
- It verifies cluster availability
- It then runs `pulumi up`

Gap:

- Cluster creation is still external to the Pulumi resource graph
- The guide describes this as a first-class step; Pulumi assumes the cluster already exists by the time the stack runs

Recommendation:

- Keep bootstrap outside the Pulumi graph, but document it as a required pre-stack phase
- Decide whether `bootstrap_k3d.py` is the supported path and explicitly align the guide with it

## Step 2: Install Platform Prerequisites

Guide expectations:

- Gateway API CRDs
- cert-manager
- External Secrets Operator
- kgateway
- OpenBao
- ClusterSecretStore
- CoreDNS rewrite for k3d

Pulumi coverage:

- Implemented in `pulumi/components/prerequisites.py`
- OpenBao values in `pulumi/values/openbao.py`

Status:

- Covered, with some divergence

What is covered:

- Gateway API CRDs
- cert-manager
- External Secrets Operator
- kgateway CRDs
- kgateway controller for non-Cilium mode
- OpenBao helm install
- OpenBao bootstrap seeding
- `ClusterSecretStore/default`
- CoreDNS rewrite when `is_k3d = true`

Pulumi-specific divergence:

- When Cilium is enabled, Pulumi does not deploy kgateway controller. It creates a `GatewayClass` named `kgateway` backed by Cilium instead.

Relevant files:

- `pulumi/components/prerequisites.py`
- `pulumi/values/openbao.py`
- `pulumi/config.py`

Important operational note:

- OpenBao base bootstrap seeds placeholders, including fake Git tokens.
- A real `github_pat` overrides the workflow-relevant entries later via the `OpenBaoSecrets` dynamic provider.

Gap:

- No strong validation that the critical OpenBao keys actually exist with the expected names after deploy
- No explicit fail-fast if `github_pat` is missing while workflow builds are expected
- No explicit wait for ESO to report that the store is ready and the critical downstream secrets are synced

Recommendation:

- Add a validation step or dynamic provider check for:
  - `secret/git-token`
  - `secret/gitops-token`
  - `ClusterSecretStore/default` Ready
- Add a config validation rule for `github_pat` when workflows or GitOps are enabled for real use

## Step 3: Install Control Plane

Guide expectations:

- Install Thunder
- Create Backstage secret bridge via ExternalSecret
- Install control plane chart
- Label namespace

Pulumi coverage:

- Implemented in `pulumi/components/control_plane.py`
- Values in `pulumi/values/control_plane.py`

Status:

- Covered, with enhancements

What is covered:

- Thunder namespace and helm install
- Thunder bootstrap ConfigMap management
- Thunder bootstrap rerun job based on checksum changes
- Backstage `ExternalSecret`
- Control plane chart install
- Namespace label

Pulumi-specific improvements:

- Uses internal Thunder service URLs for token and JWKS paths where needed
- Adds a rerun job for Thunder setup, which is more robust than the guide's one-shot framing
- Applies a workflow CRD patch after control plane deployment to replace k3d-host-specific registry endpoints with internal service endpoints

Guide gap relative to Pulumi:

- The guide does not mention the internal URL adjustments needed for reliable in-cluster behavior
- The guide does not mention the workflow CRD post-install patching that Pulumi performs

Pulumi gap relative to guide intent:

- No explicit "all control plane deployments ready" wait beyond Helm behavior and later integration testing

Recommendation:

- Document the internal endpoint behavior in the guide-derived plan
- Add explicit readiness validation for critical control plane deployments if needed

## Step 4: Install Data Plane

Guide expectations:

- Install data plane chart
- Wait for `cluster-agent-tls`
- Register `ClusterDataPlane`

Pulumi coverage:

- Implemented in `pulumi/components/data_plane.py`
- Plane registration helper in `pulumi/helpers/register_plane.py`

Status:

- Covered

What is covered:

- Namespace creation
- CA copy
- Data plane helm install
- `ClusterDataPlane` registration

Pulumi-specific behavior:

- Adds `secretStoreRef: { name: default }`
- Adds gateway ingress configuration
- Adds Cilium gateway ingress network policy in Cilium mode

Guide gap relative to Pulumi:

- The guide does not mention the extra policy/fixups required in the Cilium-backed path

Recommendation:

- Treat the current Pulumi data plane behavior as the canonical implementation for the Cilium-enabled path
- Update the guide-derived documentation to capture the Cilium ingress policy requirement

## Step 5: Install Workflow Plane

Guide expectations:

- Install registry
- Install workflow plane chart
- Apply workflow templates
- Register `ClusterWorkflowPlane`

Pulumi coverage:

- Implemented in `pulumi/components/workflow_plane.py`

Status:

- Covered, but with important runtime divergence

What is covered:

- Namespace creation
- Docker registry install
- CA copy
- Workflow plane install
- Workflow template application
- `ClusterWorkflowPlane` registration

Important divergence:

- Pulumi does not blindly apply the upstream workflow template YAML.
- It patches k3d-specific hostnames inline before applying the templates.

Patched concerns:

- Registry endpoint translation to in-cluster service DNS
- Gateway endpoint translation to in-cluster service DNS

Why this matters:

- This is one of the places where the original guide is incomplete if the goal is a reliable Pulumi-managed environment.
- The runtime behavior depends on internal endpoints, not just raw upstream template manifests.

Gap:

- No explicit post-apply validation that the workflow templates contain the expected rewritten endpoints

Recommendation:

- Keep the patching behavior
- Document it clearly in the guide-derived plan
- Consider replacing the shell-based patch/apply with explicit Pulumi-managed manifest transformations if maintainability becomes an issue

## Step 6: Install Observability Plane

Guide expectations:

- Namespace and CA
- OpenSearch-related ExternalSecrets
- machine-id init for Fluent Bit on k3d
- Install observability core and modules
- Register `ClusterObservabilityPlane`
- Link planes to observability

Pulumi coverage:

- Implemented in `pulumi/components/observability_plane.py`
- Linking in `pulumi/components/link_planes.py`

Status:

- Covered

What is covered:

- Namespace creation
- CA copy
- OpenSearch admin credentials ExternalSecret
- Observer OpenSearch credentials ExternalSecret
- Observer secret ExternalSecret
- machine-id initialization on k3d
- Observability core chart
- Logs OpenSearch chart
- Traces OpenSearch chart
- Metrics Prometheus chart
- `ClusterObservabilityPlane` registration
- Plane linking

Pulumi-specific behavior:

- Automates the machine-id step that the guide performs manually
- Applies Prometheus-specific tuning not described in the original guide

Gap:

- No explicit wait that all observability subcomponents report healthy before linking and later usage

Recommendation:

- Add validation gates if observability is intended to be consistently enabled in development

## Step 7: Install Flux CD and GitOps

Guide expectations:

- Install Flux
- Wait for Flux controllers
- Store GitHub PAT in OpenBao
- Apply GitRepository and Kustomizations
- Verify that Flux resources become Ready and that synced resources exist

Pulumi coverage:

- Implemented in `pulumi/components/flux_gitops.py`
- PAT write lives earlier in `pulumi/components/prerequisites.py`

Status:

- Mostly covered

What is covered:

- Flux manifest install
- Wait for core Flux deployments
- GitRepository creation
- Kustomization creation

Gap:

- Pulumi waits for Flux deployments, but not for Flux `Kustomization` readiness
- Pulumi does not validate that synced GitOps resources actually appeared after Flux reconciliation
- The guide's manual PAT step is not described as a Pulumi config prerequisite in a strong enough way

Recommendation:

- Add a wait/check for Flux `Kustomization` Ready status
- Add an explicit validation that expected synced resource classes exist after Flux is installed
- Make `github_pat` requirement explicit in the plan for any real workflow/GitOps usage

## What The Original Guide Misses Compared To The Pulumi Reality

These are not missing in Pulumi. They are missing or under-described in the original guide if the goal is to match how this repo actually works now.

### 1. Pulumi relies on internal service endpoints in several places

Examples:

- Internal Thunder URLs
- Internal registry endpoint rewrites
- Internal workflow endpoint rewrites

Relevant files:

- `pulumi/values/control_plane.py`
- `pulumi/components/control_plane.py`
- `pulumi/components/workflow_plane.py`

### 2. Cilium-enabled mode is not just a small flag

It changes:

- Gateway controller model
- Traffic handling
- Required ingress permissions

Relevant files:

- `pulumi/components/cilium.py`
- `pulumi/components/prerequisites.py`
- `pulumi/components/data_plane.py`

### 3. Secret flow needs explicit validation, not only resource creation

Recent runtime debugging showed that a missing `git-token` or `gitops-token` in OpenBao blocks workflow execution immediately.

The guide explains how to write the secret, but neither the guide nor Pulumi currently elevates validation of the end-to-end secret flow strongly enough.

### 4. Flux readiness is different from Flux installation

Installing Flux controllers is not enough. The practical success condition is that GitRepository and Kustomizations become Ready and the expected synced resources appear.

## What Pulumi Still Needs To Add Or Tighten

## Priority 0: Make platform handling first-class — DONE

Implemented in `pulumi/platforms/`.

## Priority 1: PAT and OpenBao validation — DONE

Implemented:

- `pulumi.log.warn` when `github_pat` is absent but Flux/GitOps is enabled
- `ValidateOpenBaoSecrets` dynamic provider checks `secret/git-token` and `secret/gitops-token` exist with correct fields
- Runs after PAT write, before downstream components

## Priority 2: External Secrets and critical secret sync waits — DONE

Implemented:

- `WaitCustomResourceCondition` dynamic provider polls CR conditions
- `ClusterSecretStore/default` now waited on for `Ready` condition before control plane proceeds
- Control plane depends on `cluster_secret_store_ready` instead of raw `cluster_secret_store`

## Priority 3: Flux reconciliation validation — DONE

Implemented:

- `WaitCustomResourceCondition` waits for `oc-demo-projects` Kustomization `Ready` condition
- `FluxGitOpsResult` now exposes `kustomizations_ready`
- Flux deployment no longer stops at object creation

## Priority 4: Make the supported bootstrap path explicit — DONE

Implemented:

- `pulumi/scripts/bootstrap.py` — dispatcher that routes to platform-specific scripts
- `pulumi/scripts/bootstrap_k3d.py` — downloads k3d config, creates cluster, runs `pulumi up -s dev`
- `pulumi/scripts/bootstrap_rancher_desktop.py` — validates existing cluster, runs `pulumi up -s rancher-desktop`

Supported bootstrap paths:

```
uv run scripts/bootstrap.py k3d [cluster-name]
uv run scripts/bootstrap.py rancher-desktop
```

## Priority 5: Document Pulumi-specific divergences — DONE

Documented inline below.

### Supported platforms and bootstrap

| Platform | Bootstrap | Stack | Gateway | CNI |
|----------|-----------|-------|---------|-----|
| k3d | `scripts/bootstrap_k3d.py` | `dev` | kgateway | flannel |
| Rancher Desktop | `scripts/bootstrap_rancher_desktop.py` | `rancher-desktop` | cilium | cilium |
| Talos | (future) | (future) | cilium | cilium |

### Platform profile model

Platform behavior is defined in `pulumi/platforms/`. Each platform is a frozen `PlatformProfile` dataclass. The resolver in `pulumi/platforms/resolver.py` maps the `platform` config key to a profile. Components branch on `cfg.platform.*` fields, not raw booleans.

To add a new platform:

1. Create `pulumi/platforms/<name>.py` with a `PlatformProfile` instance
2. Register it in `_from_name()` in `resolver.py`
3. Create `pulumi/Pulumi.<name>.yaml` with `platform: <name>` plus credentials
4. Optionally add `scripts/bootstrap_<name>.py` and register in `scripts/bootstrap.py`

### Secret flow

1. `github_pat` is set in stack config (encrypted)
2. Pulumi writes it to OpenBao as `secret/git-token` and `secret/gitops-token`
3. `ValidateOpenBaoSecrets` verifies both keys exist with correct fields
4. `ClusterSecretStore/default` is waited on for Ready condition
5. ExternalSecret resources in workflow namespaces read from OpenBao via ESO
6. If `github_pat` is missing with Flux/GitOps enabled, Pulumi warns at deploy time

### Workflow template patching

Pulumi patches upstream workflow templates to replace k3d-host-specific registry and gateway endpoints with internal service DNS names. This happens in `components/workflow_plane.py`.

### Cilium gateway mode

When the platform profile uses `gateway_mode: cilium`, Pulumi:

- Skips deploying the kgateway controller
- Creates a `GatewayClass` named `kgateway` backed by `io.cilium/gateway-controller`
- Deploys a `CiliumClusterwideNetworkPolicy` allowing gateway ingress to data-plane workloads

### Flux readiness

Pulumi waits for the final `oc-demo-projects` Kustomization to report `Ready`, not just for Flux controllers to start.

## Recommended Implementation Plan

## Phase 0: Platform model refactor — DONE

## Phase 1: Hardening secret flow — DONE

## Phase 2: Hardening Flux and workflow readiness — DONE

## Phase 3: Documentation alignment — DONE (inline above)

## Proposed Concrete Next Tasks

### Task 0 — DONE

Platform profiles for k3d and rancher-desktop. Talos reserved.

### Task A — DONE

All `is_k3d` and `enable_cilium` conditionals migrated to `cfg.platform.*` fields. Legacy fields removed from config.

### Task B — DONE

`pulumi.log.warn` fires when `github_pat` is absent but Flux/GitOps is enabled.

### Task C — DONE

`ValidateOpenBaoSecrets` dynamic provider asserts `secret/git-token` and `secret/gitops-token` exist with correct field layout.

### Task D — DONE

`WaitCustomResourceCondition` waits for `ClusterSecretStore/default` Ready. Control plane depends on this gate.

### Task E — DONE

`WaitCustomResourceCondition` waits for `oc-demo-projects` Kustomization Ready.

### Task F — DONE

Platform bootstrap paths documented. Secret flow, Cilium gateway mode, workflow patching, and Flux readiness documented inline in this plan.

## Final Assessment

All planned priorities (0-5) and tasks (0, A-F) are now implemented.

What was delivered:

- First-class platform profile model (`pulumi/platforms/`) replacing scattered `is_k3d`/`enable_cilium` booleans
- k3d, rancher-desktop, and talos (placeholder) profiles
- Legacy config fields (`is_k3d`, `enable_cilium`, `cilium_k8s_api_host`) removed from `OpenChoreoConfig`
- Stack YAML files cleaned to only carry `platform` + credentials + feature flags
- PAT warning when `github_pat` missing with Flux/GitOps enabled
- OpenBao secret validation (`ValidateOpenBaoSecrets`)
- `ClusterSecretStore/default` Ready gate before control plane deployment
- Flux `Kustomization` Ready wait before reporting success
- Per-platform bootstrap scripts with dispatcher
- Documentation of platform model, secret flow, Cilium mode, workflow patching, and Flux readiness

Remaining future work:

- Implement Talos profile behavior once hardware/VM is available
- Add cloud platform profiles (AWS, GCP, Azure) when those targets are active
- Add ExternalSecret Ready waits for observability and control-plane secret bridges (optional hardening)