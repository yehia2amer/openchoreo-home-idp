# pyright: reportMissingImports=false

from __future__ import annotations

import json
import os
from pathlib import Path

import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s


NS_EXTERNAL_SECRETS = "external-secrets"
NS_CERT_MANAGER = "cert-manager"
SA_ESO_K8S = "external-secrets"  # Default ESO SA; Flux patches it with WI annotation
SA_CAS_GCP = "google-cas-issuer"
GATEWAY_CLASS_NAME = "gke-l7-rilb"
CLUSTER_ISSUER_NAME = "openchoreo-cas-issuer"


def render_kubeconfig(project_id: str, location: str, cluster_name: str, endpoint: str, ca_cert: str) -> str:
    context = f"gke_{project_id}_{location}_{cluster_name}"
    return f"""apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: {ca_cert}
    server: https://{endpoint}
  name: {context}
contexts:
- context:
    cluster: {context}
    user: {context}
  name: {context}
current-context: {context}
users:
- name: {context}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for Kubernetes authentication.
      provideClusterInfo: true
"""


def write_text_file(path: str, content: str, mode: int = 0o600) -> str:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    os.chmod(output_path, mode)
    return str(output_path)


cfg = pulumi.Config("openchoreo")

project_id = cfg.require("gcp_project_id")
region = cfg.get("gcp_region") or "us-central1"
zone = cfg.get("gcp_zone") or f"{region}-a"
network_name = cfg.get("gcp_network_name") or "openchoreo-vpc"
cluster_name = cfg.get("gcp_gke_cluster_name") or "openchoreo-gke"
_node_count_raw = cfg.get_int("gcp_gke_node_count")
node_count = _node_count_raw if _node_count_raw is not None else 3
machine_type = cfg.get("gcp_gke_machine_type") or "e2-standard-4"
cas_pool_name = cfg.get("gcp_cas_pool_name") or "openchoreo-ca-pool"
cas_tier = cfg.get("gcp_cas_tier") or "DEVOPS"
eso_gsa_name = cfg.get("gcp_eso_service_account") or "openchoreo-eso"
cas_gsa_name = cfg.get("gcp_cas_service_account") or "openchoreo-cas"
artifact_registry_repository_id = cfg.get("artifact_registry_repository_id") or "openchoreo"
gitops_repo_url = cfg.get("gitops_repo_url") or ""
gitops_repo_branch = cfg.get("gitops_repo_branch") or "main"
github_pat = cfg.get_secret("github_pat") or ""
domain_base = cfg.get("domain_base") or "gcp.openchoreo.example.com"
deletion_protection = cfg.get_bool("deletion_protection") or False
master_authorized_cidr = cfg.get("gcp_gke_master_authorized_cidr") or ""
database_encryption_key = cfg.get("gcp_gke_database_encryption_key") or ""

outputs_dir = Path(__file__).resolve().parent / "outputs"
flux_install_manifest_path = Path(__file__).resolve().parent.parent / "flux-install.yaml"

network = gcp.compute.Network(
    "openchoreo-vpc",
    name=network_name,
    auto_create_subnetworks=False,
    project=project_id,
)

subnetwork = gcp.compute.Subnetwork(
    "openchoreo-gke-subnet",
    name=f"{cluster_name}-subnet",
    ip_cidr_range="10.10.0.0/20",
    region=region,
    network=network.id,
    project=project_id,
    secondary_ip_ranges=[
        {"range_name": f"{cluster_name}-pods", "ip_cidr_range": "10.20.0.0/16"},
        {"range_name": f"{cluster_name}-services", "ip_cidr_range": "10.30.0.0/20"},
    ],
)

cluster = gcp.container.Cluster(
    "openchoreo-gke",
    name=cluster_name,
    project=project_id,
    location=region,
    network=network.id,
    subnetwork=subnetwork.id,
    remove_default_node_pool=True,
    initial_node_count=1,
    deletion_protection=deletion_protection,
    datapath_provider="ADVANCED_DATAPATH",
    networking_mode="VPC_NATIVE",
    release_channel={"channel": "REGULAR"},
    workload_identity_config={"workload_pool": f"{project_id}.svc.id.goog"},
    gateway_api_config={"channel": "CHANNEL_STANDARD"},
    ip_allocation_policy={
        "cluster_secondary_range_name": f"{cluster_name}-pods",
        "services_secondary_range_name": f"{cluster_name}-services",
    },
    logging_service="logging.googleapis.com/kubernetes",
    monitoring_service="monitoring.googleapis.com/kubernetes",
    **(
        {
            "master_authorized_networks_config": {
                "cidr_blocks": [{"cidr_block": master_authorized_cidr, "display_name": "admin"}],
            }
        }
        if master_authorized_cidr
        else {}
    ),
    **(
        {
            "database_encryption": {
                "state": "ENCRYPTED",
                "key_name": database_encryption_key,
            }
        }
        if database_encryption_key
        else {}
    ),
    # H6: Maintenance window — Tue 03:00–07:00 UTC (low-traffic window)
    maintenance_policy={
        "recurring_window": {
            "recurrence": "FREQ=WEEKLY;BYDAY=TU",
            "start_time": "2025-01-01T03:00:00Z",
            "end_time": "2025-01-01T07:00:00Z",
        }
    },
)

node_pool = gcp.container.NodePool(
    "openchoreo-gke-nodes",
    project=project_id,
    location=region,
    cluster=cluster.name,
    # H5: Autoscaling — scale between 1 and node_count (default 3) nodes per zone
    autoscaling={
        "min_node_count": 1,
        "max_node_count": node_count,
    },
    management={
        # H4: Auto-repair and auto-upgrade for node security
        "auto_repair": True,
        "auto_upgrade": True,
    },
    node_config={
        "machine_type": machine_type,
        # H4: COS_CONTAINERD — hardened container-optimized OS image
        "image_type": "COS_CONTAINERD",
        # H3: Least-privilege OAuth scopes instead of cloud-platform
        "oauth_scopes": [
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
            "https://www.googleapis.com/auth/servicecontrol",
            "https://www.googleapis.com/auth/service.management.readonly",
            "https://www.googleapis.com/auth/trace.append",
        ],
        "labels": {"openchoreo.dev/cluster": cluster_name},
        # H4: Shielded instance — secure boot, vTPM, integrity monitoring
        "shielded_instance_config": {
            "enable_secure_boot": True,
            "enable_integrity_monitoring": True,
        },
    },
)

eso_gsa = gcp.serviceaccount.Account(
    "eso-gsa",
    project=project_id,
    account_id=eso_gsa_name,
    display_name="OpenChoreo ESO Workload Identity",
)

cas_gsa = gcp.serviceaccount.Account(
    "cas-gsa",
    project=project_id,
    account_id=cas_gsa_name,
    display_name="OpenChoreo CAS Workload Identity",
)

# NOTE: Scoping to individual secrets (gcp.secretmanager.SecretIamMember) would be
# tighter, but ESO needs access to ANY secret the user creates in GCP SM.
# Project-level is the practical minimum scope for a generic secret-store operator.
gcp.projects.IAMMember(
    "eso-secretmanager-access",
    project=project_id,
    role="roles/secretmanager.secretAccessor",
    member=eso_gsa.email.apply(lambda email: f"serviceAccount:{email}"),
)

gcp.serviceaccount.IAMMember(
    "eso-workload-identity-binding",
    service_account_id=eso_gsa.name,
    role="roles/iam.workloadIdentityUser",
    member=f"serviceAccount:{project_id}.svc.id.goog[{NS_EXTERNAL_SECRETS}/{SA_ESO_K8S}]",
)

gcp.serviceaccount.IAMMember(
    "cas-workload-identity-binding",
    service_account_id=cas_gsa.name,
    role="roles/iam.workloadIdentityUser",
    member=f"serviceAccount:{project_id}.svc.id.goog[{NS_CERT_MANAGER}/{SA_CAS_GCP}]",
)


def create_secret(secret_id: str, payload: dict[str, pulumi.Input[str]]) -> None:
    secret = gcp.secretmanager.Secret(
        secret_id,
        project=project_id,
        secret_id=secret_id,
        replication={"auto": {}},
        deletion_protection=deletion_protection,
    )
    # Resolve any Output values in the payload before JSON serialization
    secret_data = pulumi.Output.all(**payload).apply(lambda kv: json.dumps(kv))
    gcp.secretmanager.SecretVersion(
        f"{secret_id}-version",
        secret=secret.id,
        secret_data=secret_data,
    )


if github_pat:
    create_secret("git-token", {"git-token": github_pat, "gitops-token": github_pat})

if gitops_repo_url:
    create_secret(
        "backstage-fork-secrets",
        {
            "backend-secret": "backstage-fork-backend-secret",
            "client-id": "backstage-fork",
            "client-secret": "backstage-fork-client-secret",
            "auth-authorization-url": f"https://thunder.{domain_base}",
            "jenkins-api-key": "placeholder-not-in-use",
        },
    )

cas_pool = gcp.certificateauthority.CaPool(
    "openchoreo-ca-pool",
    project=project_id,
    name=cas_pool_name,
    location=region,
    tier=cas_tier,
    publishing_options={"publish_ca_cert": True, "publish_crl": True},
)

gcp.certificateauthority.CaPoolIamMember(
    "cas-certificate-requester",
    ca_pool=cas_pool.id,
    location=region,
    role="roles/privateca.certificateRequester",
    member=cas_gsa.email.apply(lambda email: f"serviceAccount:{email}"),
)

root_ca = gcp.certificateauthority.Authority(
    "openchoreo-root-ca",
    project=project_id,
    pool=cas_pool.name,
    location=region,
    certificate_authority_id=f"{cas_pool_name}-root",
    deletion_protection=deletion_protection,
    skip_grace_period=not deletion_protection,
    ignore_active_certificates_on_deletion=True,
    config={
        "subject_config": {"subject": {"organization": "OpenChoreo", "common_name": "openchoreo-root-ca"}},
        "x509_config": {
            "ca_options": {"is_ca": True},
            "key_usage": {"base_key_usage": {"cert_sign": True, "crl_sign": True}, "extended_key_usage": {}},
        },
    },
    key_spec={"algorithm": "RSA_PKCS1_4096_SHA256"},
)

subordinate_ca = gcp.certificateauthority.Authority(
    "openchoreo-subordinate-ca",
    project=project_id,
    pool=cas_pool.name,
    location=region,
    certificate_authority_id=f"{cas_pool_name}-sub",
    type="SUBORDINATE",
    deletion_protection=deletion_protection,
    skip_grace_period=not deletion_protection,
    ignore_active_certificates_on_deletion=True,
    config={
        "subject_config": {"subject": {"organization": "OpenChoreo", "common_name": "openchoreo-subordinate-ca"}},
        "x509_config": {
            "ca_options": {"is_ca": True, "zero_max_issuer_path_length": True},
            "key_usage": {"base_key_usage": {"cert_sign": True, "crl_sign": True}, "extended_key_usage": {}},
        },
    },
    subordinate_config={"certificate_authority": root_ca.name},
    lifetime=f"{5 * 365 * 24 * 3600}s",
    key_spec={"algorithm": "RSA_PKCS1_4096_SHA256"},
)

artifact_registry = gcp.artifactregistry.Repository(
    "openchoreo-artifact-registry",
    project=project_id,
    location=region,
    repository_id=artifact_registry_repository_id,
    description="OpenChoreo container images",
    format="DOCKER",
)

kubeconfig_raw = pulumi.Output.all(
    cluster.endpoint,
    cluster.master_auth,
).apply(
    lambda args: render_kubeconfig(
        project_id=project_id,
        location=region,
        cluster_name=cluster_name,
        endpoint=args[0],
        ca_cert=(args[1] or {}).get("cluster_ca_certificate", ""),
    )
)

kubeconfig_path = kubeconfig_raw.apply(lambda raw: write_text_file(str(outputs_dir / "kubeconfig"), raw))
kubeconfig_context = f"gke_{project_id}_{region}_{cluster_name}"

k8s_provider = k8s.Provider(
    "gke-k8s",
    kubeconfig=kubeconfig_raw,
    opts=pulumi.ResourceOptions(depends_on=[node_pool]),
)

install_flux = k8s.yaml.v2.ConfigGroup(
    "install-flux",
    files=[str(flux_install_manifest_path)],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[node_pool]),
)

wait_flux_source_controller = k8s.apps.v1.DeploymentPatch(
    "wait-flux-source-controller",
    metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="source-controller", namespace="flux-system"),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[install_flux]),
)

wait_flux_kustomize_controller = k8s.apps.v1.DeploymentPatch(
    "wait-flux-kustomize-controller",
    metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="kustomize-controller", namespace="flux-system"),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[wait_flux_source_controller]),
)

wait_flux_helm_controller = k8s.apps.v1.DeploymentPatch(
    "wait-flux-helm-controller",
    metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="helm-controller", namespace="flux-system"),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[wait_flux_kustomize_controller]),
)

git_credentials_secret: k8s.core.v1.Secret | None = None
if github_pat:
    git_credentials_secret = k8s.core.v1.Secret(
        "flux-git-credentials",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="flux-git-credentials", namespace="flux-system"),
        string_data={"username": "git", "password": github_pat},
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[wait_flux_helm_controller]),
    )

if gitops_repo_url:
    git_repo_spec: dict[str, object] = {
        "interval": "5m",
        "timeout": "90s",
        "url": gitops_repo_url,
        "ref": {"branch": gitops_repo_branch},
    }
    if github_pat:
        git_repo_spec["secretRef"] = {"name": "flux-git-credentials"}

    git_repo_depends: list[pulumi.Resource] = [wait_flux_helm_controller]
    if git_credentials_secret is not None:
        git_repo_depends.append(git_credentials_secret)

    git_repository = k8s.apiextensions.CustomResource(
        "flux-system-repository",
        api_version="source.toolkit.fluxcd.io/v1",
        kind="GitRepository",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="flux-system", namespace="flux-system"),
        spec=git_repo_spec,
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=git_repo_depends),
    )

    k8s.apiextensions.CustomResource(
        "root-kustomization",
        api_version="kustomize.toolkit.fluxcd.io/v1",
        kind="Kustomization",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="root-sync", namespace="flux-system"),
        spec={
            "interval": "5m",
            "path": "./clusters/gke/",
            "prune": True,
            "wait": True,
            "sourceRef": {"kind": "GitRepository", "name": "flux-system"},
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[git_repository]),
    )

pulumi.export("project_id", project_id)
pulumi.export("region", region)
pulumi.export("zone", zone)
pulumi.export("cluster_name", cluster.name)
pulumi.export("cluster_endpoint", cluster.endpoint)
pulumi.export("network_name", network.name)
pulumi.export("subnetwork_name", subnetwork.name)
pulumi.export("kubeconfig_raw", pulumi.Output.secret(kubeconfig_raw))
pulumi.export("kubeconfig_path", kubeconfig_path)
pulumi.export("kubeconfig_context", kubeconfig_context)
pulumi.export("gcp_project_id", project_id)
pulumi.export("gcp_region", region)
pulumi.export("gcp_gke_cluster_name", cluster_name)
pulumi.export("gcp_cas_pool_name", cas_pool.name)
pulumi.export("gcp_eso_service_account", eso_gsa.email)
pulumi.export("gcp_cas_service_account", cas_gsa.email)
pulumi.export(
    "artifact_registry_url",
    pulumi.Output.concat(region, "-docker.pkg.dev/", project_id, "/", artifact_registry.repository_id),
)
pulumi.export("artifact_registry_repository_id", artifact_registry.repository_id)
pulumi.export("gateway_class_name", GATEWAY_CLASS_NAME)
pulumi.export("cluster_issuer_name", CLUSTER_ISSUER_NAME)
pulumi.export("cas_authority_name", subordinate_ca.name)
