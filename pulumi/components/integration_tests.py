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

from typing import Any

import pulumi

from config import (
    CLUSTER_SECRET_STORE_NAME,
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
    TEST_CR_CONDITION,
    TEST_CRD,
    TEST_DAEMONSET,
    TEST_DEPLOY_LABEL,
    TEST_DEPLOYMENT,
    TEST_HTTPROUTE_STATUS,
    TEST_SECRET_EXISTS,
    TEST_SERVICE_HTTP,
    TEST_STATEFULSET,
    IntegrationTest,
)


class IntegrationTests(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:IntegrationTests", name, {}, opts)

        tests: list[pulumi.Resource] = []
        base_opts = self._child_opts(depends_on=depends)

        def _test(**kwargs: Any) -> IntegrationTest:
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

        if cfg.platform.gateway_mode == "cilium":
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

            _test(
                test_name="e2e-backstage-fork-externalsecret-synced",
                test_type=TEST_CR_CONDITION,
                cr_group="external-secrets.io",
                cr_version="v1",
                cr_plural="externalsecrets",
                resource_name="backstage-fork-secrets",
                namespace="backstage-fork",
                condition_type="Ready",
            )

            _test(
                test_name="e2e-backstage-fork-secret-exists",
                test_type=TEST_SECRET_EXISTS,
                namespace="backstage-fork",
                resource_name="backstage-fork-secrets",
                expected_keys=[
                    "backend-secret",
                    "client-id",
                    "client-secret",
                    "auth-authorization-url",
                    "jenkins-api-key",
                ],
            )

        # ─── Observability (optional) ─────────────────────────────

        if cfg.enable_observability:
            _test(
                test_name="crd-clusterobservabilityplanes",
                test_type=TEST_CRD,
                crd_name="clusterobservabilityplanes.openchoreo.dev",
            )

        # ═══════════════════════════════════════════════════════════
        # E2E Validation Tests
        # ═══════════════════════════════════════════════════════════

        # ─── PushSecret Sync E2E ──────────────────────────────────
        # Verify PushSecret resources have synced secrets to OpenBao.
        # PushSecrets are created in the openbao namespace and push
        # K8s Secret data → OpenBao via the ClusterSecretStore.

        _pushsecret_names: list[str] = []
        if cfg.github_pat:
            _pushsecret_names.append("git-secrets")
        if cfg.enable_flux or cfg.gitops_repo_url:
            _pushsecret_names.append("backstage-fork-secrets")
        if cfg.enable_openobserve and cfg.openobserve_admin_password:
            _pushsecret_names.append("openobserve-creds")
        _is_dev = pulumi.get_stack() in (
            "dev",
            "rancher-desktop",
            "local",
            "test",
            "talos",
            "talos-baremetal",
        )
        if _is_dev:
            _pushsecret_names.append("dev-secrets")

        for ps_name in _pushsecret_names:
            _test(
                test_name=f"e2e-pushsecret-{ps_name}",
                test_type=TEST_CR_CONDITION,
                cr_group="external-secrets.io",
                cr_version="v1alpha1",
                cr_plural="pushsecrets",
                resource_name=ps_name,
                namespace=NS_OPENBAO,
                condition_type="Ready",
            )

        # Also verify K8s source secrets exist
        if cfg.github_pat:
            _test(
                test_name="e2e-push-git-secrets-exist",
                test_type=TEST_SECRET_EXISTS,
                namespace=NS_OPENBAO,
                resource_name="push-git-secrets",
                expected_keys=["git-token", "gitops-token"],
            )

        # ─── ClusterSecretStore E2E ───────────────────────────────
        # Verify the ClusterSecretStore is Ready — ESO can talk to OpenBao.

        _test(
            test_name="e2e-clustersecretstore-ready",
            test_type=TEST_CR_CONDITION,
            cr_group="external-secrets.io",
            cr_version="v1",
            cr_plural="clustersecretstores",
            resource_name=CLUSTER_SECRET_STORE_NAME,
            condition_type="Ready",
        )

        # ─── Backstage Secret Bridge E2E ──────────────────────────
        # Verify the Backstage ExternalSecret has synced and created
        # the actual Kubernetes secret with expected keys.

        _test(
            test_name="e2e-backstage-externalsecret-synced",
            test_type=TEST_CR_CONDITION,
            cr_group="external-secrets.io",
            cr_version="v1",
            cr_plural="externalsecrets",
            resource_name="backstage-secrets",
            namespace=NS_CONTROL_PLANE,
            condition_type="Ready",
        )

        _test(
            test_name="e2e-backstage-secret-exists",
            test_type=TEST_SECRET_EXISTS,
            namespace=NS_CONTROL_PLANE,
            resource_name="backstage-secrets",
            expected_keys=["backend-secret", "client-secret"],
        )

        # ─── Plane Registration E2E ───────────────────────────────
        # Verify that all registered planes exist as cluster CRDs.

        _test(
            test_name="e2e-clusterdataplane-exists",
            test_type=TEST_CR_CONDITION,
            cr_group="openchoreo.dev",
            cr_version="v1alpha1",
            cr_plural="clusterdataplanes",
            resource_name="default",
            condition_type="Created",
        )

        _test(
            test_name="e2e-clusterworkflowplane-exists",
            test_type=TEST_CR_CONDITION,
            cr_group="openchoreo.dev",
            cr_version="v1alpha1",
            cr_plural="clusterworkflowplanes",
            resource_name="default",
            condition_type="Created",
        )

        if cfg.enable_observability:
            _test(
                test_name="e2e-clusterobservabilityplane-exists",
                test_type=TEST_CR_CONDITION,
                cr_group="openchoreo.dev",
                cr_version="v1alpha1",
                cr_plural="clusterobservabilityplanes",
                resource_name="default",
                condition_type="Created",
            )

        # ─── Gateway E2E ──────────────────────────────────────────
        # Verify the shared Gateway resource is programmed.

        _test(
            test_name="e2e-shared-gateway-programmed",
            test_type=TEST_CR_CONDITION,
            cr_group="gateway.networking.k8s.io",
            cr_version="v1",
            cr_plural="gateways",
            resource_name="gateway-shared",
            namespace="openchoreo-gateway",
            condition_type="Programmed",
        )

        # ─── Flux Kustomization E2E (optional) ────────────────────

        if cfg.enable_flux and cfg.gitops_repo_url:
            for kust in ("oc-namespaces", "oc-platform-shared", "oc-platform", "oc-demo-projects"):
                _test(
                    test_name=f"e2e-flux-kustomization-{kust}",
                    test_type=TEST_CR_CONDITION,
                    cr_group="kustomize.toolkit.fluxcd.io",
                    cr_version="v1",
                    cr_plural="kustomizations",
                    resource_name=kust,
                    namespace=NS_FLUX_SYSTEM,
                    condition_type="Ready",
                )

        # ─── Observability Secrets E2E (optional) ─────────────────

        if cfg.enable_observability:
            for es_name in ("observer-secret",):
                _test(
                    test_name=f"e2e-obs-externalsecret-{es_name}",
                    test_type=TEST_CR_CONDITION,
                    cr_group="external-secrets.io",
                    cr_version="v1",
                    cr_plural="externalsecrets",
                    resource_name=es_name,
                    namespace="openchoreo-observability-plane",
                    condition_type="Ready",
                )

        # ─── Summary export ───────────────────────────────────────

        test_names = [t._name for t in tests]
        pulumi.export("integration_tests", test_names)
        pulumi.export("integration_test_count", len(test_names))

        self.result = tests
        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs = {
            "parent": self,
            "aliases": [pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)],
        }
        if depends_on:
            opts_kwargs["depends_on"] = depends_on
        return pulumi.ResourceOptions(**opts_kwargs)


def deploy(
    cfg: OpenChoreoConfig,
    depends: list[pulumi.Resource],
) -> list[pulumi.Resource]:
    """Create integration-test resources.  Returns the list of test resources."""
    return IntegrationTests(
        "integration-tests",
        cfg=cfg,
        depends=depends,
    ).result
