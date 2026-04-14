# pyright: reportMissingImports=false

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import (
    CLUSTER_SECRET_STORE_NAME,
    DEV_STACKS,
    NS_CERT_MANAGER,
    NS_CONTROL_PLANE,
    NS_DATA_PLANE,
    NS_EXTERNAL_SECRETS,
    NS_FLUX_SYSTEM,
    NS_OPENBAO,
    SA_ESO_OPENBAO,
    SLEEP_AFTER_GATEWAY_API,
    SLEEP_AFTER_OPENBAO,
    TIMEOUT_TLS_WAIT,
    TIMEOUT_WAIT,
    OpenChoreoConfig,
)
from helpers.dynamic_providers import WaitCustomResourceCondition, WaitPodReady
from helpers.wait import sleep
from values.openbao import get_values as openbao_values


class SecretBackendResult:
    def __init__(
        self,
        openbao_ready: WaitPodReady | pulumi.Resource | None,
        cluster_secret_store: k8s.apiextensions.CustomResource | None,
        cluster_secret_store_ready: pulumi.Resource,
    ):
        self.openbao_ready = openbao_ready
        self.cluster_secret_store = cluster_secret_store
        self.cluster_secret_store_ready = cluster_secret_store_ready


class PrerequisitesResult:
    def __init__(
        self,
        openbao_ready: WaitPodReady | pulumi.Resource | None,
        cluster_secret_store: k8s.apiextensions.CustomResource | None,
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
        p = cfg.platform

        wait_gw = sleep("gateway-api", SLEEP_AFTER_GATEWAY_API, opts=self._child_opts(depends_on=base_depends))

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
            opts=self._child_opts(provider=k8s_provider, depends_on=[wait_gw]),
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
            opts=self._child_opts(provider=k8s_provider, depends_on=[wait_gw]),
        )

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

        platform_result = self._setup_secret_backend(
            cfg=cfg,
            k8s_provider=k8s_provider,
            base_depends=base_depends,
        )

        if p.requires_coredns_rewrite:
            k8s.yaml.v2.ConfigGroup(
                "coredns-rewrite",
                files=[cfg.coredns_rewrite_url],
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_gw]),
            )

        self.result = PrerequisitesResult(
            openbao_ready=platform_result.openbao_ready,
            cluster_secret_store=platform_result.cluster_secret_store,
            cluster_secret_store_ready=platform_result.cluster_secret_store_ready,
            control_plane_ns=control_plane_ns,
            data_plane_ns=data_plane_ns,
        )
        self.register_outputs({})

    def _setup_secret_backend(
        self,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        base_depends: list[pulumi.Resource],
    ) -> SecretBackendResult:
        if cfg.platform.secrets_backend == "openbao":
            return self._setup_openbao(cfg=cfg, k8s_provider=k8s_provider, base_depends=base_depends)
        if cfg.platform.secrets_backend == "gcp-sm":
            return self._setup_gcp_secret_manager(cfg=cfg, k8s_provider=k8s_provider, base_depends=base_depends)
        msg = f"Unsupported secrets backend: {cfg.platform.secrets_backend}"
        raise ValueError(msg)

    def _setup_gcp_secret_manager(
        self,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        base_depends: list[pulumi.Resource],
    ) -> SecretBackendResult:
        """GCP Secret Manager path.

        Per ADR-001, Pulumi bootstraps GCP infrastructure (IAM, APIs) in the
        gke-cluster nested project.  The in-cluster resources (ClusterSecretStore,
        ESO ServiceAccount WI annotation) are owned by FluxCD via the
        ``secrets-gcp-sm`` Kustomize component.

        This method only creates a lightweight dependency marker so downstream
        resources (Thunder, control-plane) can depend on prerequisites without
        needing the actual ClusterSecretStore object.
        """
        gcp_sm_ready = sleep(
            "gcp-sm-flux-marker",
            1,
            opts=self._child_opts(depends_on=base_depends),
        )

        return SecretBackendResult(
            openbao_ready=None,
            cluster_secret_store=None,
            cluster_secret_store_ready=gcp_sm_ready,
        )

    def _setup_openbao(
        self,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        base_depends: list[pulumi.Resource],
    ) -> SecretBackendResult:
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
            opts=self._child_opts(provider=k8s_provider, depends_on=base_depends),
        )

        openbao = k8s.helm.v4.Chart(
            "openbao",
            k8s.helm.v4.ChartArgs(
                chart="oci://ghcr.io/openbao/charts/openbao",
                version=cfg.openbao_version,
                namespace=NS_OPENBAO,
                values=openbao_values(cfg.openbao_root_token),
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[openbao_ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")),
            ),
        )

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

        push_secret_git: k8s.core.v1.Secret | None = None
        if cfg.github_pat:
            push_secret_git = k8s.core.v1.Secret(
                "push-git-secrets",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-git-secrets", namespace=NS_OPENBAO),
                string_data={"git-token": cfg.github_pat, "gitops-token": cfg.github_pat},
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_poststart]),
            )

        push_secret_backstage_fork: k8s.core.v1.Secret | None = None
        if cfg.enable_flux or cfg.gitops_repo_url:
            push_secret_backstage_fork = k8s.core.v1.Secret(
                "push-backstage-fork-secrets",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-backstage-fork-secrets", namespace=NS_OPENBAO),
                string_data={
                    "backend-secret": "backstage-fork-backend-secret",
                    "client-id": "backstage-fork",
                    "client-secret": "backstage-fork-client-secret",
                    "auth-authorization-url": f"{cfg.thunder_url}/oauth2/authorize",
                    "jenkins-api-key": "placeholder-not-in-use",
                    "github-token": "placeholder-not-in-use",
                    "github-app-client-secret": "placeholder-not-in-use",
                    "github-app-webhook-secret": "placeholder-not-in-use",
                    "github-app-private-key": "placeholder-not-in-use",
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_poststart]),
            )

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
            pulumi.log.warn(
                "GitHub Actions secrets contain placeholder values. "
                "If Backstage githubActions.enabled=true, GitHub Actions API calls will fail until a real token or GitHub App secrets are written to OpenBao.",
                resource=None,
            )

        _is_dev_stack = pulumi.get_stack() in DEV_STACKS
        push_secret_dev: k8s.core.v1.Secret | None = None
        if _is_dev_stack:
            push_secret_dev = k8s.core.v1.Secret(
                "push-dev-secrets",
                metadata=k8s.meta.v1.ObjectMetaArgs(name="push-dev-secrets", namespace=NS_OPENBAO),
                string_data={
                    "backstage-backend-secret": "local-dev-backend-secret",
                    "backstage-client-secret": "backstage-portal-secret",
                    "backstage-jenkins-api-key": "placeholder-not-in-use",
                    "backstage-github-token": "placeholder-github-token",
                    "backstage-github-app-client-secret": "placeholder-github-app-client-secret",
                    "backstage-github-app-webhook-secret": "placeholder-github-app-webhook-secret",
                    "backstage-github-app-private-key": "placeholder-github-app-private-key",
                    "observer-oauth-client-secret": "openchoreo-observer-resource-reader-client-secret",
                    "rca-oauth-client-secret": "openchoreo-rca-agent-secret",
                    "rca-llm-api-key": "REPLACE_WITH_YOUR_LLM_API_KEY",
                    "npm-token": "fake-npm-token-for-development",
                    "docker-username": "dev-user",
                    "docker-password": "dev-password",
                    "github-pat": "fake-github-token-for-development",
                    "cloudflare-api-token": "placeholder-cloudflare-api-token",
                    "adguard-truenas-url": "http://192.168.0.1:3000",
                    "adguard-truenas-user": "admin",
                    "adguard-truenas-password": "placeholder-adguard-truenas-password",
                    "adguard-k8s-url": "http://adguard-home-k8s.keepalived.svc.cluster.local:3000",
                    "adguard-k8s-user": "admin",
                    "adguard-k8s-password": "placeholder-adguard-k8s-password",
                    "keepalived-auth-pass": "placeholder-keepalived",
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[openbao_ns]),
            )

        eso_sa = k8s.core.v1.ServiceAccount(
            SA_ESO_OPENBAO,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=SA_ESO_OPENBAO, namespace=NS_OPENBAO),
            opts=self._child_opts(provider=k8s_provider, depends_on=[openbao]),
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
                                "serviceAccountRef": {"name": SA_ESO_OPENBAO, "namespace": NS_OPENBAO},
                            }
                        },
                    }
                }
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[eso_sa, wait_poststart]),
        )

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
                                    "remoteRef": {"remoteKey": "backstage-fork-secrets", "property": "backend-secret"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "client-id",
                                    "remoteRef": {"remoteKey": "backstage-fork-secrets", "property": "client-id"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "client-secret",
                                    "remoteRef": {"remoteKey": "backstage-fork-secrets", "property": "client-secret"},
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
                                    "secretKey": "jenkins-api-key",
                                    "remoteRef": {"remoteKey": "backstage-fork-secrets", "property": "jenkins-api-key"},
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
                                    "remoteRef": {"remoteKey": "backstage-backend-secret", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "backstage-client-secret",
                                    "remoteRef": {"remoteKey": "backstage-client-secret", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "backstage-jenkins-api-key",
                                    "remoteRef": {"remoteKey": "backstage-jenkins-api-key", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "observer-oauth-client-secret",
                                    "remoteRef": {"remoteKey": "observer-oauth-client-secret", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "rca-oauth-client-secret",
                                    "remoteRef": {"remoteKey": "rca-oauth-client-secret", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "rca-llm-api-key",
                                    "remoteRef": {"remoteKey": "rca-llm-api-key", "property": "value"},
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
                                    "remoteRef": {"remoteKey": "docker-username", "property": "value"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "docker-password",
                                    "remoteRef": {"remoteKey": "docker-password", "property": "value"},
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
                                    "remoteRef": {"remoteKey": "apps/external-dns/cloudflare", "property": "api-token"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-truenas-url",
                                    "remoteRef": {"remoteKey": "apps/external-dns/adguard-truenas", "property": "url"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-truenas-user",
                                    "remoteRef": {"remoteKey": "apps/external-dns/adguard-truenas", "property": "user"},
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
                                    "remoteRef": {"remoteKey": "apps/external-dns/adguard-k8s", "property": "url"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-k8s-user",
                                    "remoteRef": {"remoteKey": "apps/external-dns/adguard-k8s", "property": "user"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "adguard-k8s-password",
                                    "remoteRef": {"remoteKey": "apps/external-dns/adguard-k8s", "property": "password"},
                                }
                            },
                            {
                                "match": {
                                    "secretKey": "keepalived-auth-pass",
                                    "remoteRef": {"remoteKey": "apps/external-dns/keepalived", "property": "auth-pass"},
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

        return SecretBackendResult(
            openbao_ready=openbao_ready,
            cluster_secret_store=cluster_secret_store,
            cluster_secret_store_ready=push_sync_wait,
        )

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
    return Prerequisites(
        "prerequisites",
        cfg=cfg,
        k8s_provider=k8s_provider,
        extra_depends=extra_depends,
    ).result
