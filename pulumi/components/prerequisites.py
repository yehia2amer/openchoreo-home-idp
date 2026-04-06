"""Prerequisites component: Gateway API CRDs, cert-manager, ESO, kgateway, OpenBao, ClusterSecretStore."""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes_cert_manager import CertManager

from config import (
    CLUSTER_SECRET_STORE_NAME,
    EXTERNAL_SECRETS_CHART_REPO,
    KGATEWAY_CHART_REPO,
    NS_CERT_MANAGER,
    NS_CONTROL_PLANE,
    NS_DATA_PLANE,
    NS_EXTERNAL_SECRETS,
    NS_OPENBAO,
    OPENBAO_CHART_REPO,
    SA_ESO_OPENBAO,
    SLEEP_AFTER_GATEWAY_API,
    SLEEP_AFTER_OPENBAO,
    THUNDER_INTERNAL_BASE,
    TIMEOUT_DEFAULT,
    TIMEOUT_TLS_WAIT,
    TIMEOUT_WAIT,
    OpenChoreoConfig,
)
from helpers.dynamic_providers import (
    OpenBaoSecrets,
    ValidateOpenBaoSecrets,
    WaitCustomResourceCondition,
    WaitPodReady,
)
from helpers.wait import sleep
from values.openbao import get_values as openbao_values


class PrerequisitesResult:
    """Outputs from the prerequisites component."""

    def __init__(
        self,
        openbao_ready: WaitPodReady,
        cluster_secret_store: k8s.apiextensions.CustomResource,
        cluster_secret_store_ready: WaitCustomResourceCondition,
        openbao_validated: ValidateOpenBaoSecrets,
        control_plane_ns: k8s.core.v1.Namespace,
        data_plane_ns: k8s.core.v1.Namespace,
    ):
        self.openbao_ready = openbao_ready
        self.cluster_secret_store = cluster_secret_store
        self.cluster_secret_store_ready = cluster_secret_store_ready
        self.openbao_validated = openbao_validated
        self.control_plane_ns = control_plane_ns
        self.data_plane_ns = data_plane_ns


class Prerequisites(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        extra_depends: list[pulumi.Resource] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:Prerequisites", name, {}, opts)

        base_depends = extra_depends or []
        p = cfg.platform  # Platform profile

        # ─── 1. Gateway API CRDs ───
        # When Cilium is the gateway controller, CRDs are installed in __main__.py
        # (before Cilium) so we only install them here for the kgateway path.
        if p.gateway_api_crds_pre_installed or p.gateway_mode == "cilium":
            # CRDs already installed; just wire up the dependency chain
            wait_gw = sleep("gateway-api", SLEEP_AFTER_GATEWAY_API, opts=self._child_opts(depends_on=base_depends))
        else:
            gateway_api_crds = k8s.yaml.v2.ConfigGroup(
                "gateway-api-crds",
                files=[cfg.gateway_api_crds_url],
                opts=self._child_opts(provider=k8s_provider, depends_on=base_depends),
            )
            wait_gw = sleep(
                "gateway-api", SLEEP_AFTER_GATEWAY_API, opts=self._child_opts(depends_on=[gateway_api_crds])
            )

        # ─── 2. cert-manager ───
        cert_manager_ns = k8s.core.v1.Namespace(
            NS_CERT_MANAGER,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=NS_CERT_MANAGER,
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=[wait_gw]),
        )

        cert_manager = CertManager(
            "cert-manager",
            install_crds=True,
            helm_options={
                "namespace": NS_CERT_MANAGER,
                "version": cfg.cert_manager_version,
                "timeout": TIMEOUT_DEFAULT,
            },
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[cert_manager_ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        # ─── 3. External Secrets Operator ───
        external_secrets_ns = k8s.core.v1.Namespace(
            NS_EXTERNAL_SECRETS,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=NS_EXTERNAL_SECRETS,
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=[cert_manager]),
        )

        external_secrets = k8s.helm.v4.Chart(
            "external-secrets",
            k8s.helm.v4.ChartArgs(
                chart=f"{EXTERNAL_SECRETS_CHART_REPO}/external-secrets",
                version=cfg.external_secrets_version,
                namespace=NS_EXTERNAL_SECRETS,
                values={"installCRDs": True},
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[external_secrets_ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")),
            ),
        )

        # ─── 4. Control Plane Namespace ───
        control_plane_ns = k8s.core.v1.Namespace(
            NS_CONTROL_PLANE,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=NS_CONTROL_PLANE,
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(
                provider=k8s_provider,
                depends_on=[cert_manager],
            ),
        )

        data_plane_ns = k8s.core.v1.Namespace(
            NS_DATA_PLANE,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=NS_DATA_PLANE,
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(
                provider=k8s_provider,
                depends_on=[cert_manager],
            ),
        )

        # ─── 5. Gateway controller ───
        # kgateway CRDs are always needed — the CP Helm chart uses kgateway-specific
        # resources like TrafficPolicy.
        kgateway_crds = k8s.helm.v4.Chart(
            "kgateway-crds",
            k8s.helm.v4.ChartArgs(
                chart=f"{KGATEWAY_CHART_REPO}/kgateway-crds",
                version=cfg.kgateway_version,
                namespace=NS_CONTROL_PLANE,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[control_plane_ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")),
            ),
        )

        if p.gateway_mode == "cilium":
            # Cilium is the Gateway API controller.  The OpenChoreo Helm charts
            # hardcode gatewayClassName: kgateway, so we create a GatewayClass
            # with that name backed by Cilium's controller.  No kgateway
            # controller is deployed — Cilium handles everything.
            k8s.apiextensions.CustomResource(
                "gatewayclass-kgateway",
                api_version="gateway.networking.k8s.io/v1",
                kind="GatewayClass",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="kgateway"),
                spec={"controllerName": "io.cilium/gateway-controller"},
                opts=self._child_opts(
                    provider=k8s_provider,
                    depends_on=[*base_depends, kgateway_crds],
                ),
            )
        else:
            k8s.helm.v4.Chart(
                "kgateway",
                k8s.helm.v4.ChartArgs(
                    chart=f"{KGATEWAY_CHART_REPO}/kgateway",
                    version=cfg.kgateway_version,
                    namespace=NS_CONTROL_PLANE,
                    values={
                        "controller": {
                            "extraEnv": {
                                "KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES": "true",
                            },
                        },
                    },
                ),
                opts=pulumi.ResourceOptions.merge(
                    self._child_opts(provider=k8s_provider, depends_on=[kgateway_crds]),
                    pulumi.ResourceOptions(
                        custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")
                    ),
                ),
            )

        # ─── 6. OpenBao ───
        openbao_ns = k8s.core.v1.Namespace(
            NS_OPENBAO,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=NS_OPENBAO,
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=[external_secrets]),
        )

        openbao = k8s.helm.v4.Chart(
            "openbao",
            k8s.helm.v4.ChartArgs(
                chart=f"{OPENBAO_CHART_REPO}/openbao",
                version=cfg.openbao_version,
                namespace=NS_OPENBAO,
                values=openbao_values(
                    cfg.openbao_root_token,
                    cfg.opensearch_username,
                    cfg.opensearch_password,
                    is_dev_stack=pulumi.get_stack()
                    in ("dev", "rancher-desktop", "local", "test", "talos", "talos-baremetal"),
                ),
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[openbao_ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")),
            ),
        )

        # Wait for OpenBao pod ready + postStart to finish
        openbao_ready = WaitPodReady(
            "openbao-ready",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            pod_name="openbao-0",
            namespace=NS_OPENBAO,
            timeout=TIMEOUT_TLS_WAIT,
            opts=self._child_opts(depends_on=[openbao]),
        )

        wait_poststart = sleep(
            "openbao-poststart",
            SLEEP_AFTER_OPENBAO,
            opts=self._child_opts(depends_on=[openbao_ready]),
        )

        # ─── 7. Store GitHub PAT (conditional) ───
        pat_depends: list[pulumi.Resource] = [wait_poststart]
        if cfg.github_pat:
            pat_store = OpenBaoSecrets(
                "store-github-pat",
                kubeconfig_path=cfg.kubeconfig_path,
                context=cfg.kubeconfig_context,
                namespace=NS_OPENBAO,
                root_token=cfg.openbao_root_token,
                secrets=[
                    {"path": "git-token", "data": {"git-token": cfg.github_pat}},
                    {"path": "gitops-token", "data": {"git-token": cfg.github_pat}},
                ],
                opts=self._child_opts(depends_on=[wait_poststart]),
            )
            pat_depends.append(pat_store)

        # ─── 7a. Store Backstage Fork secrets (conditional on Flux/GitOps) ───
        if cfg.enable_flux or cfg.gitops_repo_url:
            backstage_fork_store = OpenBaoSecrets(
                "store-backstage-fork-secrets",
                kubeconfig_path=cfg.kubeconfig_path,
                context=cfg.kubeconfig_context,
                namespace=NS_OPENBAO,
                root_token=cfg.openbao_root_token,
                secrets=[
                    {
                        "path": "backstage-fork-secrets",
                        "data": {
                            "backend-secret": "backstage-fork-backend-secret",
                            "client-id": "backstage-fork",
                            "client-secret": "backstage-fork-client-secret",
                            "auth-authorization-url": f"{THUNDER_INTERNAL_BASE}/oauth2/authorize",
                            "auth-token-url": f"{THUNDER_INTERNAL_BASE}/oauth2/token",
                        },
                    },
                ],
                opts=self._child_opts(depends_on=[wait_poststart]),
            )
            pat_depends.append(backstage_fork_store)

        # ─── 7b. Store OpenObserve credentials (conditional) ───
        if cfg.enable_openobserve and cfg.openobserve_admin_password:
            oo_store = OpenBaoSecrets(
                "store-openobserve-creds",
                kubeconfig_path=cfg.kubeconfig_path,
                context=cfg.kubeconfig_context,
                namespace=NS_OPENBAO,
                root_token=cfg.openbao_root_token,
                secrets=[
                    {
                        "path": "openobserve-admin-credentials",
                        "data": {
                            "ZO_ROOT_USER_EMAIL": cfg.openobserve_admin_email,
                            "ZO_ROOT_USER_PASSWORD": cfg.openobserve_admin_password,
                        },
                    },
                ],
                opts=self._child_opts(depends_on=[wait_poststart]),
            )
            pat_depends.append(oo_store)

        elif cfg.enable_flux or cfg.gitops_repo_url:
            pulumi.log.warn(
                "github_pat is not set but Flux/GitOps features are enabled. "
                "Workflow builds and GitOps reconciliation will fail without a real PAT in OpenBao.",
                resource=None,
            )

        # ─── 7c. Validate OpenBao secrets ───
        _is_dev_stack = pulumi.get_stack() in (
            "dev",
            "rancher-desktop",
            "local",
            "test",
            "talos",
            "talos-baremetal",
        )
        _validate_git_secrets = bool(cfg.github_pat) or _is_dev_stack
        _expected_paths: list[dict[str, object]] = []
        if _validate_git_secrets:
            _expected_paths.append({"path": "git-token", "fields": ["git-token"]})
            _expected_paths.append({"path": "gitops-token", "fields": ["git-token"]})
        if cfg.enable_openobserve:
            _expected_paths.append(
                {"path": "openobserve-admin-credentials", "fields": ["ZO_ROOT_USER_EMAIL", "ZO_ROOT_USER_PASSWORD"]}
            )
        if cfg.enable_flux or cfg.gitops_repo_url:
            _expected_paths.append(
                {
                    "path": "backstage-fork-secrets",
                    "fields": [
                        "backend-secret",
                        "client-id",
                        "client-secret",
                        "auth-authorization-url",
                        "auth-token-url",
                    ],
                }
            )

        openbao_validated = ValidateOpenBaoSecrets(
            "validate-openbao-secrets",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            namespace=NS_OPENBAO,
            root_token=cfg.openbao_root_token,
            expected_paths=_expected_paths,
            opts=self._child_opts(depends_on=pat_depends),
        )

        # ─── 8. ServiceAccount + ClusterSecretStore ───
        eso_sa = k8s.core.v1.ServiceAccount(
            SA_ESO_OPENBAO,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=SA_ESO_OPENBAO,
                namespace=NS_OPENBAO,
            ),
            opts=self._child_opts(
                provider=k8s_provider,
                depends_on=[openbao],
            ),
        )

        cluster_secret_store = k8s.apiextensions.CustomResource(
            "cluster-secret-store",
            api_version="external-secrets.io/v1",
            kind="ClusterSecretStore",
            metadata=k8s.meta.v1.ObjectMetaArgs(name=CLUSTER_SECRET_STORE_NAME),
            spec={
                "provider": {
                    "vault": {
                        "server": f"http://openbao.{NS_OPENBAO}.svc:8200",
                        "path": "secret",
                        "version": "v2",
                        "auth": {
                            "kubernetes": {
                                "mountPath": "kubernetes",
                                "role": "openchoreo-secret-writer-role",
                                "serviceAccountRef": {
                                    "name": SA_ESO_OPENBAO,
                                    "namespace": NS_OPENBAO,
                                },
                            },
                        },
                    },
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[eso_sa, wait_poststart, external_secrets]),
        )

        # ─── 8b. Wait for ClusterSecretStore to be Ready ───
        css_ready = WaitCustomResourceCondition(
            "wait-cluster-secret-store-ready",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            group="external-secrets.io",
            version="v1",
            plural="clustersecretstores",
            resource_name=CLUSTER_SECRET_STORE_NAME,
            namespace=None,
            condition_type="Ready",
            timeout=TIMEOUT_WAIT,
            opts=self._child_opts(depends_on=[cluster_secret_store, openbao_validated]),
        )

        # ─── 9. Workflow namespace (pre-create with PodSecurity labels) ───
        # OpenChoreo creates workflows-{ns} namespaces dynamically, but on
        # Talos the default PodSecurity is *baseline* which rejects the
        # privileged containers needed for Podman/buildah image builds.
        # Pre-create the namespace so labels are in place before any build runs.
        k8s.core.v1.Namespace(
            "workflows-default",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="workflows-default",
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=[wait_gw]),
        )

        # ─── 10. CoreDNS rewrite (platform-specific) ───
        if p.requires_coredns_rewrite:
            k8s.yaml.v2.ConfigGroup(
                "coredns-rewrite",
                files=[cfg.coredns_rewrite_url],
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_gw]),
            )

        self.result = PrerequisitesResult(
            openbao_ready=openbao_ready,
            cluster_secret_store=cluster_secret_store,
            cluster_secret_store_ready=css_ready,
            openbao_validated=openbao_validated,
            control_plane_ns=control_plane_ns,
            data_plane_ns=data_plane_ns,
        )
        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
        provider: k8s.Provider | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs = {
            "parent": self,
            "aliases": [pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)],
        }
        if depends_on:
            opts_kwargs["depends_on"] = depends_on
        if provider:
            opts_kwargs["provider"] = provider
        return pulumi.ResourceOptions(**opts_kwargs)


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    extra_depends: list[pulumi.Resource] | None = None,
) -> PrerequisitesResult:
    """Deploy all prerequisite resources. Returns handles for downstream depends_on."""
    return Prerequisites(
        "prerequisites",
        cfg=cfg,
        k8s_provider=k8s_provider,
        extra_depends=extra_depends,
    ).result
