# F4: Pulumi Preview Integration Test

Date: 2026-03-29

## Commands Run

1. `PULUMI_CONFIG_PASSPHRASE=openchoreo pulumi preview --stack dev`
2. `python3 -m compileall -q components/ policy/ values/ scripts/ templates/ __main__.py`
3. `PULUMI_CONFIG_PASSPHRASE=openchoreo pulumi preview --stack dev --policy-pack ./policy`

## Output (trimmed to relevant sections)

### 1) Pulumi Preview (dev stack)

```text
Previewing update (dev):

 +  pulumi:pulumi:Stack openchoreo-dev create
 +  openchoreo:components:Prerequisites prerequisites create
 +  openchoreo:components:DataPlane data-plane create
 +  openchoreo:components:ObservabilityPlane observability-plane create
 +  openchoreo:components:LinkPlanes link-planes create
 +  openchoreo:components:WorkflowPlane workflow-plane create
 +  pulumi:providers:kubernetes k8s create
 +  openchoreo:components:FluxGitOps flux-gitops create
 +  openchoreo:components:ControlPlane control-plane create
 +  openchoreo:components:IntegrationTests integration-tests create

error: kubernetes:yaml/v2:ConfigGroup resource 'gateway-api-crds' has a problem:
configured Kubernetes cluster is unreachable:
Get "https://0.0.0.0:6550/openapi/v2?timeout=32s": dial tcp 0.0.0.0:6550: connect: connection refused

Resources:
    + 10 to create
    1 errored
```

### 2) Python compilation

```text
(no output)
```

`python3 -m compileall -q ...` returned with no errors.

### 3) Pulumi Preview with Policy Pack

```text
Loading policy packs...: done

 +  pulumi:pulumi:Stack openchoreo-dev create
 +  openchoreo:components:Prerequisites prerequisites create
 +  openchoreo:components:FluxGitOps flux-gitops create
 +  pulumi:providers:kubernetes k8s create
 +  openchoreo:components:ControlPlane control-plane create
 +  openchoreo:components:DataPlane data-plane create
 +  openchoreo:components:LinkPlanes link-planes create
 +  openchoreo:components:WorkflowPlane workflow-plane create
 +  openchoreo:components:IntegrationTests integration-tests create
 +  openchoreo:components:ObservabilityPlane observability-plane create

Policies:
    ✅ openchoreo-policy@v0.0.1 (local: policy)

error: kubernetes:yaml/v2:ConfigGroup resource 'gateway-api-crds' has a problem:
configured Kubernetes cluster is unreachable:
Get "https://0.0.0.0:6550/openapi/v2?timeout=32s": dial tcp 0.0.0.0:6550: connect: connection refused

Resources:
    + 10 to create
    1 errored
```

## Interpretation

- Outcome classification: **Outcome B — Kubernetes Connection Error**.
- Pulumi program startup succeeded far enough to evaluate stack/component graph and outputs.
- No Python import/syntax failures were observed in preview output.
- `compileall` check passed (no errors), which further confirms Python modules compile.
- Policy pack loaded successfully (`openchoreo-policy@v0.0.1`).

### Create/Delete operation assessment

- Preview did **not** reach full completion due unreachable local Kubernetes API (`0.0.0.0:6550`).
- The current preview shows planned creates (`+ 10 to create`) and no deletes in this failed run.
- Because the run stops at cluster schema access, this environment cannot fully validate alias-migration behavior end-to-end against a live cluster/state.

## Checklist Against Expected Outcome

- [x] `pulumi preview --stack dev` runs without Python import errors
- [x] Report on whether there are unexpected create/delete operations
- [x] Findings written to `docs/pulumi-improvements-reviews/f4-pulumi-preview-test.md`

## VERDICT

**APPROVE (with environment caveat)**

Reason: This dev run matches expected local behavior when the cluster is down (connection refused), Python code compiles cleanly, and policy pack integration works. Full alias migration validation for create/delete parity still requires rerunning preview against a reachable Kubernetes cluster and existing stack state.
