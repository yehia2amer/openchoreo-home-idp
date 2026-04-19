# pyright: reportMissingImports=false

"""Backstage infrastructure: Cloud SQL PostgreSQL + GCS TechDocs bucket.

Provisions GCP-managed infrastructure for the backstage-fork service:
1. Cloud SQL PostgreSQL instance, database, and user
2. GCS bucket for TechDocs with Workload Identity access
3. Credentials stored in GCP Secret Manager
"""

from __future__ import annotations

import json
import secrets

import pulumi
import pulumi_gcp as gcp

from config import OpenChoreoConfig
from helpers.component_utils import child_opts


class BackstageInfraResult:
    def __init__(
        self,
        pg_instance_name: pulumi.Output[str],
        techdocs_bucket_name: pulumi.Output[str],
        techdocs_sa_email: pulumi.Output[str],
    ):
        self.pg_instance_name = pg_instance_name
        self.techdocs_bucket_name = techdocs_bucket_name
        self.techdocs_sa_email = techdocs_sa_email


class BackstageInfra(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: object,  # unused but kept for interface consistency
        depends: list[pulumi.Resource] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:BackstageInfra", name, {}, opts)

        base_depends = depends or []
        instance_name = cfg.backstage_pg_instance_name or f"{cfg.gcp_gke_cluster_name}-backstage-pg"

        # Private services connection for Cloud SQL
        # Creates a VPC peering with Google's service networking
        # so Cloud SQL can use private IPs within our VPC.
        private_ip_range = gcp.compute.GlobalAddress(
            "backstage-pg-private-ip-range",
            project=cfg.gcp_project_id,
            name=f"{instance_name}-private-ip",
            purpose="VPC_PEERING",
            address_type="INTERNAL",
            prefix_length=16,
            network=pulumi.Output.concat(
                "projects/", cfg.gcp_project_id, "/global/networks/", cfg.gcp_network_name
            ),
            opts=child_opts(self, depends_on=base_depends),
        )

        private_services_connection = gcp.servicenetworking.Connection(
            "backstage-pg-private-connection",
            network=pulumi.Output.concat(
                "projects/", cfg.gcp_project_id, "/global/networks/", cfg.gcp_network_name
            ),
            service="servicenetworking.googleapis.com",
            reserved_peering_ranges=[private_ip_range.name],
            opts=child_opts(self, depends_on=[private_ip_range]),
        )

        # ──────────────────────────────────────────────────────────────
        # Part A: Cloud SQL PostgreSQL
        # ──────────────────────────────────────────────────────────────

        pg_instance = gcp.sql.DatabaseInstance(
            "backstage-pg-instance",
            name=instance_name,
            database_version="POSTGRES_15",
            region=cfg.gcp_region,
            project=cfg.gcp_project_id,
            deletion_protection=False,
            settings=gcp.sql.DatabaseInstanceSettingsArgs(
                tier=cfg.backstage_pg_tier,
                ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
                    ipv4_enabled=False,
                    private_network=pulumi.Output.concat(
                        "projects/", cfg.gcp_project_id, "/global/networks/", cfg.gcp_network_name
                    ),
                    enable_private_path_for_google_cloud_services=True,
                ),
                disk_autoresize=True,
                disk_size=10,
                disk_type="PD_SSD",
                backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
                    enabled=True,
                    start_time="03:00",
                ),
            ),
            opts=child_opts(self, depends_on=[*base_depends, private_services_connection]),
        )

        pg_database = gcp.sql.Database(
            "backstage-pg-database",
            name="backstage",
            instance=pg_instance.name,
            project=cfg.gcp_project_id,
            opts=child_opts(self, depends_on=[pg_instance]),
        )

        # Generate a secure password at plan time
        pg_password = secrets.token_urlsafe(24)

        pg_user = gcp.sql.User(
            "backstage-pg-user",
            name="backstage",
            instance=pg_instance.name,
            password=pulumi.Output.secret(pg_password),
            project=cfg.gcp_project_id,
            opts=child_opts(self, depends_on=[pg_database]),
        )

        # Store PG credentials in GCP Secret Manager
        pg_creds_secret = gcp.secretmanager.Secret(
            "backstage-fork-pg-credentials",
            project=cfg.gcp_project_id,
            secret_id="backstage-fork-pg-credentials",
            replication={"auto": {}},
            opts=child_opts(self, depends_on=base_depends),
        )

        gcp.secretmanager.SecretVersion(
            "backstage-fork-pg-credentials-version",
            secret=pg_creds_secret.id,
            secret_data=pulumi.Output.secret(
                pg_instance.private_ip_address.apply(
                    lambda ip: json.dumps(
                        {
                            "pg-host": ip,
                            "pg-port": "5432",
                            "pg-user": "backstage",
                            "pg-password": pg_password,
                            "pg-database": "backstage",
                        }
                    )
                )
            ),
            opts=child_opts(self, depends_on=[pg_creds_secret, pg_user]),
        )

        # ──────────────────────────────────────────────────────────────
        # Part B: GCS Bucket for TechDocs (native GCS via Workload Identity)
        # ──────────────────────────────────────────────────────────────

        techdocs_bucket_name = f"{cfg.gcp_project_id}-backstage-techdocs"

        techdocs_bucket = gcp.storage.Bucket(
            "backstage-techdocs-bucket",
            name=techdocs_bucket_name,
            location=cfg.gcp_region,
            project=cfg.gcp_project_id,
            uniform_bucket_level_access=True,
            force_destroy=True,
            opts=child_opts(self, depends_on=base_depends),
        )

        techdocs_sa = gcp.serviceaccount.Account(
            "backstage-techdocs-sa",
            account_id="backstage-techdocs",
            display_name="Backstage TechDocs GCS Access",
            project=cfg.gcp_project_id,
            opts=child_opts(self, depends_on=base_depends),
        )

        gcp.storage.BucketIAMMember(
            "backstage-techdocs-bucket-iam",
            bucket=techdocs_bucket.name,
            role="roles/storage.objectAdmin",
            member=techdocs_sa.email.apply(lambda email: f"serviceAccount:{email}"),
            opts=child_opts(self, depends_on=[techdocs_bucket, techdocs_sa]),
        )

        # Workload Identity: let K8s SA impersonate this GCP SA
        gcp.serviceaccount.IAMMember(
            "backstage-techdocs-wi-binding",
            service_account_id=techdocs_sa.name,
            role="roles/iam.workloadIdentityUser",
            member=pulumi.Output.concat(
                "serviceAccount:",
                cfg.gcp_project_id,
                ".svc.id.goog[backstage-fork/backstage-fork]",
            ),
            opts=child_opts(self, depends_on=[techdocs_sa]),
        )

        # Store TechDocs GCS config in GCP Secret Manager
        techdocs_creds_secret = gcp.secretmanager.Secret(
            "backstage-fork-techdocs-s3-credentials",
            project=cfg.gcp_project_id,
            secret_id="backstage-fork-techdocs-s3-credentials",
            replication={"auto": {}},
            opts=child_opts(self, depends_on=base_depends),
        )

        gcp.secretmanager.SecretVersion(
            "backstage-fork-techdocs-s3-credentials-version",
            secret=techdocs_creds_secret.id,
            secret_data=pulumi.Output.secret(
                pulumi.Output.all(
                    techdocs_bucket.name,
                    techdocs_sa.email,
                ).apply(
                    lambda args: json.dumps(
                        {
                            "techdocs-gcs-bucket-name": args[0],
                            "techdocs-gcs-sa-email": args[1],
                        }
                    )
                )
            ),
            opts=child_opts(self, depends_on=[techdocs_creds_secret, techdocs_bucket, techdocs_sa]),
        )

        # ──────────────────────────────────────────────────────────────
        # Part C: GitHub App Credentials in GCP Secret Manager
        # ──────────────────────────────────────────────────────────────

        if cfg.backstage_github_app_id:
            github_app_secret = gcp.secretmanager.Secret(
                "backstage-fork-github-app-credentials",
                project=cfg.gcp_project_id,
                secret_id="backstage-fork-github-app-credentials",
                replication={"auto": {}},
                opts=child_opts(self, depends_on=base_depends),
            )

            gcp.secretmanager.SecretVersion(
                "backstage-fork-github-app-credentials-version",
                secret=github_app_secret.id,
                secret_data=pulumi.Output.secret(
                    pulumi.Output.all(
                        cfg.backstage_github_app_id,
                        cfg.backstage_github_app_client_id,
                        cfg.backstage_github_app_client_secret,
                        cfg.backstage_github_app_webhook_secret,
                        cfg.backstage_github_private_key,
                    ).apply(
                        lambda args: json.dumps(
                            {
                                "github-app-id": args[0],
                                "github-app-client-id": args[1],
                                "github-app-client-secret": args[2],
                                "github-app-webhook-secret": args[3],
                                "github-private-key": args[4],
                            }
                        )
                    )
                ),
                opts=child_opts(self, depends_on=[github_app_secret]),
            )

        # ──────────────────────────────────────────────────────────────
        # Outputs
        # ──────────────────────────────────────────────────────────────

        self.pg_instance_name = pg_instance.name
        self.techdocs_bucket_name = techdocs_bucket.name
        self.techdocs_sa_email = techdocs_sa.email
        self.result = BackstageInfraResult(
            pg_instance_name=pg_instance.name,
            techdocs_bucket_name=techdocs_bucket.name,
            techdocs_sa_email=techdocs_sa.email,
        )
        self.register_outputs(
            {
                "pg_instance_name": pg_instance.name,
                "techdocs_bucket_name": techdocs_bucket.name,
                "techdocs_sa_email": techdocs_sa.email,
            }
        )
