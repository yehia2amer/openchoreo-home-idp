# pyright: reportMissingImports=false

"""TLS Setup component: self-signed CA chain and per-plane wildcard certificates."""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import (
    CERT_CP_GATEWAY_TLS,
    CERT_DP_GATEWAY_TLS,
    CERT_OPENCHOREO_CA,
    ISSUER_OPENCHOREO_CA,
    ISSUER_SELFSIGNED_BOOTSTRAP,
    NS_CERT_MANAGER,
    NS_CONTROL_PLANE,
    NS_DATA_PLANE,
    SECRET_OPENCHOREO_CA,
    OpenChoreoConfig,
)


class TlsSetupResult:
    """Outputs from the TLS setup component."""

    def __init__(
        self,
        ca_issuer: k8s.apiextensions.CustomResource,
        cp_cert: k8s.apiextensions.CustomResource,
        dp_cert: k8s.apiextensions.CustomResource,
    ):
        self.ca_issuer = ca_issuer
        self.cp_cert = cp_cert
        self.dp_cert = dp_cert


class TlsSetup(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:TlsSetup", name, {}, opts)

        # ─── 1. Self-signed bootstrap ClusterIssuer ───
        selfsigned_bootstrap = k8s.apiextensions.CustomResource(
            ISSUER_SELFSIGNED_BOOTSTRAP,
            api_version="cert-manager.io/v1",
            kind="ClusterIssuer",
            metadata=k8s.meta.v1.ObjectMetaArgs(name=ISSUER_SELFSIGNED_BOOTSTRAP),
            spec={"selfSigned": {}},
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        # ─── 2. OpenChoreo CA Certificate (self-signed, ECDSA P256) ───
        openchoreo_ca_cert = k8s.apiextensions.CustomResource(
            CERT_OPENCHOREO_CA,
            api_version="cert-manager.io/v1",
            kind="Certificate",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=CERT_OPENCHOREO_CA,
                namespace=NS_CERT_MANAGER,
            ),
            spec={
                "isCA": True,
                "commonName": CERT_OPENCHOREO_CA,
                "secretName": SECRET_OPENCHOREO_CA,
                "privateKey": {
                    "algorithm": "ECDSA",
                    "size": 256,
                },
                "issuerRef": {
                    "name": ISSUER_SELFSIGNED_BOOTSTRAP,
                    "kind": "ClusterIssuer",
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[selfsigned_bootstrap]),
        )

        # ─── 3. OpenChoreo CA ClusterIssuer (backed by CA secret) ───
        openchoreo_ca_issuer = k8s.apiextensions.CustomResource(
            f"{ISSUER_OPENCHOREO_CA}-issuer",
            api_version="cert-manager.io/v1",
            kind="ClusterIssuer",
            metadata=k8s.meta.v1.ObjectMetaArgs(name=ISSUER_OPENCHOREO_CA),
            spec={
                "ca": {
                    "secretName": SECRET_OPENCHOREO_CA,
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[openchoreo_ca_cert]),
        )

        # ─── 4. Control Plane gateway TLS Certificate (wildcard) ───
        cp_gateway_tls = k8s.apiextensions.CustomResource(
            CERT_CP_GATEWAY_TLS,
            api_version="cert-manager.io/v1",
            kind="Certificate",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=CERT_CP_GATEWAY_TLS,
                namespace=NS_CONTROL_PLANE,
            ),
            spec={
                "secretName": CERT_CP_GATEWAY_TLS,
                "issuerRef": {
                    "name": ISSUER_OPENCHOREO_CA,
                    "kind": "ClusterIssuer",
                },
                "dnsNames": [
                    f"*.{cfg.domain_base}",
                    cfg.domain_base,
                ],
                "privateKey": {
                    "rotationPolicy": "Always",
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[openchoreo_ca_issuer]),
        )

        # ─── 5. Data Plane gateway TLS Certificate (wildcard) ───
        dp_gateway_tls = k8s.apiextensions.CustomResource(
            CERT_DP_GATEWAY_TLS,
            api_version="cert-manager.io/v1",
            kind="Certificate",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=CERT_DP_GATEWAY_TLS,
                namespace=NS_DATA_PLANE,
            ),
            spec={
                "secretName": CERT_DP_GATEWAY_TLS,
                "issuerRef": {
                    "name": ISSUER_OPENCHOREO_CA,
                    "kind": "ClusterIssuer",
                },
                "dnsNames": [
                    f"*.{cfg.domain_base}",
                    cfg.domain_base,
                ],
                "privateKey": {
                    "rotationPolicy": "Always",
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[openchoreo_ca_issuer]),
        )

        self.result = TlsSetupResult(
            ca_issuer=openchoreo_ca_issuer,
            cp_cert=cp_gateway_tls,
            dp_cert=dp_gateway_tls,
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
