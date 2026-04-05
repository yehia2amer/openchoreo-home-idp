# Draft: FluxCD Pipeline Consolidation

## Original Request
User wants to consolidate the current 4-step deployment pipeline:
1. **Pulumi Step 1** (KEEP): Talos + Cilium + Longhorn + **move OpenBao here**
2. **Pulumi Step 2** → FluxCD: OpenChoreo dependencies → OpenChoreo
3. **Pulumi Step 3** → FluxCD: FluxCD + monitoring tools
4. **Pulumi Step 4** → FluxCD: Apps etc

**Proposed new architecture:**
- Step 1 (Pulumi): Talos + Cilium + Longhorn + **OpenBao** (imperative needs)
- Steps 2-4 (FluxCD): Everything else via `dependsOn` chains

## Requirements (confirmed)
- Move OpenBao to Pulumi Step 1 (baremetal stack) — rationale: imperative setup needs
- Use FluxCD `dependsOn` for multi-step dependent deployments in Steps 2-4
- FluxCD would manage: cert-manager, ESO, kgateway, OpenChoreo planes, monitoring, apps

## Research Findings

### Current Pipeline (main Pulumi stack)
```
Step 0: Cilium (conditional)
Step 1: Prerequisites (cert-manager, ESO, kgateway, OpenBao, ClusterSecretStore)
Step 1.5: TLS Setup (self-signed CA chain)
Step 2: Control Plane (Thunder IdP, CP Helm)
Step 3: Data Plane (DP Helm, register)
Step 4: Workflow Plane (registry, WP Helm, templates, register)
Step 5: Observability Plane (optional)
Step 6: Link Planes
Step 7: Flux CD & GitOps
Step 8: Integration Tests
```

### FluxCD CAN handle (~70%)
- All Helm chart deployments with `dependsOn` ordering
- CRD-before-operator patterns
- Health check-based readiness
- cert-manager → ESO → ClusterSecretStore → Control Plane → Data/Workflow/Obs Planes

### FluxCD CANNOT handle (~30% — 6 imperative operations)
1. **RegisterPlane** — reads TLS cert from secret, embeds in CRD spec (HARDEST)
2. **OpenBaoSecrets** — host port-forward + hvac to write GitHub PAT
3. **ValidateOpenBaoSecrets** — host port-forward + hvac reads
4. **CopyCA** — cross-namespace secret→configmap propagation
5. **Workflow CRD patching** — sed hostname replacement
6. **Workflow template application** — download + sed + kubectl apply

### OpenBao postStart script IS FluxCD-compatible
The auth enable, policies, roles, and dev secret seeding all run inside the pod
via a container lifecycle hook. FluxCD can deploy this Helm chart as-is.

## Technical Decisions
- [PENDING] How to handle RegisterPlane: K8s Job vs custom controller vs keep thin Pulumi
- [PENDING] How to handle CopyCA: K8s Job vs Helm post-install hook
- [PENDING] Where does FluxCD itself get installed? (Currently Pulumi installs Flux in Step 7)
- [PENDING] Should workflow templates use Kustomize overlays instead of sed patching?

## Open Questions
1. For OpenBao in Step 1: full production HA mode or keep dev mode?
2. The GitHub PAT injection — is this still needed? Could it be a manual step or K8s Job?
3. What's the target platform? Only talos-baremetal, or also k3d/rancher-desktop?
4. Should integration tests (Step 8) become a separate CI pipeline?
5. FluxCD bootstrap: `flux bootstrap` command in Pulumi Step 1, or manual?

## Scope Boundaries
- INCLUDE: Migration of Steps 2-4 to FluxCD, OpenBao move to Step 1
- INCLUDE: Design of FluxCD directory structure and dependsOn chain
- EXCLUDE: [PENDING — need to clarify multi-platform scope]
