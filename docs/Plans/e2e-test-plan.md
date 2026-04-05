# E2E Test Plan: OpenChoreo Real Environment Validation

**Date**: 2026-04-05
**Motivation**: The frontend CrashLoopBackOff incident (see `openchoreo-frontend-crashloop-diagnosis-and-fix.md`) showed that our existing smoke tests only verify infrastructure health — they don't catch broken application deployments, unresolved dependencies, or failed CI pipelines. We need E2E tests that run against real environments and tell us "your platform is actually working end-to-end."

---

## 1. What the Existing Tests Cover vs. What They Miss

### Currently Covered (Smoke Tests — `tests/`)
| Layer | What's Tested |
|-------|--------------|
| Infrastructure | Cilium DaemonSet, cert-manager certs, ESO sync, OpenBao health |
| Control Plane | Backstage health, Thunder OIDC, OpenChoreo API health |
| Data Plane | Gateway programmed, HTTPRoutes accepted |
| Workflow Plane | Argo server ready, Docker registry health |
| Observability | OpenSearch cluster, Prometheus targets, Observer health |
| GitOps | Flux controllers ready, Kustomizations reconciling |

### Not Covered (What Would Have Caught the CrashLoop)
| Gap | What Would Have Caught |
|-----|----------------------|
| **OpenChoreo resource chain validation** | ReleaseBinding stuck at "2 connections pending" |
| **Application pod health (not just Deployment exists)** | Pod in CrashLoopBackOff with 68+ restarts |
| **Dependency resolution verification** | `env: []` in RenderedRelease instead of `DOC_SERVICE_URL` |
| **WorkflowRun completion tracking** | `frontend-build-002` failed silently at `generate-gitops-resources` |
| **GitOps repo state consistency** | `document-svc` and `collab-svc` missing `releases/` directories |
| **Cross-component dependency graph** | Frontend deployed before its dependencies existed |
| **End-to-end user journey** | "Can I actually open the frontend app?" |

---

## 2. E2E Test Architecture

```
tests/
├── conftest.py                         # Existing fixtures (k8s, auth, http)
├── utils/                              # Existing helpers
│   ├── openchoreo_helpers.py           # NEW: OpenChoreo CRD helpers
│   └── github_helpers.py              # NEW: GitOps repo state checks
│
├── infrastructure/                     # Existing smoke tests
├── control_plane/                      # Existing smoke tests
├── ...
│
├── e2e/                                # NEW: End-to-end tests
│   ├── __init__.py
│   ├── conftest.py                     # E2E-specific fixtures
│   │
│   ├── test_resource_chain.py          # Layer 1: OpenChoreo resource chain
│   ├── test_dependency_resolution.py   # Layer 2: Cross-component dependencies
│   ├── test_workflow_pipeline.py       # Layer 3: CI/CD pipeline health
│   ├── test_gitops_consistency.py      # Layer 4: GitOps repo ↔ cluster sync
│   ├── test_application_health.py      # Layer 5: Application-level health
│   └── test_user_journeys.py           # Layer 6: End-to-end user scenarios
│
└── pytest.ini                          # Marker registration
```

---

## 3. Test Layers (Bottom-Up)

### Layer 1: OpenChoreo Resource Chain Validation
**Purpose**: Verify every link in the chain: Component → Workload → ComponentRelease → ReleaseBinding → RenderedRelease → Deployment → Pod

**File**: `tests/e2e/test_resource_chain.py`

```python
@pytest.mark.e2e
@pytest.mark.resource_chain
class TestOpenChoreoResourceChain:
    """Verify the full OpenChoreo resource chain for every component."""

    @pytest.mark.parametrize("component", ["frontend", "document-svc", "collab-svc", "nats", "postgres"])
    def test_component_exists(self, k8s_custom_api, component):
        """Every declared component has a Component CR in the cluster."""
        component_cr = get_openchoreo_resource(k8s_custom_api, "components", component)
        assert component_cr is not None, f"Component '{component}' CR missing from cluster"

    @pytest.mark.parametrize("component", ["frontend", "document-svc", "collab-svc", "nats", "postgres"])
    def test_workload_exists(self, k8s_custom_api, component):
        """Every component has a Workload CR."""
        workload = get_openchoreo_resource(k8s_custom_api, "workloads", f"{component}-workload")
        assert workload is not None, f"Workload for '{component}' missing"

    @pytest.mark.parametrize("component", ["frontend", "document-svc", "collab-svc", "nats", "postgres"])
    def test_component_release_exists(self, k8s_custom_api, component):
        """Every component has at least one ComponentRelease.
        THIS would have caught: document-svc and collab-svc had no releases."""
        releases = list_openchoreo_resources(k8s_custom_api, "componentreleases",
                                              label_selector=f"openchoreo.dev/component={component}")
        assert len(releases) > 0, (
            f"Component '{component}' has NO ComponentRelease — "
            f"build was never triggered or failed. "
            f"Check WorkflowRuns and gitops repo releases/ directory."
        )

    @pytest.mark.parametrize("component,env", [
        ("frontend", "development"),
        ("document-svc", "development"),
        ("collab-svc", "development"),
        ("nats", "development"),
        ("postgres", "development"),
    ])
    def test_release_binding_exists_and_ready(self, k8s_custom_api, component, env):
        """Every component has a ReleaseBinding for its environment, and it's Ready.
        THIS would have caught: frontend ReleaseBinding stuck at ConnectionsPending."""
        rb_name = f"{component}-{env}"
        rb = get_openchoreo_resource(k8s_custom_api, "releasebindings", rb_name)
        assert rb is not None, f"ReleaseBinding '{rb_name}' missing — component never deployed to {env}"

        # Check Ready condition
        conditions = rb.get("status", {}).get("conditions", [])
        ready = next((c for c in conditions if c["type"] == "Ready"), None)
        assert ready is not None, f"ReleaseBinding '{rb_name}' has no Ready condition"
        assert ready["status"] == "True", (
            f"ReleaseBinding '{rb_name}' not Ready: {ready.get('reason', 'unknown')} — "
            f"{ready.get('message', 'no message')}"
        )

    @pytest.mark.parametrize("component,env", [
        ("frontend", "development"),
        ("document-svc", "development"),
        ("collab-svc", "development"),
    ])
    def test_release_binding_connections_resolved(self, k8s_custom_api, component, env):
        """ReleaseBindings with dependencies have ALL connections resolved.
        THIS is the exact check that would have caught the CrashLoop root cause."""
        rb_name = f"{component}-{env}"
        rb = get_openchoreo_resource(k8s_custom_api, "releasebindings", rb_name)
        assert rb is not None

        conditions = rb.get("status", {}).get("conditions", [])
        conn_resolved = next((c for c in conditions if c["type"] == "ConnectionsResolved"), None)

        if conn_resolved is not None:
            assert conn_resolved["status"] == "True", (
                f"ReleaseBinding '{rb_name}' has UNRESOLVED connections: "
                f"{conn_resolved.get('message', '')}. "
                f"Check that dependency components have been built and deployed."
            )

    @pytest.mark.parametrize("component,env", [
        ("frontend", "development"),
        ("document-svc", "development"),
        ("collab-svc", "development"),
    ])
    def test_rendered_release_not_degraded(self, k8s_custom_api, component, env):
        """RenderedRelease is not in Degraded state."""
        rr_name = f"{component}-{env}"
        rr = get_openchoreo_resource(k8s_custom_api, "renderedreleases", rr_name)
        if rr is not None:
            conditions = rr.get("status", {}).get("conditions", [])
            degraded = next((c for c in conditions if c["type"] == "Degraded"), None)
            if degraded is not None:
                assert degraded["status"] != "True", (
                    f"RenderedRelease '{rr_name}' is DEGRADED: {degraded.get('message', '')}"
                )
```

### Layer 2: Dependency Resolution Verification
**Purpose**: Verify that components with declared dependencies actually receive their env vars

**File**: `tests/e2e/test_dependency_resolution.py`

```python
@pytest.mark.e2e
@pytest.mark.dependencies
class TestDependencyResolution:
    """Verify cross-component dependencies are resolved and env vars injected."""

    EXPECTED_DEPENDENCIES = {
        "frontend": {
            "DOC_SERVICE_URL": "document-svc",
            "COLLAB_SERVICE_URL": "collab-svc",
        },
        # Add more as components grow
    }

    DATA_PLANE_NS = "dp-default-doclet-development-*"  # glob pattern

    def test_frontend_has_doc_service_url(self, k8s_core_api, k8s_apps_api):
        """Frontend Deployment has DOC_SERVICE_URL env var injected.
        THIS would have caught: env: [] in the Deployment spec."""
        ns = self._find_data_plane_namespace(k8s_core_api)
        deployment = self._find_deployment(k8s_apps_api, ns, "frontend-development")
        env_vars = self._extract_env_vars(deployment)

        assert "DOC_SERVICE_URL" in env_vars, (
            f"Frontend deployment missing DOC_SERVICE_URL. "
            f"Current env vars: {list(env_vars.keys())}. "
            f"This means document-svc ReleaseBinding doesn't exist or connections are pending."
        )
        assert "document-svc" in env_vars["DOC_SERVICE_URL"], (
            f"DOC_SERVICE_URL doesn't point to document-svc: {env_vars['DOC_SERVICE_URL']}"
        )

    def test_frontend_has_collab_service_url(self, k8s_core_api, k8s_apps_api):
        """Frontend Deployment has COLLAB_SERVICE_URL env var injected."""
        ns = self._find_data_plane_namespace(k8s_core_api)
        deployment = self._find_deployment(k8s_apps_api, ns, "frontend-development")
        env_vars = self._extract_env_vars(deployment)

        assert "COLLAB_SERVICE_URL" in env_vars, (
            f"Frontend deployment missing COLLAB_SERVICE_URL. "
            f"This means collab-svc ReleaseBinding doesn't exist or connections are pending."
        )

    def test_all_declared_dependencies_resolved(self, k8s_core_api, k8s_apps_api):
        """Comprehensive: every component's declared dependencies are present as env vars."""
        ns = self._find_data_plane_namespace(k8s_core_api)

        for component, deps in self.EXPECTED_DEPENDENCIES.items():
            deployment = self._find_deployment(k8s_apps_api, ns, f"{component}-development")
            env_vars = self._extract_env_vars(deployment)

            for env_name, expected_svc in deps.items():
                assert env_name in env_vars, (
                    f"{component}: missing {env_name} (depends on {expected_svc})"
                )

    def _find_data_plane_namespace(self, k8s_core_api):
        """Find the data plane namespace for the doclet project."""
        namespaces = k8s_core_api.list_namespace()
        for ns in namespaces.items:
            if ns.metadata.name.startswith("dp-default-doclet-development"):
                return ns.metadata.name
        pytest.fail("Data plane namespace for doclet/development not found")

    def _find_deployment(self, k8s_apps_api, namespace, name_prefix):
        """Find deployment by name prefix."""
        deployments = k8s_apps_api.list_namespaced_deployment(namespace)
        for d in deployments.items:
            if d.metadata.name.startswith(name_prefix):
                return d
        pytest.fail(f"Deployment starting with '{name_prefix}' not found in {namespace}")

    def _extract_env_vars(self, deployment):
        """Extract env vars from first container in deployment."""
        containers = deployment.spec.template.spec.containers
        if not containers:
            return {}
        env_list = containers[0].env or []
        return {e.name: (e.value or "") for e in env_list}
```

### Layer 3: CI/CD Pipeline (WorkflowRun) Health
**Purpose**: Detect failed or never-triggered builds before they cause downstream issues

**File**: `tests/e2e/test_workflow_pipeline.py`

```python
@pytest.mark.e2e
@pytest.mark.workflow
class TestWorkflowPipelineHealth:
    """Verify CI/CD pipelines have run successfully for all components."""

    BUILDABLE_COMPONENTS = ["frontend", "document-svc", "collab-svc"]

    def test_workflow_template_exists(self, k8s_custom_api):
        """The docker-gitops-release Workflow template exists."""
        workflow = get_openchoreo_resource(
            k8s_custom_api, "workflows", "docker-gitops-release",
            group="openchoreo.dev", version="v1alpha1"
        )
        assert workflow is not None, "docker-gitops-release Workflow missing"

    @pytest.mark.parametrize("component", BUILDABLE_COMPONENTS)
    def test_at_least_one_successful_workflow_run(self, k8s_custom_api, component):
        """Every buildable component has at least one completed WorkflowRun.
        THIS would have caught: document-svc and collab-svc never had builds triggered."""
        runs = list_openchoreo_resources(
            k8s_custom_api, "workflowruns",
            label_selector=f"openchoreo.dev/component={component}",
            group="openchoreo.dev", version="v1alpha1"
        )
        assert len(runs) > 0, (
            f"Component '{component}' has ZERO WorkflowRuns — "
            f"no build was ever triggered. Run the build manually."
        )

        # Check at least one succeeded
        succeeded = [r for r in runs
                     if r.get("status", {}).get("phase") == "Succeeded"]
        assert len(succeeded) > 0, (
            f"Component '{component}' has {len(runs)} WorkflowRun(s) but "
            f"NONE succeeded. Phases: {[r.get('status', {}).get('phase', 'unknown') for r in runs]}. "
            f"Check Argo Workflow logs."
        )

    @pytest.mark.parametrize("component", BUILDABLE_COMPONENTS)
    def test_no_stuck_workflow_runs(self, k8s_custom_api, component):
        """No WorkflowRuns stuck in Running state for > 30 minutes."""
        runs = list_openchoreo_resources(
            k8s_custom_api, "workflowruns",
            label_selector=f"openchoreo.dev/component={component}",
            group="openchoreo.dev", version="v1alpha1"
        )
        for run in runs:
            phase = run.get("status", {}).get("phase", "")
            if phase == "Running":
                start = run.get("status", {}).get("startedAt")
                if start:
                    age_minutes = _age_in_minutes(start)
                    assert age_minutes < 30, (
                        f"WorkflowRun '{run['metadata']['name']}' for {component} "
                        f"has been Running for {age_minutes:.0f} minutes — likely stuck"
                    )

    def test_no_failed_workflow_runs_in_last_hour(self, k8s_custom_api):
        """Alert on any WorkflowRun that failed in the last hour."""
        all_runs = list_openchoreo_resources(
            k8s_custom_api, "workflowruns",
            group="openchoreo.dev", version="v1alpha1"
        )
        recent_failures = []
        for run in all_runs:
            phase = run.get("status", {}).get("phase", "")
            if phase == "Failed":
                finished = run.get("status", {}).get("finishedAt")
                if finished and _age_in_minutes(finished) < 60:
                    recent_failures.append(run["metadata"]["name"])

        assert len(recent_failures) == 0, (
            f"WorkflowRuns failed in last hour: {recent_failures}. "
            f"Check `kubectl get workflowruns` and Argo Workflow logs."
        )
```

### Layer 4: GitOps Repo ↔ Cluster Consistency
**Purpose**: Verify the gitops repo has the expected structure and matches cluster state

**File**: `tests/e2e/test_gitops_consistency.py`

```python
@pytest.mark.e2e
@pytest.mark.gitops_consistency
class TestGitOpsConsistency:
    """Verify gitops repo state matches what's expected in the cluster."""

    GITOPS_REPO = "yehia2amer/openchoreo-gitops"
    COMPONENTS_WITH_RELEASES = ["frontend", "document-svc", "collab-svc", "nats", "postgres"]

    def test_flux_gitrepository_synced(self, k8s_custom_api):
        """Flux GitRepository is synced and not stale."""
        gr = get_custom_resource(
            k8s_custom_api,
            group="source.toolkit.fluxcd.io",
            version="v1",
            plural="gitrepositories",
            name="sample-gitops",
            namespace="flux-system",
        )
        assert gr is not None, "GitRepository 'sample-gitops' not found"
        conditions = gr.get("status", {}).get("conditions", [])
        ready = next((c for c in conditions if c["type"] == "Ready"), None)
        assert ready and ready["status"] == "True", (
            f"GitRepository not Ready: {ready.get('message', 'unknown') if ready else 'no condition'}"
        )

    def test_all_kustomizations_ready(self, k8s_custom_api):
        """All Flux Kustomizations are Ready (no stuck reconciliation)."""
        kustomizations = k8s_custom_api.list_namespaced_custom_object(
            group="kustomize.toolkit.fluxcd.io",
            version="v1",
            namespace="flux-system",
            plural="kustomizations",
        )
        for ks in kustomizations.get("items", []):
            name = ks["metadata"]["name"]
            conditions = ks.get("status", {}).get("conditions", [])
            ready = next((c for c in conditions if c["type"] == "Ready"), None)
            assert ready and ready["status"] == "True", (
                f"Kustomization '{name}' not Ready: "
                f"{ready.get('message', 'unknown') if ready else 'no condition'}. "
                f"This means Flux can't sync changes from the gitops repo."
            )

    def test_no_kustomization_has_errors(self, k8s_custom_api):
        """No Flux Kustomization is in a failed/error state."""
        kustomizations = k8s_custom_api.list_namespaced_custom_object(
            group="kustomize.toolkit.fluxcd.io",
            version="v1",
            namespace="flux-system",
            plural="kustomizations",
        )
        errors = []
        for ks in kustomizations.get("items", []):
            name = ks["metadata"]["name"]
            conditions = ks.get("status", {}).get("conditions", [])
            for c in conditions:
                if c.get("type") == "Ready" and c.get("status") == "False":
                    errors.append(f"{name}: {c.get('message', 'unknown')}")
        assert len(errors) == 0, f"Kustomizations with errors: {errors}"

    @pytest.mark.parametrize("component", COMPONENTS_WITH_RELEASES)
    def test_component_has_release_in_cluster(self, k8s_custom_api, component):
        """Every expected component has a ComponentRelease synced to the cluster.
        THIS would have caught: document-svc/collab-svc had no releases/ in gitops repo."""
        releases = list_openchoreo_resources(
            k8s_custom_api, "componentreleases",
            label_selector=f"openchoreo.dev/component={component}"
        )
        assert len(releases) > 0, (
            f"Component '{component}' has no ComponentRelease in cluster. "
            f"Either the gitops repo is missing releases/{component}-*.yaml "
            f"or Flux hasn't synced it yet."
        )
```

### Layer 5: Application Pod Health (Beyond "Deployment Exists")
**Purpose**: Verify that pods are actually Running and not CrashLooping

**File**: `tests/e2e/test_application_health.py`

```python
@pytest.mark.e2e
@pytest.mark.app_health
class TestApplicationHealth:
    """Verify deployed application pods are healthy — not just that Deployments exist."""

    EXPECTED_PODS = {
        # component-prefix: minimum-ready-count
        "frontend-development": 1,
        "document-svc-development": 1,
        "collab-svc-development": 1,
        "nats-development": 1,
        "postgres-development": 1,
    }

    def test_data_plane_namespace_exists(self, k8s_core_api):
        """Data plane namespace for doclet project exists."""
        ns = self._find_dp_namespace(k8s_core_api)
        assert ns is not None, (
            "No namespace matching dp-default-doclet-development-* found. "
            "The project may not have been deployed yet."
        )

    @pytest.mark.parametrize("pod_prefix,min_ready", list(EXPECTED_PODS.items()))
    def test_pod_is_running(self, k8s_core_api, pod_prefix, min_ready):
        """Each component has at least min_ready pods in Running phase.
        THIS would have caught: frontend pod in CrashLoopBackOff."""
        ns = self._find_dp_namespace(k8s_core_api)
        pods = k8s_core_api.list_namespaced_pod(ns)

        matching = [p for p in pods.items
                    if p.metadata.name.startswith(pod_prefix)
                    or any(pod_prefix in (o.name or "") for o in (p.metadata.owner_references or []))]

        # Broader match: find by label
        if not matching:
            matching = [p for p in pods.items
                        if pod_prefix.replace("-development", "") in p.metadata.name]

        running = [p for p in matching if p.status.phase == "Running"]
        assert len(running) >= min_ready, (
            f"Expected >= {min_ready} Running pods for '{pod_prefix}', "
            f"found {len(running)} Running out of {len(matching)} total. "
            f"Pod statuses: {[(p.metadata.name, p.status.phase) for p in matching]}"
        )

    @pytest.mark.parametrize("pod_prefix", list(EXPECTED_PODS.keys()))
    def test_no_crashloop(self, k8s_core_api, pod_prefix):
        """No pods are in CrashLoopBackOff.
        THIS is the exact symptom check for the incident."""
        ns = self._find_dp_namespace(k8s_core_api)
        pods = k8s_core_api.list_namespaced_pod(ns)

        for pod in pods.items:
            if pod_prefix.replace("-development", "") not in pod.metadata.name:
                continue
            for cs in (pod.status.container_statuses or []):
                waiting = cs.state.waiting if cs.state else None
                if waiting and waiting.reason == "CrashLoopBackOff":
                    pytest.fail(
                        f"Pod '{pod.metadata.name}' is in CrashLoopBackOff! "
                        f"Restart count: {cs.restart_count}. "
                        f"Check: kubectl logs -n {ns} {pod.metadata.name}"
                    )

    @pytest.mark.parametrize("pod_prefix", list(EXPECTED_PODS.keys()))
    def test_low_restart_count(self, k8s_core_api, pod_prefix):
        """Pods haven't restarted excessively (threshold: 5)."""
        ns = self._find_dp_namespace(k8s_core_api)
        pods = k8s_core_api.list_namespaced_pod(ns)

        for pod in pods.items:
            if pod_prefix.replace("-development", "") not in pod.metadata.name:
                continue
            for cs in (pod.status.container_statuses or []):
                assert cs.restart_count < 5, (
                    f"Pod '{pod.metadata.name}' container '{cs.name}' "
                    f"has {cs.restart_count} restarts — something is wrong. "
                    f"Check logs and env vars."
                )

    @pytest.mark.parametrize("pod_prefix", list(EXPECTED_PODS.keys()))
    def test_all_containers_ready(self, k8s_core_api, pod_prefix):
        """All containers in matching pods report ready=True."""
        ns = self._find_dp_namespace(k8s_core_api)
        pods = k8s_core_api.list_namespaced_pod(ns)

        for pod in pods.items:
            if pod_prefix.replace("-development", "") not in pod.metadata.name:
                continue
            if pod.status.phase != "Running":
                continue
            for cs in (pod.status.container_statuses or []):
                assert cs.ready, (
                    f"Container '{cs.name}' in pod '{pod.metadata.name}' not ready"
                )

    def _find_dp_namespace(self, k8s_core_api):
        namespaces = k8s_core_api.list_namespace()
        for ns in namespaces.items:
            if ns.metadata.name.startswith("dp-default-doclet-development"):
                return ns.metadata.name
        return None
```

### Layer 6: End-to-End User Journeys
**Purpose**: Test what the user actually experiences — can they use the deployed app?

**File**: `tests/e2e/test_user_journeys.py`

```python
@pytest.mark.e2e
@pytest.mark.user_journey
class TestDocletAppUserJourney:
    """End-to-end user journey tests for the Doclet demo application."""

    def test_frontend_serves_html(self, k8s_core_api, http_session):
        """Frontend pod serves HTML (not an error page).
        Tests: nginx is running, React app is built, static assets are served."""
        ns = self._find_dp_namespace(k8s_core_api)
        # Port-forward to frontend pod
        with PortForward(k8s_core_api, ns, self._find_pod(k8s_core_api, ns, "frontend"), 80) as port:
            response = http_session.get(f"http://localhost:{port}/", timeout=10)
            assert response.status_code == 200, f"Frontend returned {response.status_code}"
            assert "<!doctype html>" in response.text.lower() or "<html" in response.text.lower(), (
                "Frontend didn't return HTML — nginx may be misconfigured"
            )

    def test_frontend_can_reach_document_svc(self, k8s_core_api, http_session):
        """Document service is reachable at the URL injected into frontend."""
        ns = self._find_dp_namespace(k8s_core_api)
        with PortForward(k8s_core_api, ns,
                         self._find_pod(k8s_core_api, ns, "document-svc"), 8080) as port:
            response = http_session.get(f"http://localhost:{port}/health", timeout=10)
            # Accept 200 or 404 (endpoint may not have /health, but TCP connection works)
            assert response.status_code < 500, (
                f"document-svc returned {response.status_code} — service is broken"
            )

    def test_frontend_can_reach_collab_svc(self, k8s_core_api, http_session):
        """Collab service is reachable at the URL injected into frontend."""
        ns = self._find_dp_namespace(k8s_core_api)
        with PortForward(k8s_core_api, ns,
                         self._find_pod(k8s_core_api, ns, "collab-svc"), 8090) as port:
            response = http_session.get(f"http://localhost:{port}/health", timeout=10)
            assert response.status_code < 500, (
                f"collab-svc returned {response.status_code} — service is broken"
            )

    def test_nats_is_accepting_connections(self, k8s_core_api):
        """NATS server accepts TCP connections."""
        ns = self._find_dp_namespace(k8s_core_api)
        with PortForward(k8s_core_api, ns,
                         self._find_pod(k8s_core_api, ns, "nats"), 4222) as port:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            assert result == 0, "NATS is not accepting TCP connections"

    def test_postgres_is_accepting_connections(self, k8s_core_api):
        """PostgreSQL accepts TCP connections."""
        ns = self._find_dp_namespace(k8s_core_api)
        with PortForward(k8s_core_api, ns,
                         self._find_pod(k8s_core_api, ns, "postgres"), 5432) as port:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            assert result == 0, "PostgreSQL is not accepting TCP connections"

    def _find_dp_namespace(self, k8s_core_api):
        for ns in k8s_core_api.list_namespace().items:
            if ns.metadata.name.startswith("dp-default-doclet-development"):
                return ns.metadata.name
        pytest.fail("Data plane namespace not found")

    def _find_pod(self, k8s_core_api, namespace, name_fragment):
        pods = k8s_core_api.list_namespaced_pod(namespace)
        for pod in pods.items:
            if name_fragment in pod.metadata.name and pod.status.phase == "Running":
                return pod.metadata.name
        pytest.fail(f"No running pod matching '{name_fragment}' in {namespace}")
```

---

## 4. Shared E2E Helpers

**File**: `tests/utils/openchoreo_helpers.py`

```python
"""OpenChoreo CRD helper functions for E2E tests."""

from kubernetes import client
from kubernetes.client.rest import ApiException


OPENCHOREO_GROUP = "core.openchoreo.dev"
OPENCHOREO_VERSION = "v1alpha1"


def get_openchoreo_resource(
    custom_api: client.CustomObjectsApi,
    plural: str,
    name: str,
    namespace: str = "default",
    group: str = OPENCHOREO_GROUP,
    version: str = OPENCHOREO_VERSION,
):
    """Get a single OpenChoreo custom resource."""
    try:
        return custom_api.get_namespaced_custom_object(
            group=group, version=version, namespace=namespace,
            plural=plural, name=name,
        )
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def list_openchoreo_resources(
    custom_api: client.CustomObjectsApi,
    plural: str,
    namespace: str = "default",
    label_selector: str = "",
    group: str = OPENCHOREO_GROUP,
    version: str = OPENCHOREO_VERSION,
):
    """List OpenChoreo custom resources with optional label filter."""
    result = custom_api.list_namespaced_custom_object(
        group=group, version=version, namespace=namespace,
        plural=plural, label_selector=label_selector,
    )
    return result.get("items", [])
```

---

## 5. E2E Fixtures

**File**: `tests/e2e/conftest.py`

```python
"""E2E test fixtures — extends base conftest with OpenChoreo-specific setup."""

import pytest


@pytest.fixture(scope="session")
def demo_app_config():
    """Configuration for the Doclet demo application."""
    return {
        "project": "doclet",
        "environment": "development",
        "components": {
            "frontend": {"port": 80, "has_dependencies": True},
            "document-svc": {"port": 8080, "has_dependencies": False},
            "collab-svc": {"port": 8090, "has_dependencies": False},
            "nats": {"port": 4222, "has_dependencies": False},
            "postgres": {"port": 5432, "has_dependencies": False},
        },
        "dependency_map": {
            "frontend": {
                "DOC_SERVICE_URL": "document-svc",
                "COLLAB_SERVICE_URL": "collab-svc",
            },
        },
    }


@pytest.fixture(scope="session")
def dp_namespace(k8s_core_api):
    """Discover the data plane namespace for doclet/development."""
    for ns in k8s_core_api.list_namespace().items:
        if ns.metadata.name.startswith("dp-default-doclet-development"):
            return ns.metadata.name
    pytest.skip("Data plane namespace not found — demo app may not be deployed")
```

---

## 6. Pytest Markers

**File**: `tests/pytest.ini` (or add to `pyproject.toml`)

```ini
[pytest]
markers =
    smoke: Quick health checks (existing)
    e2e: End-to-end tests against real environment
    resource_chain: OpenChoreo resource chain validation
    dependencies: Cross-component dependency resolution
    workflow: CI/CD pipeline health
    gitops_consistency: GitOps repo ↔ cluster sync
    app_health: Application pod-level health
    user_journey: End-to-end user scenarios
```

---

## 7. Execution Strategy

### Run E2E Tests After Pulumi Deploy
```bash
# After `pulumi up` and demo app bootstrap
pytest tests/e2e/ -v --tb=long --html=e2e-report.html

# Quick check: just resource chain + app health (< 30 seconds)
pytest tests/e2e/ -m "resource_chain or app_health" -v

# Full suite with smoke tests
pytest tests/ -v --html=full-report.html
```

### CI Integration (Future)
```yaml
# In a GitHub Action or similar
- name: Run E2E Tests
  run: |
    export KUBECONFIG=$HOME/.kube/config
    export KUBE_CONTEXT=admin@openchoreo
    pytest tests/e2e/ -v --tb=long --junitxml=e2e-results.xml
  timeout-minutes: 10
```

### Periodic Health Check (Cron)
```bash
# Run every 15 minutes to catch drift
*/15 * * * * cd /path/to/project && pytest tests/e2e/ -m "resource_chain or app_health" --tb=line -q >> /var/log/openchoreo-health.log 2>&1
```

---

## 8. What Each Layer Would Have Caught in the Incident

| Layer | Test | Would Have Detected |
|-------|------|-------------------|
| 1 - Resource Chain | `test_component_release_exists("document-svc")` | ❌ No ComponentRelease for document-svc |
| 1 - Resource Chain | `test_release_binding_connections_resolved("frontend")` | ❌ "2 connections pending, 0 resolved" |
| 2 - Dependencies | `test_frontend_has_doc_service_url` | ❌ `env: []` — DOC_SERVICE_URL missing |
| 3 - Workflow | `test_at_least_one_successful_workflow_run("document-svc")` | ❌ Zero WorkflowRuns for document-svc |
| 3 - Workflow | `test_at_least_one_successful_workflow_run("collab-svc")` | ❌ Zero WorkflowRuns for collab-svc |
| 4 - GitOps | `test_component_has_release_in_cluster("document-svc")` | ❌ No releases/ directory in gitops repo |
| 5 - App Health | `test_no_crashloop("frontend")` | ❌ CrashLoopBackOff with 68+ restarts |
| 5 - App Health | `test_low_restart_count("frontend")` | ❌ 68 restarts > threshold of 5 |
| 6 - User Journey | `test_frontend_serves_html` | ❌ Pod not running, can't serve anything |

**Every single layer would have caught the problem from a different angle.** The defense-in-depth approach means even if one test is flaky, another layer catches it.

---

## 9. Implementation Priority

| Phase | What | Effort | Value |
|-------|------|--------|-------|
| **Phase 1** | Layer 5: App Health (CrashLoop + restart count) | 1-2 hours | 🔴 Highest — catches the exact symptom |
| **Phase 2** | Layer 1: Resource Chain (ReleaseBinding + connections) | 2-3 hours | 🔴 Highest — catches the root cause |
| **Phase 3** | Layer 2: Dependency Resolution (env var injection) | 1-2 hours | 🟠 High — catches the mechanism |
| **Phase 4** | Layer 3: Workflow Pipeline health | 2-3 hours | 🟠 High — catches builds never triggered |
| **Phase 5** | Layer 4: GitOps Consistency | 1-2 hours | 🟡 Medium — catches repo drift |
| **Phase 6** | Layer 6: User Journeys | 2-3 hours | 🟡 Medium — catches user-facing breakage |

**Total estimated effort: ~10-15 hours for all 6 layers.**

---

## 10. Dependencies to Add

```toml
# In pyproject.toml [project.optional-dependencies] or [tool.uv.dev-dependencies]
e2e = [
    "pytest>=8.0.0",
    "pytest-html>=4.1.0",
    "pytest-timeout>=2.3.0",
    "kubernetes>=29.0.0",
    "requests>=2.31.0",
]
```

No new heavy dependencies — all tests use the Kubernetes Python client and requests, which are already in the project.
