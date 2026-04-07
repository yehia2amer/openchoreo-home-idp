"""Control Plane component: Thunder, Backstage ExternalSecret, CP Helm chart."""

from __future__ import annotations

import hashlib
import json
import urllib.request

import pulumi
import pulumi_command as command
import pulumi_kubernetes as k8s
import yaml

from config import (
    CLUSTER_SECRET_STORE_NAME,
    NS_CONTROL_PLANE,
    NS_THUNDER,
    NS_WORKFLOW_PLANE,
    SECRET_BACKSTAGE,
    SLEEP_AFTER_ESO_SYNC,
    SLEEP_AFTER_THUNDER,
    TIMEOUT_DEFAULT,
    OpenChoreoConfig,
)
from helpers.dynamic_providers import LabelNamespace
from helpers.wait import sleep
from values.control_plane import get_values as cp_values


def _fetch_yaml(url: str) -> dict:
    """Fetch and parse a remote YAML file."""
    with urllib.request.urlopen(url, timeout=30) as resp:
        return yaml.safe_load(resp.read())


def _thunder_image(values: dict, default_tag: str) -> str:
    """Build the Thunder image reference from chart values."""
    image = values.get("deployment", {}).get("image", {})
    registry = image.get("registry", "ghcr.io/asgardeo")
    repository = image.get("repository", "thunder")
    digest = image.get("digest")
    if digest:
        return f"{registry}/{repository}@{digest}"
    return f"{registry}/{repository}:{image.get('tag', default_tag)}"


class ControlPlaneResult:
    """Outputs from the control plane component."""

    def __init__(self, helm_chart: k8s.helm.v3.Release, label_ns: LabelNamespace):
        self.helm_chart = helm_chart
        self.label_ns = label_ns


class ControlPlane(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:ControlPlane", name, {}, opts)

        # ─── 1. Thunder (Identity Provider) ───
        thunder_ns = k8s.core.v1.Namespace(
            NS_THUNDER,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_THUNDER),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends or []),
        )

        thunder_values = _fetch_yaml(cfg.thunder_values_url)
        thunder_values.setdefault("thunderServer", {})["publicUrl"] = cfg.thunder_url

        # Override Thunder hostnames/URLs for the target platform.
        # The upstream values file hardcodes openchoreo.localhost.
        thunder_host = f"thunder.{cfg.domain_base}"
        thunder_values.setdefault("httproute", {})["hostnames"] = [thunder_host]
        thunder_config = thunder_values.setdefault("configuration", {})
        thunder_config.setdefault("server", {})["publicUrl"] = cfg.thunder_url
        # Keep httpOnly=true: TLS is terminated at the Gateway, not Thunder itself
        thunder_config.setdefault("server", {})["httpOnly"] = True
        gate = thunder_config.setdefault("gateClient", {})
        gate["hostname"] = thunder_host
        gate["port"] = cfg.cp_port
        gate["scheme"] = cfg.scheme
        thunder_config.setdefault("cors", {})["allowedOrigins"] = [
            cfg.backstage_url,
            cfg.backstage_fork_url,
            cfg.thunder_url,
        ]
        thunder_config.setdefault("passkey", {})["allowedOrigins"] = [
            cfg.backstage_url,
            cfg.backstage_fork_url,
        ]

        thunder_bootstrap_scripts = thunder_values.get("bootstrap", {}).get("scripts", {})
        # Fix redirect URIs in bootstrap scripts to match the target platform domain.
        for script_name, script_body in thunder_bootstrap_scripts.items():
            thunder_bootstrap_scripts[script_name] = script_body.replace(
                "http://openchoreo.localhost:8080", cfg.backstage_url
            ).replace("http://thunder.openchoreo.localhost:8080", cfg.thunder_url)
        # Assign a default theme to Backstage and Console apps.
        # Thunder Gate UI returns DSR-1005 if APPLICATION.THEME_ID is NULL.
        thunder_bootstrap_scripts["60-assign-themes.sh"] = """#!/bin/bash
set -e

DB="/opt/thunder/repository/database/configdb.db"

log_info "Assigning default theme to applications..."

# Wait for themes to be seeded (created on first boot)
for i in $(seq 1 30); do
  THEME_COUNT=$(sqlite3 "$DB" "SELECT COUNT(*) FROM THEME" 2>/dev/null || echo "0")
  [ "$THEME_COUNT" -gt 0 ] && break
  sleep 2
done

DEFAULT_THEME_ID=$(sqlite3 "$DB" \
  "SELECT ID FROM THEME WHERE DISPLAY_NAME='Pale Indigo' ORDER BY CREATED_AT DESC LIMIT 1")

if [ -z "$DEFAULT_THEME_ID" ]; then
  DEFAULT_THEME_ID=$(sqlite3 "$DB" \
    "SELECT ID FROM THEME ORDER BY CREATED_AT DESC LIMIT 1")
fi

if [ -n "$DEFAULT_THEME_ID" ]; then
  sqlite3 "$DB" \
    "UPDATE APPLICATION SET THEME_ID='$DEFAULT_THEME_ID' WHERE THEME_ID IS NULL;"
  log_info "Assigned theme $DEFAULT_THEME_ID to all applications without a theme"
else
  log_info "WARNING: No themes found in database, skipping theme assignment"
fi
"""
        # Register backstage-fork as an OIDC application in Thunder.
        # Client credentials match the OpenBao seeds in prerequisites.py § 7a.
        if cfg.enable_flux or cfg.gitops_repo_url:
            thunder_bootstrap_scripts["61-backstage-fork-app.sh"] = f"""#!/bin/bash
set -e

THUNDER_URL="http://localhost:8090"

log_info "Checking if application 'Backstage Fork' already exists..."
existing_apps=$(curl -s --max-time 10 "${{THUNDER_URL}}/applications")

app_id=$(echo "$existing_apps" | tr '\\n' ' ' | sed 's/" *: *"/":"/g' \\
  | grep -o '"name":"Backstage Fork"[^}}]*"id":"[^"]*"\\|"id":"[^"]*"[^}}]*"name":"Backstage Fork"' \\
  | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

APP_PAYLOAD='{{
  "name": "Backstage Fork",
  "description": "OpenChoreo Portal (Company Fork)",
  "logo_url": "https://cdn.statically.io/gh/openchoreo/openchoreo.github.io@main/static/img/openchoreo-logo.png",
  "allowed_user_types": ["openchoreo-user"],
  "assertion": {{
    "validity_period": 3600
  }},
  "inbound_auth_config": [
    {{
      "type": "oauth2",
      "config": {{
        "client_id": "backstage-fork",
        "client_secret": "backstage-fork-client-secret",
        "redirect_uris": [
          "{cfg.backstage_fork_url}/api/auth/openchoreo-auth/handler/frame"
        ],
        "grant_types": [
          "authorization_code",
          "client_credentials",
          "refresh_token"
        ],
        "response_types": [
          "code"
        ],
        "token_endpoint_auth_method": "client_secret_post",
        "pkce_required": false,
        "public_client": false,
        "token": {{
          "access_token": {{
            "validity_period": 86400,
            "user_attributes": [
              "given_name",
              "family_name",
              "username",
              "groups"
            ]
          }},
          "id_token": {{
            "validity_period": 86400,
            "user_attributes": [
              "given_name",
              "family_name",
              "username",
              "groups"
            ]
          }}
        }},
        "scope_claims": {{
          "email": [
            "email"
          ],
          "groups": [
            "groups"
          ],
          "profile": [
            "username",
            "given_name",
            "family_name",
            "picture"
          ]
        }}
      }}
    }}
  ]
}}'

if [ -n "$app_id" ]; then
  log_info "Application 'Backstage Fork' already exists (id: $app_id), updating..."
  curl --location -X PUT "${{THUNDER_URL}}/applications/$app_id" \\
    --header 'Content-Type: application/json' \\
    --data "$APP_PAYLOAD" \\
    --fail-with-body \\
    --max-time 30 \\
    --retry 3 \\
    --retry-delay 5
  log_info "Application updated successfully"
else
  log_info "Application 'Backstage Fork' does not exist, creating..."
  curl --location "${{THUNDER_URL}}/applications" \\
    --header 'Content-Type: application/json' \\
    --data "$APP_PAYLOAD" \\
    --fail-with-body \\
    --max-time 30 \\
    --retry 3 \\
    --retry-delay 5
  log_info "Application created successfully"
fi
"""
        thunder_bootstrap_files = sorted(thunder_bootstrap_scripts)
        thunder_bootstrap_cm_name = "thunder-bootstrap-managed"
        thunder_values["bootstrap"] = {
            "configMap": {
                "name": thunder_bootstrap_cm_name,
                "files": thunder_bootstrap_files,
            }
        }

        thunder_bootstrap = k8s.core.v1.ConfigMap(
            "thunder-bootstrap-managed",
            metadata=k8s.meta.v1.ObjectMetaArgs(name=thunder_bootstrap_cm_name, namespace=NS_THUNDER),
            data=thunder_bootstrap_scripts,
            opts=self._child_opts(provider=k8s_provider, depends_on=[thunder_ns]),
        )

        # Use helm.v3.Release (not v4.Chart) because Thunder uses Helm lifecycle
        # hooks (pre-install ServiceAccount/Secret/PVC, post-install Job) that
        # k8s.helm.v4.Chart silently drops.
        thunder = k8s.helm.v3.Release(
            "thunder",
            k8s.helm.v3.ReleaseArgs(
                chart=cfg.thunder_chart,
                version=cfg.thunder_version,
                namespace=NS_THUNDER,
                values=thunder_values,
                timeout=TIMEOUT_DEFAULT,
                wait_for_jobs=True,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[thunder_bootstrap]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        wait_thunder = sleep("thunder", SLEEP_AFTER_THUNDER, opts=self._child_opts(depends_on=[thunder]))

        thunder_bootstrap_checksum = hashlib.sha256(
            json.dumps(thunder_bootstrap_scripts, sort_keys=True).encode("utf-8")
        ).hexdigest()
        thunder_security_context = thunder_values.get("deployment", {}).get("securityContext", {})
        thunder_image_pull_policy = thunder_values.get("deployment", {}).get("image", {}).get("pullPolicy", "Always")

        rerun_volume_mounts = [
            k8s.core.v1.VolumeMountArgs(
                name="bootstrap-scripts",
                mount_path=f"/opt/thunder/bootstrap/{filename}",
                sub_path=filename,
            )
            for filename in thunder_bootstrap_files
        ]

        thunder_setup_rerun = k8s.batch.v1.Job(
            "thunder-setup-rerun",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="thunder-setup-rerun",
                namespace=NS_THUNDER,
                annotations={"openchoreo.dev/bootstrap-checksum": thunder_bootstrap_checksum},
            ),
            spec=k8s.batch.v1.JobSpecArgs(
                backoff_limit=1,
                ttl_seconds_after_finished=3600,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(
                        annotations={"openchoreo.dev/bootstrap-checksum": thunder_bootstrap_checksum}
                    ),
                    spec=k8s.core.v1.PodSpecArgs(
                        service_account_name="thunder-service-account",
                        restart_policy="OnFailure",
                        security_context=k8s.core.v1.PodSecurityContextArgs(
                            run_as_user=thunder_security_context.get("runAsUser", 10001),
                            run_as_group=thunder_security_context.get("runAsGroup", 10001),
                            fs_group=thunder_security_context.get("fsGroup", 10001),
                        ),
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                name="setup",
                                image=_thunder_image(thunder_values, cfg.thunder_version),
                                image_pull_policy=thunder_image_pull_policy,
                                command=["./setup.sh"],
                                env=[
                                    k8s.core.v1.EnvVarArgs(
                                        name="DB_CONFIG_PASSWORD",
                                        value_from=k8s.core.v1.EnvVarSourceArgs(
                                            secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                                name="thunder-db-credentials",
                                                key="config-db-password",
                                            )
                                        ),
                                    ),
                                    k8s.core.v1.EnvVarArgs(
                                        name="DB_RUNTIME_PASSWORD",
                                        value_from=k8s.core.v1.EnvVarSourceArgs(
                                            secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                                name="thunder-db-credentials",
                                                key="runtime-db-password",
                                            )
                                        ),
                                    ),
                                    k8s.core.v1.EnvVarArgs(
                                        name="DB_USER_PASSWORD",
                                        value_from=k8s.core.v1.EnvVarSourceArgs(
                                            secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                                name="thunder-db-credentials",
                                                key="user-db-password",
                                            )
                                        ),
                                    ),
                                ],
                                security_context=k8s.core.v1.SecurityContextArgs(
                                    allow_privilege_escalation=False,
                                    read_only_root_filesystem=thunder_security_context.get(
                                        "readOnlyRootFilesystem", True
                                    ),
                                    run_as_non_root=True,
                                    run_as_user=thunder_security_context.get("runAsUser", 10001),
                                    capabilities=k8s.core.v1.CapabilitiesArgs(drop=["ALL"]),
                                ),
                                volume_mounts=[
                                    k8s.core.v1.VolumeMountArgs(
                                        name="database-storage",
                                        mount_path="/opt/thunder/repository/database",
                                    ),
                                    k8s.core.v1.VolumeMountArgs(
                                        name="deployment-yaml-volume",
                                        mount_path="/opt/thunder/repository/conf/deployment.yaml",
                                        sub_path="deployment.yaml",
                                    ),
                                    *rerun_volume_mounts,
                                ],
                            )
                        ],
                        volumes=[
                            k8s.core.v1.VolumeArgs(
                                name="database-storage",
                                persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                                    claim_name="thunder-database-pvc"
                                ),
                            ),
                            k8s.core.v1.VolumeArgs(
                                name="deployment-yaml-volume",
                                config_map=k8s.core.v1.ConfigMapVolumeSourceArgs(name="thunder-setup-config-map"),
                            ),
                            k8s.core.v1.VolumeArgs(
                                name="bootstrap-scripts",
                                config_map=k8s.core.v1.ConfigMapVolumeSourceArgs(
                                    name=thunder_bootstrap_cm_name,
                                    default_mode=0o755,
                                ),
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[wait_thunder]),
                pulumi.ResourceOptions(
                    delete_before_replace=True,
                    replace_on_changes=["metadata.annotations", "spec"],
                    custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s"),
                ),
            ),
        )

        # ─── 2. Backstage ExternalSecret ───
        backstage_es = k8s.apiextensions.CustomResource(
            "backstage-external-secret",
            api_version="external-secrets.io/v1",
            kind="ExternalSecret",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=SECRET_BACKSTAGE,
                namespace=NS_CONTROL_PLANE,
            ),
            spec={
                "refreshInterval": "1h",
                "secretStoreRef": {"kind": "ClusterSecretStore", "name": CLUSTER_SECRET_STORE_NAME},
                "target": {"name": SECRET_BACKSTAGE},
                "data": [
                    {
                        "secretKey": "backend-secret",
                        "remoteRef": {"key": "backstage-backend-secret", "property": "value"},
                    },
                    {
                        "secretKey": "client-secret",
                        "remoteRef": {"key": "backstage-client-secret", "property": "value"},
                    },
                    {
                        "secretKey": "jenkins-api-key",
                        "remoteRef": {"key": "backstage-jenkins-api-key", "property": "value"},
                    },
                ],
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[wait_thunder]),
        )

        wait_eso_sync = sleep(
            "eso-sync",
            SLEEP_AFTER_ESO_SYNC,
            opts=self._child_opts(depends_on=[backstage_es, thunder_setup_rerun]),
        )

        # ─── 3. OpenChoreo Control Plane Helm Chart ───
        # Use helm.v3.Release (not v4.Chart) because the chart contains
        # cert-manager Certificate resources; v4.Chart does client-side rendering
        # that fails if cert-manager CRDs are not yet installed.
        cp_chart = k8s.helm.v3.Release(
            NS_CONTROL_PLANE,
            k8s.helm.v3.ReleaseArgs(
                chart=cfg.cp_chart,
                version=cfg.openchoreo_version,
                namespace=NS_CONTROL_PLANE,
                values=cp_values(
                    domain_base=cfg.domain_base,
                    scheme=cfg.scheme,
                    cp_port=cfg.cp_port,
                    tls_enabled=cfg.tls_enabled,
                    thunder_url=cfg.thunder_url,
                    backstage_url=cfg.backstage_url,
                    api_url=cfg.api_url,
                ),
                timeout=TIMEOUT_DEFAULT,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[wait_eso_sync]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        # ─── 4. Patch Workflow CRDs (k3d → internal endpoints) ───
        # The control-plane chart creates Workflow CRDs with k3d-specific
        # hostnames (host.k3d.internal) that don't resolve on non-k3d clusters.
        # Patch them to use cluster-internal service DNS names.
        # Only needed when workflow_template_mode is k3d-patch.
        registry_endpoint = f"registry.{NS_WORKFLOW_PLANE}.svc.cluster.local:{cfg.wp_registry_port}"
        if cfg.platform.workflow_template_mode == "k3d-patch":
            patch_workflows = command.local.Command(
                "patch-workflow-crds",
                create=(
                    f"OBJS=$(kubectl get workflow.openchoreo.dev --all-namespaces -o yaml"
                    f" --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} 2>/dev/null);"
                    f" if echo \"$OBJS\" | grep -q 'host.k3d.internal'; then"
                    f" echo \"$OBJS\" | sed 's|host.k3d.internal:10082|{registry_endpoint}|g'"
                    f" | kubectl apply --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} -f -;"
                    f" else echo 'No k3d-specific workflow CRDs to patch'; fi"
                ),
                opts=self._child_opts(depends_on=[cp_chart]),
            )
        else:
            patch_workflows = cp_chart  # no patching needed

        # ─── 5. Label namespace ───
        label_ns = LabelNamespace(
            "label-cp-namespace",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            namespace=NS_CONTROL_PLANE,
            labels={"openchoreo.dev/control-plane": "true"},
            opts=self._child_opts(depends_on=[cp_chart, patch_workflows]),
        )

        self.result = ControlPlaneResult(helm_chart=cp_chart, label_ns=label_ns)
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
    depends: list[pulumi.Resource],
) -> ControlPlaneResult:
    """Deploy Thunder IdP, backstage secrets, and the control plane chart."""
    return ControlPlane(
        "control-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
