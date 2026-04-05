# OpenChoreo Infrastructure Remediation Plan

**Date**: 2026-04-04  
**Version**: 1.0  
**Related Document**: [Infrastructure Gap Analysis](./infrastructure-gap-analysis.md)

---

## Overview

This document provides a detailed implementation plan for addressing the 15 gaps identified in the infrastructure gap analysis. The plan is organized into 4 phases spanning 8 weeks, with clear deliverables and acceptance criteria for each task.

---

## Phase 1: Security Hardening (Weeks 1-2)

### 1.1 GAP-9: Migrate Secrets to External Secret Management

**Priority**: P1  
**Estimated Effort**: 3 days  
**Owner**: TBD

#### Objective
Remove hardcoded credentials from Pulumi config files and integrate with an external secret provider.

#### Tasks

- [ ] **Task 1.1.1**: Evaluate Pulumi ESC vs External Secrets Operator for bootstrap secrets
  - Decision criteria: CI/CD integration, OIDC support, team familiarity
  - Document decision in ADR

- [ ] **Task 1.1.2**: Set up Pulumi ESC environment (if chosen)
  ```bash
  pulumi config env init openchoreo/prod
  pulumi env set openchoreo/prod github_pat --secret
  pulumi env set openchoreo/prod openbao_root_token --secret
  ```

- [ ] **Task 1.1.3**: Update `config.py` to read from environment
  ```python
  # Before
  github_pat = cfg.get_secret("github_pat") or ""
  
  # After  
  github_pat = os.environ.get("GITHUB_PAT") or cfg.get_secret("github_pat") or ""
  ```

- [ ] **Task 1.1.4**: Remove encrypted secrets from `Pulumi.*.yaml` files

- [ ] **Task 1.1.5**: Update CI/CD pipeline to inject secrets via environment

#### Acceptance Criteria
- [ ] No secrets in version control (verify with `git-secrets` scan)
- [ ] `pulumi up` works with secrets from external source
- [ ] Documentation updated with new secret management flow

---

### 1.2 GAP-2: Production-Ready OpenBao Configuration

**Priority**: P1  
**Estimated Effort**: 5 days  
**Owner**: TBD

#### Objective
Replace OpenBao dev mode with a production-ready configuration using persistent storage.

#### Tasks

- [ ] **Task 1.2.1**: Create `values/openbao_production.py` with file storage backend
  ```python
  def get_production_values(storage_class: str) -> dict:
      return {
          "server": {
              "dev": {"enabled": False},
              "standalone": {
                  "enabled": True,
                  "config": """
                      storage "file" {
                          path = "/openbao/data"
                      }
                      listener "tcp" {
                          address = "0.0.0.0:8200"
                          tls_disable = true
                      }
                  """
              },
              "dataStorage": {
                  "enabled": True,
                  "size": "10Gi",
                  "storageClass": storage_class,
              },
          },
          "injector": {"enabled": False},
      }
  ```

- [ ] **Task 1.2.2**: Add `is_production` config flag to `config.py`
  ```python
  is_production = cfg.get_bool("is_production") or False
  ```

- [ ] **Task 1.2.3**: Create initialization Job for production mode
  - Initialize OpenBao on first run
  - Store unseal keys in Kubernetes Secret (temporary) or external KMS
  - Implement auto-unseal with Kubernetes auth

- [ ] **Task 1.2.4**: Update `prerequisites.py` to conditionally use production values

- [ ] **Task 1.2.5**: Create migration script for dev → production
  - Export secrets from dev mode
  - Import into production instance
  - Verify all ExternalSecrets resync

- [ ] **Task 1.2.6**: Update ClusterSecretStore for production endpoint

#### Acceptance Criteria
- [ ] OpenBao persists secrets across pod restarts
- [ ] Unseal process is documented (manual or auto)
- [ ] All ExternalSecrets sync successfully with production OpenBao
- [ ] Dev mode still works for local development

---

### 1.3 GAP-8: Implement Network Policies

**Priority**: P1  
**Estimated Effort**: 4 days  
**Owner**: TBD

#### Objective
Implement namespace isolation with default-deny policies and explicit allow rules.

#### Tasks

- [ ] **Task 1.3.1**: Create `components/network_policies.py` module
  ```python
  def deploy_network_policies(
      cfg: OpenChoreoConfig,
      depends: list[pulumi.Resource],
  ) -> list[pulumi.Resource]:
      policies = []
      
      # Default deny for each namespace
      for ns in [NS_CONTROL_PLANE, NS_DATA_PLANE, NS_WORKFLOW_PLANE, NS_OPENBAO]:
          policies.append(_default_deny(ns))
      
      # Explicit allows
      policies.extend(_openbao_policies())
      policies.extend(_control_plane_policies())
      # ...
      
      return policies
  ```

- [ ] **Task 1.3.2**: Define allow policies for each namespace pair
  
  | Source Namespace | Destination Namespace | Ports | Reason |
  |-----------------|----------------------|-------|--------|
  | openchoreo-control-plane | openbao | 8200 | ESO secret sync |
  | openchoreo-data-plane | openbao | 8200 | ESO secret sync |
  | openchoreo-workflow-plane | openbao | 8200 | ESO secret sync |
  | openchoreo-control-plane | thunder | 8090 | OIDC/JWKS |
  | * | openchoreo-control-plane | 443 | Gateway ingress |

- [ ] **Task 1.3.3**: Create Cilium-specific policies (CiliumNetworkPolicy) for L7 rules
  ```yaml
  apiVersion: cilium.io/v2
  kind: CiliumNetworkPolicy
  metadata:
    name: openbao-api-access
    namespace: openbao
  spec:
    endpointSelector:
      matchLabels:
        app.kubernetes.io/name: openbao
    ingress:
    - fromEndpoints:
      - matchLabels:
          io.kubernetes.pod.namespace: openchoreo-control-plane
      toPorts:
      - ports:
        - port: "8200"
          protocol: TCP
        rules:
          http:
          - method: "GET"
            path: "/v1/secret/data/.*"
  ```

- [ ] **Task 1.3.4**: Add integration tests for network policy enforcement

- [ ] **Task 1.3.5**: Document network policy architecture

#### Acceptance Criteria
- [ ] Default-deny policy in all OpenChoreo namespaces
- [ ] All plane-to-plane communication explicitly allowed
- [ ] Integration tests verify policy enforcement
- [ ] No regression in functionality

---

## Phase 2: Reliability (Weeks 3-4)

### 2.1 GAP-1: Implement Per-Namespace Certificates

**Priority**: P2  
**Estimated Effort**: 3 days  
**Owner**: TBD

#### Objective
Replace cross-namespace secret copying with per-namespace Certificate resources.

#### Tasks

- [ ] **Task 2.1.1**: Create Certificate resource for each plane namespace
  ```python
  # In data_plane.py
  dp_gateway_cert = k8s.apiextensions.CustomResource(
      "dp-gateway-cert",
      api_version="cert-manager.io/v1",
      kind="Certificate",
      metadata=k8s.meta.v1.ObjectMetaArgs(
          name="cluster-gateway-ca",
          namespace=NS_DATA_PLANE,
      ),
      spec={
          "secretName": "cluster-gateway-ca",
          "issuerRef": {
              "name": "openchoreo-ca",
              "kind": "ClusterIssuer",
          },
          "commonName": "cluster-gateway",
          "dnsNames": ["*.openchoreo-data-plane.svc.cluster.local"],
      },
  )
  ```

- [ ] **Task 2.1.2**: Update Helm values to reference local secrets
  - Modify `values/data_plane.py`, `values/workflow_plane.py`, etc.
  - Change `cluster-gateway-ca` ConfigMap references to Secret references

- [ ] **Task 2.1.3**: Remove `helpers/copy_ca.py` and related code

- [ ] **Task 2.1.4**: Add cert-manager Certificate readiness checks

- [ ] **Task 2.1.5**: Update integration tests for new certificate flow

#### Acceptance Criteria
- [ ] Each namespace has its own Certificate resource
- [ ] No cross-namespace secret copying
- [ ] Certificate rotation handled by cert-manager
- [ ] All planes communicate successfully

---

### 2.2 GAP-5: Add Health Check Waits

**Priority**: P2  
**Estimated Effort**: 2 days  
**Owner**: TBD

#### Objective
Ensure components are fully ready before dependent resources are created.

#### Tasks

- [ ] **Task 2.2.1**: Add `wait=True` to all Helm releases
  ```python
  # Update all k8s.helm.v3.Release calls
  openbao_chart = k8s.helm.v3.Release(
      "openbao",
      ...,
      wait=True,
      wait_for_jobs=True,
      timeout=600,
  )
  ```

- [ ] **Task 2.2.2**: Create `WaitForExternalSecretSync` dynamic provider
  ```python
  class WaitForExternalSecretSync(ResourceProvider):
      def create(self, props: dict) -> CreateResult:
          # Poll ExternalSecret status until Ready
          while True:
              es = get_external_secret(props["name"], props["namespace"])
              if es.status.conditions.get("Ready") == "True":
                  break
              time.sleep(5)
          return CreateResult(id_=props["name"], outs=props)
  ```

- [ ] **Task 2.2.3**: Add waits for critical paths:
  - OpenBao StatefulSet → ClusterSecretStore
  - ClusterSecretStore → ExternalSecrets
  - ExternalSecrets → Helm releases that need secrets

- [ ] **Task 2.2.4**: Add timeout configuration to config.py
  ```python
  deployment_timeouts = {
      "openbao": cfg.get_int("timeout_openbao") or 600,
      "control_plane": cfg.get_int("timeout_control_plane") or 900,
  }
  ```

#### Acceptance Criteria
- [ ] No race conditions between components
- [ ] Clear error messages on timeout
- [ ] Configurable timeouts per component

---

### 2.3 GAP-14: Add Resource Limits

**Priority**: P2  
**Estimated Effort**: 2 days  
**Owner**: TBD

#### Objective
Define resource requests and limits for all platform components.

#### Tasks

- [ ] **Task 2.3.1**: Profile current resource usage
  ```bash
  kubectl top pods -n openbao
  kubectl top pods -n openchoreo-control-plane
  # ... for all namespaces
  ```

- [ ] **Task 2.3.2**: Define resource profiles in `config.py`
  ```python
  RESOURCE_PROFILES = {
      "small": {"requests": {"cpu": "100m", "memory": "128Mi"}, "limits": {"cpu": "500m", "memory": "512Mi"}},
      "medium": {"requests": {"cpu": "250m", "memory": "256Mi"}, "limits": {"cpu": "1000m", "memory": "1Gi"}},
      "large": {"requests": {"cpu": "500m", "memory": "512Mi"}, "limits": {"cpu": "2000m", "memory": "2Gi"}},
  }
  
  COMPONENT_PROFILES = {
      "openbao": "medium",
      "backstage": "large",
      "thunder": "small",
      # ...
  }
  ```

- [ ] **Task 2.3.3**: Update all values files to include resources
  ```python
  # values/openbao.py
  def get_values(...) -> dict:
      return {
          ...,
          "server": {
              "resources": RESOURCE_PROFILES[COMPONENT_PROFILES["openbao"]],
          },
      }
  ```

- [ ] **Task 2.3.4**: Create LimitRange for each namespace
  ```python
  limit_range = k8s.core.v1.LimitRange(
      f"limitrange-{namespace}",
      metadata=k8s.meta.v1.ObjectMetaArgs(
          name="default-limits",
          namespace=namespace,
      ),
      spec=k8s.core.v1.LimitRangeSpecArgs(
          limits=[
              k8s.core.v1.LimitRangeItemArgs(
                  type="Container",
                  default={"cpu": "500m", "memory": "512Mi"},
                  default_request={"cpu": "100m", "memory": "128Mi"},
              ),
          ],
      ),
  )
  ```

#### Acceptance Criteria
- [ ] All components have explicit resource requests/limits
- [ ] LimitRange in each namespace provides defaults
- [ ] No OOM kills or CPU throttling under normal load

---

### 2.4 GAP-3: Create Kustomize Overlays for Templates

**Priority**: P2  
**Estimated Effort**: 3 days  
**Owner**: TBD

#### Objective
Replace sed-based template patching with Kustomize overlays.

#### Tasks

- [ ] **Task 2.4.1**: Create base workflow templates directory
  ```
  pulumi/workflow-templates/
  ├── base/
  │   ├── kustomization.yaml
  │   ├── publish-image.yaml
  │   └── ...
  └── overlays/
      ├── k3d/
      │   ├── kustomization.yaml
      │   └── patches/
      │       └── registry-endpoint.yaml
      └── baremetal/
          ├── kustomization.yaml
          └── patches/
              └── registry-endpoint.yaml
  ```

- [ ] **Task 2.4.2**: Create Kustomize replacement patches
  ```yaml
  # overlays/k3d/kustomization.yaml
  apiVersion: kustomize.config.k8s.io/v1beta1
  kind: Kustomization
  resources:
    - ../../base
  replacements:
    - source:
        kind: ConfigMap
        name: workflow-config
        fieldPath: data.registryEndpoint
      targets:
        - select:
            kind: ClusterWorkflowTemplate
          fieldPaths:
            - spec.templates.*.container.image
          options:
            delimiter: '/'
            index: 0
  ```

- [ ] **Task 2.4.3**: Update `workflow_plane.py` to use Kustomize
  ```python
  def apply_workflow_templates(cfg: OpenChoreoConfig, ...) -> pulumi.Resource:
      overlay = "k3d" if cfg.platform.name == "k3d" else "baremetal"
      
      return k8s.yaml.ConfigGroup(
          "workflow-templates",
          files=[f"workflow-templates/overlays/{overlay}"],
          transformations=[kustomize_transform],
      )
  ```

- [ ] **Task 2.4.4**: Remove sed-based patching code

#### Acceptance Criteria
- [ ] No sed commands in workflow template deployment
- [ ] Templates work correctly on k3d and baremetal
- [ ] Easy to add new platform overlays

---

## Phase 3: Simplification (Weeks 5-6)

### 3.1 GAP-4: Implement Pulumi Stack References

**Priority**: P3  
**Estimated Effort**: 4 days  
**Owner**: TBD

#### Objective
Connect the Talos bootstrap stack with the OpenChoreo stack using proper stack references.

#### Tasks

- [ ] **Task 3.1.1**: Add explicit exports to `talos-cluster-baremetal/__main__.py`
  ```python
  pulumi.export("kubeconfig_path", kubeconfig_file)
  pulumi.export("k8s_provider_kubeconfig", kubeconfig.kubeconfig_raw)
  pulumi.export("cilium_installed", True)
  pulumi.export("gateway_api_version", gateway_api_version)
  ```

- [ ] **Task 3.1.2**: Create stack reference in main Pulumi program
  ```python
  # __main__.py
  talos_stack = pulumi.StackReference(f"organization/talos-cluster-baremetal/{stack_name}")
  
  kubeconfig_raw = talos_stack.get_output("k8s_provider_kubeconfig")
  cilium_installed = talos_stack.get_output("cilium_installed")
  ```

- [ ] **Task 3.1.3**: Update platform detection to use stack reference
  ```python
  if cilium_installed:
      cfg.platform = talos_baremetal(cilium_pre_installed=True)
  ```

- [ ] **Task 3.1.4**: Remove duplicate Gateway API CRD installation

- [ ] **Task 3.1.5**: Document stack dependency in README

#### Acceptance Criteria
- [ ] Single `pulumi up` per stack (no cross-stack implicit dependencies)
- [ ] Stack references properly typed
- [ ] Documentation explains two-stack model

---

### 3.2 GAP-12: Migrate Integration Tests to pytest

**Priority**: P3  
**Estimated Effort**: 3 days  
**Owner**: TBD

#### Objective
Move integration tests out of Pulumi deployment into standalone pytest suite.

#### Tasks

- [ ] **Task 3.2.1**: Create `tests/integration/` directory structure
  ```
  tests/
  └── integration/
      ├── conftest.py          # Fixtures for k8s client, port-forward
      ├── test_prerequisites.py
      ├── test_control_plane.py
      ├── test_data_plane.py
      ├── test_workflow_plane.py
      └── test_e2e.py
  ```

- [ ] **Task 3.2.2**: Create pytest fixtures
  ```python
  # conftest.py
  import pytest
  from kubernetes import client, config
  
  @pytest.fixture(scope="session")
  def k8s_client():
      config.load_kube_config()
      return client.CoreV1Api()
  
  @pytest.fixture(scope="session")
  def custom_objects_client():
      config.load_kube_config()
      return client.CustomObjectsApi()
  ```

- [ ] **Task 3.2.3**: Migrate tests from `integration_tests.py`
  ```python
  # test_prerequisites.py
  def test_cert_manager_deployments(k8s_client):
      deps = k8s_client.list_namespaced_deployment("cert-manager")
      ready = [d for d in deps.items if d.status.ready_replicas == d.spec.replicas]
      assert len(ready) >= 3  # cert-manager, webhook, cainjector
  ```

- [ ] **Task 3.2.4**: Add CI/CD job for integration tests
  ```yaml
  # .github/workflows/integration-tests.yaml
  jobs:
    integration-test:
      runs-on: self-hosted
      steps:
        - uses: actions/checkout@v4
        - run: pip install -r tests/requirements.txt
        - run: pytest tests/integration/ -v --kubeconfig=$KUBECONFIG
  ```

- [ ] **Task 3.2.5**: Make Pulumi integration tests optional
  ```python
  # config.py
  run_integration_tests = cfg.get_bool("run_integration_tests") or False
  ```

#### Acceptance Criteria
- [ ] All existing tests migrated to pytest
- [ ] Tests can run independently of `pulumi up`
- [ ] CI/CD pipeline runs tests on schedule
- [ ] `pulumi up` completes faster without tests

---

### 3.3 GAP-6: Fix Thunder Bootstrap Idempotency

**Priority**: P3  
**Estimated Effort**: 1 day  
**Owner**: TBD

#### Tasks

- [ ] **Task 3.3.1**: Add `delete_before_replace=True` to Thunder setup Job
- [ ] **Task 3.3.2**: Reduce `ttl_seconds_after_finished` to 300
- [ ] **Task 3.3.3**: Add Job name suffix with checksum for uniqueness

---

### 3.4 GAP-10: Make Flux Paths Configurable

**Priority**: P3  
**Estimated Effort**: 1 day  
**Owner**: TBD

#### Tasks

- [ ] **Task 3.4.1**: Add config keys for GitOps paths
  ```python
  gitops_base_path = cfg.get("gitops_base_path") or "./"
  gitops_namespace_path = cfg.get("gitops_namespace_path") or "namespaces"
  gitops_platform_path = cfg.get("gitops_platform_path") or "namespaces/default/platform"
  ```

- [ ] **Task 3.4.2**: Update `flux_gitops.py` to use config values

---

## Phase 4: Production Readiness (Weeks 7-8)

### 4.1 GAP-11: Implement Backup Strategy

**Priority**: P3  
**Estimated Effort**: 5 days  
**Owner**: TBD

#### Tasks

- [ ] **Task 4.1.1**: Configure Longhorn backup target
  ```yaml
  # Add to Longhorn Helm values
  defaultSettings:
    backupTarget: "s3://openchoreo-backups@us-east-1/"
    backupTargetCredentialSecret: "longhorn-backup-credentials"
  ```

- [ ] **Task 4.1.2**: Create recurring Longhorn backup jobs
- [ ] **Task 4.1.3**: Document OpenBao backup procedure
- [ ] **Task 4.1.4**: Create disaster recovery runbook

---

### 4.2 GAP-15: Add Platform Alerting

**Priority**: P4  
**Estimated Effort**: 3 days  
**Owner**: TBD

#### Tasks

- [ ] **Task 4.2.1**: Create PrometheusRules for platform components
  ```yaml
  apiVersion: monitoring.coreos.com/v1
  kind: PrometheusRule
  metadata:
    name: openchoreo-platform-alerts
  spec:
    groups:
    - name: openchoreo.rules
      rules:
      - alert: OpenBaoSealed
        expr: openbao_core_unsealed == 0
        for: 5m
        labels:
          severity: critical
      - alert: ExternalSecretSyncFailed
        expr: externalsecret_status_condition{condition="Ready"} == 0
        for: 10m
        labels:
          severity: warning
  ```

- [ ] **Task 4.2.2**: Configure alerting destination (Slack, PagerDuty, email)
- [ ] **Task 4.2.3**: Create runbook for each alert

---

## Quick Wins (Can Be Done Anytime)

These tasks can be implemented independently with minimal risk:

| Task | File | Change |
|------|------|--------|
| Add `wait=True` to Helm releases | `components/*.py` | Add `wait=True, timeout=600` |
| Add `.gitignore` for outputs | `talos-cluster-baremetal/.gitignore` | Add `outputs/` |
| Add Job cleanup timeout | `components/control_plane.py` | Reduce TTL to 300s |
| Document two-phase flow | `README.md` | Add installation section |
| Add kubeconfig context validation | `config.py` | Validate context exists |

---

## Tracking

### Status Legend
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked

### Progress Dashboard

| Phase | Tasks | Complete | Status |
|-------|-------|----------|--------|
| Phase 1: Security | 18 | 0 | ⬜ |
| Phase 2: Reliability | 17 | 0 | ⬜ |
| Phase 3: Simplification | 12 | 0 | ⬜ |
| Phase 4: Production | 7 | 0 | ⬜ |
| Quick Wins | 5 | 0 | ⬜ |
| **Total** | **59** | **0** | **0%** |

---

## Appendix A: Resource Requirements

### Estimated Time Investment
- Phase 1: 12 person-days
- Phase 2: 10 person-days
- Phase 3: 9 person-days
- Phase 4: 8 person-days
- **Total**: ~39 person-days (8 weeks at 50% allocation)

### Infrastructure Requirements
- Test cluster for validation
- Backup storage (S3/MinIO)
- Pulumi Cloud or self-hosted backend
- CI/CD runner with cluster access

---

## Appendix B: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing deployments | Feature flags, gradual rollout |
| Secret migration data loss | Full backup before migration |
| Network policy lockout | Test in staging first, have escape hatch |
| Performance regression | Profile before/after each phase |
