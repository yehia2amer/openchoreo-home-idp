"""Integration tests that run as the final step of ``pulumi up``.

Each test is a Pulumi dynamic resource that performs a live health check against
the deployed cluster.  Tests always re-run (diff returns *changes=True*) so
every ``pulumi up`` validates the current cluster state.

Gateway API validation uses two complementary approaches:
- **HTTPRoute status checks** — verify that HTTPRoutes are ``Accepted`` and
  ``ResolvedRefs`` by the gateway controller (config validation).
- **Service HTTP checks** — port-forward to backend services and verify they
  respond to HTTP requests (health validation).

Tests are grouped by plane and only created when the corresponding feature flag
is enabled (e.g. Cilium tests only run when ``enable_cilium=True``).
"""

from __future__ import annotations

import pulumi

from config import (
    NS_CERT_MANAGER,
    NS_CONTROL_PLANE,
    NS_DATA_PLANE,
    NS_EXTERNAL_SECRETS,
    NS_FLUX_SYSTEM,
    NS_OPENBAO,
    NS_THUNDER,
    NS_WORKFLOW_PLANE,
    OpenChoreoConfig,
)
from helpers.dynamic_providers import (
    TEST_CRD,
    TEST_DAEMONSET,
    TEST_DEPLOY_LABEL,
    TEST_DEPLOYMENT,
    TEST_HTTPROUTE_STATUS,
    TEST_SERVICE_HTTP,
    TEST_STATEFULSET,
    IntegrationTest,
)


def deploy(
    cfg: OpenChoreoConfig,
    depends: list[pulumi.Resource],
) -> list[pulumi.Resource]:
    """Create integration-test resources.  Returns the list of test resources."""

    tests: list[pulumi.Resource] = []
    base_opts = pulumi.ResourceOptions(depends_on=depends)

    def _test(**kwargs: object) -> IntegrationTest:
        t = IntegrationTest(
            f"itest-{kwargs['test_name']}",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            opts=base_opts,
            **kwargs,
        )
        tests.append(t)
        return t

    # ─── Prerequisites ────────────────────────────────────────

    # cert-manager (deployment names include Helm-generated suffix, use label selector)
    _test(
        test_name="cert-manager-deployments",
        test_type=TEST_DEPLOY_LABEL,
        namespace=NS_CERT_MANAGER,
        label_selector="app.kubernetes.io/name=cert-manager",
    )

    # External Secrets Operator
    _test(
        test_name="external-secrets-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_EXTERNAL_SECRETS,
        resource_name="external-secrets",
    )

    # OpenBao vault — StatefulSet readiness
    _test(
        test_name="openbao-statefulset",
        test_type=TEST_STATEFULSET,
        namespace=NS_OPENBAO,
        resource_name="openbao",
    )

    # ─── Cilium (optional) ────────────────────────────────────

    if cfg.enable_cilium:
        _test(
            test_name="cilium-operator-deployment",
            test_type=TEST_DEPLOYMENT,
            namespace="kube-system",
            resource_name="cilium-operator",
        )
        _test(
            test_name="cilium-daemonset",
            test_type=TEST_DAEMONSET,
            namespace="kube-system",
            resource_name="cilium",
        )

    # ─── Thunder IdP ─────────────────────────────────────────

    _test(
        test_name="thunder-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_THUNDER,
        resource_name="thunder-deployment",
    )
    # Verify the Thunder HTTPRoute is accepted by the CP gateway
    _test(
        test_name="thunder-httproute-status",
        test_type=TEST_HTTPROUTE_STATUS,
        route_name="thunder-httproute",
        route_namespace=NS_THUNDER,
    )
    # Verify Thunder's JWKS endpoint responds via the service
    _test(
        test_name="thunder-jwks-http",
        test_type=TEST_SERVICE_HTTP,
        namespace=NS_THUNDER,
        service_name="thunder-service",
        service_port=8090,
        path="/oauth2/jwks",
        expected_statuses=[200],
        timeout=60,
    )

    # ─── Control Plane ────────────────────────────────────────

    # OpenChoreo API server — deployment + HTTPRoute + HTTP health
    _test(
        test_name="openchoreo-api-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_CONTROL_PLANE,
        resource_name="openchoreo-api",
    )
    _test(
        test_name="openchoreo-api-httproute-status",
        test_type=TEST_HTTPROUTE_STATUS,
        route_name="openchoreo-api",
        route_namespace=NS_CONTROL_PLANE,
    )
    _test(
        test_name="openchoreo-api-http",
        test_type=TEST_SERVICE_HTTP,
        namespace=NS_CONTROL_PLANE,
        service_name="openchoreo-api",
        service_port=8080,
        path="/",
        # API server may return 404 on root — that still proves the service is up
        expected_statuses=[200, 404],
        timeout=60,
    )

    # Backstage — deployment + HTTPRoute + HTTP health
    _test(
        test_name="backstage-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_CONTROL_PLANE,
        resource_name="backstage",
    )
    _test(
        test_name="backstage-httproute-status",
        test_type=TEST_HTTPROUTE_STATUS,
        route_name="backstage",
        route_namespace=NS_CONTROL_PLANE,
    )
    _test(
        test_name="backstage-http",
        test_type=TEST_SERVICE_HTTP,
        namespace=NS_CONTROL_PLANE,
        service_name="backstage",
        service_port=7007,
        path="/",
        expected_statuses=[200, 301, 302],
        timeout=60,
    )

    # Controller Manager + Cluster Gateway
    _test(
        test_name="controller-manager-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_CONTROL_PLANE,
        resource_name="controller-manager",
    )
    _test(
        test_name="cluster-gateway-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_CONTROL_PLANE,
        resource_name="cluster-gateway",
    )

    # Control Plane CRDs (representative set)
    for crd in (
        "components.openchoreo.dev",
        "projects.openchoreo.dev",
        "environments.openchoreo.dev",
    ):
        _test(
            test_name=f"crd-{crd.split('.')[0]}",
            test_type=TEST_CRD,
            crd_name=crd,
        )

    # ─── Data Plane ───────────────────────────────────────────

    _test(
        test_name="data-plane-agent-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_DATA_PLANE,
        resource_name="cluster-agent-dataplane",
    )
    _test(
        test_name="crd-clusterdataplanes",
        test_type=TEST_CRD,
        crd_name="clusterdataplanes.openchoreo.dev",
    )

    # ─── Workflow Plane ───────────────────────────────────────

    # Argo Workflows server
    _test(
        test_name="argo-server-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_WORKFLOW_PLANE,
        resource_name="argo-server",
    )

    # Workflow Plane agent
    _test(
        test_name="workflow-plane-agent-deployment",
        test_type=TEST_DEPLOYMENT,
        namespace=NS_WORKFLOW_PLANE,
        resource_name="cluster-agent-workflowplane",
    )

    # Workflow Plane CRD
    _test(
        test_name="crd-clusterworkflowplanes",
        test_type=TEST_CRD,
        crd_name="clusterworkflowplanes.openchoreo.dev",
    )

    # ─── Gateway API CRDs ─────────────────────────────────────

    _test(
        test_name="crd-gateways",
        test_type=TEST_CRD,
        crd_name="gateways.gateway.networking.k8s.io",
    )
    _test(
        test_name="crd-httproutes",
        test_type=TEST_CRD,
        crd_name="httproutes.gateway.networking.k8s.io",
    )

    # ─── Flux (optional) ──────────────────────────────────────

    if cfg.enable_flux and cfg.gitops_repo_url:
        for ctrl in ("source-controller", "kustomize-controller", "helm-controller"):
            _test(
                test_name=f"flux-{ctrl}",
                test_type=TEST_DEPLOYMENT,
                namespace=NS_FLUX_SYSTEM,
                resource_name=ctrl,
            )

    # ─── Observability (optional) ─────────────────────────────

    if cfg.enable_observability:
        _test(
            test_name="crd-clusterobservabilityplanes",
            test_type=TEST_CRD,
            crd_name="clusterobservabilityplanes.openchoreo.dev",
        )

    # ─── Summary export ───────────────────────────────────────

    test_names = [t._name for t in tests]
    pulumi.export("integration_tests", test_names)
    pulumi.export("integration_test_count", len(test_names))

    return tests
