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
        cluster_secret_store_ready: pulumi.Resource,
        control_plane_ns: k8s.core.v1.Namespace,
        data_plane_ns: k8s.core.v1.Namespace,
    ):
        self.openbao_ready = openbao_ready
        self.cluster_secret_store = cluster_secret_store
        self.cluster_secret_store_ready = cluster_secret_store_ready
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
                values=openbao_values(cfg.openbao_root_token),
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
        push_secret_git: k8s.core.v1.Secret | None = None
        if cfg.github_pat:
            push_secret_git = k8s.core.v1.Secret(
                "push-git-secrets",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-git-secrets", namespace=NS_OPENBAO),
                string_data={
                    "git-token": cfg.github_pat,
                    "gitops-token": cfg.github_pat,
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_poststart]),
            )

        # ─── 7a. Store Backstage Fork secrets (conditional on Flux/GitOps) ───
        push_secret_backstage_fork: k8s.core.v1.Secret | None = None
        if cfg.enable_flux or cfg.gitops_repo_url:
            push_secret_backstage_fork = k8s.core.v1.Secret(
                "push-backstage-fork-secrets",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-backstage-fork-secrets", namespace=NS_OPENBAO),
                string_data={
                    "backend-secret": "backstage-fork-backend-secret",
                    "client-id": "backstage-fork",
                    "client-secret": "backstage-fork-client-secret",
                    "auth-authorization-url": f"{THUNDER_INTERNAL_BASE}/oauth2/authorize",
                    "auth-token-url": f"{THUNDER_INTERNAL_BASE}/oauth2/token",
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_poststart]),
            )

        # ─── 7b. Store OpenObserve credentials (conditional) ───
        push_secret_openobserve: k8s.core.v1.Secret | None = None
        if cfg.enable_openobserve and cfg.openobserve_admin_password:
            push_secret_openobserve = k8s.core.v1.Secret(
                "push-openobserve-creds",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-openobserve-creds", namespace=NS_OPENBAO),
                string_data={
                    "ZO_ROOT_USER_EMAIL": cfg.openobserve_admin_email,
                    "ZO_ROOT_USER_PASSWORD": cfg.openobserve_admin_password,
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_poststart]),
            )

        if not cfg.github_pat and (cfg.enable_flux or cfg.gitops_repo_url):
            pulumi.log.warn(
                "github_pat is not set but Flux/GitOps features are enabled. "
                "Workflow builds and GitOps reconciliation will fail without a real PAT in OpenBao.",
                resource=None,
            )

        _is_dev_stack = pulumi.get_stack() in (
            "dev",
            "rancher-desktop",
            "local",
            "test",
            "talos",
            "talos-baremetal",
        )
        push_secret_dev: k8s.core.v1.Secret | None = None
        if _is_dev_stack:
            dev_secret_data = {
                "backstage-backend-secret": "local-dev-backend-secret",
                "backstage-client-secret": "backstage-portal-secret",
                "backstage-jenkins-api-key": "placeholder-not-in-use",
                "observer-oauth-client-secret": "openchoreo-observer-resource-reader-client-secret",
                "rca-oauth-client-secret": "openchoreo-rca-agent-secret",
                "rca-llm-api-key": "REPLACE_WITH_YOUR_LLM_API_KEY",
                "opensearch-username": cfg.opensearch_username,
                "opensearch-password": cfg.opensearch_password,
                "npm-token": "fake-npm-token-for-development",
                "docker-username": "dev-user",
                "docker-password": "dev-password",
                "github-pat": "fake-github-token-for-development",
                "cloudflare-api-token": "cfut_uaRooKcWkb77Ygz9CNr7KXwsNnJCiNUALAe5RULDcfd4b1b7",
                "adguard-truenas-url": "http://192.168.0.129:30004",
                "adguard-truenas-user": "yehia",
                "adguard-truenas-password": "t9QVO!wg$C7$1dAHZ@%j6HH",
                "adguard-k8s-url": "http://adguard-home-k8s.keepalived.svc.cluster.local:3000",
                "adguard-k8s-user": "admin",
                "adguard-k8s-password": "pI03loPa6Nhlele",
                "keepalived-auth-pass": "HHsiI0T7",
            }
            push_secret_dev = k8s.core.v1.Secret(
                "push-dev-secrets",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-dev-secrets", namespace=NS_OPENBAO),
                string_data=dev_secret_data,
                opts=self._child_opts(provider=k8s_provider, depends_on=[openbao_ns]),
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
            opts=self._child_opts(depends_on=[cluster_secret_store]),
        )

        push_secrets: list[pulumi.Resource] = []

        if cfg.github_pat and push_secret_git is not None:
            push_secrets.append(
                k8s.apiextensions.CustomResource(
                    "pushsecret-git-secrets",
                    api_version="external-secrets.io/v1alpha1",
                    kind="PushSecret",
                    metadata=k8s.meta.v1.ObjectMetaArgs(name="git-secrets", namespace=NS_OPENBAO),
                    spec={
                        "refreshInterval": "5m",
                        "updatePolicy": "Replace",
                        "deletionPolicy": "None",
                        "secretStoreRefs": [{"name": CLUSTER_SECRET_STORE_NAME, "kind": "ClusterSecretStore"}],
                        "selector": {"secret": {"name": "push-git-secrets"}},
                        "data": [
                            {
                                "match": {
                                    "secretKey": "git-token",
                                    "remoteRef": {"remoteKey": "git-token", "property": "git-token"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "gitops-token",
                                    "remoteRef": {"remoteKey": "gitops-token", "property": "git-token"},
                                }
                            },
                        ],
                    },
                    opts=self._child_opts(provider=k8s_provider, depends_on=[css_ready, push_secret_git]),
                )
            )

        if (cfg.enable_flux or cfg.gitops_repo_url) and push_secret_backstage_fork is not None:
            push_secrets.append(
                k8s.apiextensions.CustomResource(
                    "pushsecret-backstage-fork-secrets",
                    api_version="external-secrets.io/v1alpha1",
                    kind="PushSecret",
                    metadata=k8s.meta.v1.ObjectMetaArgs(name="backstage-fork-secrets", namespace=NS_OPENBAO),
                    spec={
                        "refreshInterval": "5m",
                        "updatePolicy": "Replace",
                        "deletionPolicy": "None",
                        "secretStoreRefs": [{"name": CLUSTER_SECRET_STORE_NAME, "kind": "ClusterSecretStore"}],
                        "selector": {"secret": {"name": "push-backstage-fork-secrets"}},
                        "data": [
                            {
                                "match": {
                                    "secretKey": "backend-secret",
                                    "remoteRef": {
                                        "remoteKey": "backstage-fork-secrets",
                                        "property": "backend-secret",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "client-id",
                                    "remoteRef": {
                                        "remoteKey": "backstage-fork-secrets",
                                        "property": "client-id",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "client-secret",
                                    "remoteRef": {
                                        "remoteKey": "backstage-fork-secrets",
                                        "property": "client-secret",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "auth-authorization-url",
                                    "remoteRef": {
                                        "remoteKey": "backstage-fork-secrets",
                                        "property": "auth-authorization-url",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "auth-token-url",
                                    "remoteRef": {
                                        "remoteKey": "backstage-fork-secrets",
                                        "property": "auth-token-url",
                                    },
                                }
                            },
                        ],
                    },
                    opts=self._child_opts(provider=k8s_provider, depends_on=[css_ready, push_secret_backstage_fork]),
                )
            )

        if cfg.enable_openobserve and cfg.openobserve_admin_password and push_secret_openobserve is not None:
            push_secrets.append(
                k8s.apiextensions.CustomResource(
                    "pushsecret-openobserve-creds",
                    api_version="external-secrets.io/v1alpha1",
                    kind="PushSecret",
                    metadata=k8s.meta.v1.ObjectMetaArgs(name="openobserve-creds", namespace=NS_OPENBAO),
                    spec={
                        "refreshInterval": "5m",
                        "updatePolicy": "Replace",
                        "deletionPolicy": "None",
                        "secretStoreRefs": [{"name": CLUSTER_SECRET_STORE_NAME, "kind": "ClusterSecretStore"}],
                        "selector": {"secret": {"name": "push-openobserve-creds"}},
                        "data": [
                            {
                                "match": {
                                    "secretKey": "ZO_ROOT_USER_EMAIL",
                                    "remoteRef": {
                                        "remoteKey": "openobserve-admin-credentials",
                                        "property": "ZO_ROOT_USER_EMAIL",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "ZO_ROOT_USER_PASSWORD",
                                    "remoteRef": {
                                        "remoteKey": "openobserve-admin-credentials",
                                        "property": "ZO_ROOT_USER_PASSWORD",
                                    },
                                }
                            },
                        ],
                    },
                    opts=self._child_opts(provider=k8s_provider, depends_on=[css_ready, push_secret_openobserve]),
                )
            )

        if _is_dev_stack and push_secret_dev is not None:
            push_secrets.append(
                k8s.apiextensions.CustomResource(
                    "pushsecret-dev-secrets",
                    api_version="external-secrets.io/v1alpha1",
                    kind="PushSecret",
                    metadata=k8s.meta.v1.ObjectMetaArgs(name="dev-secrets", namespace=NS_OPENBAO),
                    spec={
                        "refreshInterval": "5m",
                        "updatePolicy": "Replace",
                        "deletionPolicy": "None",
                        "secretStoreRefs": [{"name": CLUSTER_SECRET_STORE_NAME, "kind": "ClusterSecretStore"}],
                        "selector": {"secret": {"name": "push-dev-secrets"}},
                        "data": [
                            {
                                "match": {
                                    "secretKey": "backstage-backend-secret",
                                    "remoteRef": {
                                        "remoteKey": "backstage-backend-secret",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "backstage-client-secret",
                                    "remoteRef": {
                                        "remoteKey": "backstage-client-secret",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "backstage-jenkins-api-key",
                                    "remoteRef": {
                                        "remoteKey": "backstage-jenkins-api-key",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "observer-oauth-client-secret",
                                    "remoteRef": {
                                        "remoteKey": "observer-oauth-client-secret",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "rca-oauth-client-secret",
                                    "remoteRef": {
                                        "remoteKey": "rca-oauth-client-secret",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "rca-llm-api-key",
                                    "remoteRef": {
                                        "remoteKey": "rca-llm-api-key",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "opensearch-username",
                                    "remoteRef": {
                                        "remoteKey": "opensearch-username",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "opensearch-password",
                                    "remoteRef": {
                                        "remoteKey": "opensearch-password",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "npm-token",
                                    "remoteRef": {"remoteKey": "npm-token", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "docker-username",
                                    "remoteRef": {
                                        "remoteKey": "docker-username",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "docker-password",
                                    "remoteRef": {
                                        "remoteKey": "docker-password",
                                        "property": "value",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "github-pat",
                                    "remoteRef": {"remoteKey": "github-pat", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "cloudflare-api-token",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/cloudflare",
                                        "property": "api-token",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-truenas-url",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/adguard-truenas",
                                        "property": "url",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-truenas-user",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/adguard-truenas",
                                        "property": "user",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-truenas-password",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/adguard-truenas",
                                        "property": "password",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-k8s-url",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/adguard-k8s",
                                        "property": "url",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-k8s-user",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/adguard-k8s",
                                        "property": "user",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-k8s-password",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/adguard-k8s",
                                        "property": "password",
                                    },
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "keepalived-auth-pass",
                                    "remoteRef": {
                                        "remoteKey": "apps/external-dns/keepalived",
                                        "property": "auth-pass",
                                    },
                                }
                            },
                        ],
                    },
                    opts=self._child_opts(provider=k8s_provider, depends_on=[css_ready, push_secret_dev]),
                )
            )

        push_sync_wait = sleep(
            "pushsecret-sync",
            15,
            opts=self._child_opts(depends_on=push_secrets + [css_ready]),
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
            cluster_secret_store_ready=push_sync_wait,
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
