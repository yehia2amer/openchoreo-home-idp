# pyright: reportMissingImports=false

from __future__ import annotations

import hashlib
import json
import urllib.request

import pulumi
import pulumi_kubernetes as k8s
import yaml

from config import NS_THUNDER, SLEEP_AFTER_THUNDER, TIMEOUT_DEFAULT, OpenChoreoConfig
from helpers.wait import sleep


def _fetch_yaml(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return yaml.safe_load(resp.read())


def _thunder_image(values: dict, default_tag: str) -> str:
    image = values.get("deployment", {}).get("image", {})
    registry = image.get("registry", "ghcr.io/asgardeo")
    repository = image.get("repository", "thunder")
    digest = image.get("digest")
    if digest:
        return f"{registry}/{repository}@{digest}"
    return f"{registry}/{repository}:{image.get('tag', default_tag)}"


class ThunderResult:
    def __init__(self, thunder: k8s.helm.v3.Release, wait_thunder: pulumi.Resource):
        self.thunder = thunder
        self.wait_thunder = wait_thunder


class Thunder(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:Thunder", name, {}, opts)

        thunder_ns = k8s.core.v1.Namespace(
            NS_THUNDER,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_THUNDER),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends or []),
        )

        thunder_values = _fetch_yaml(cfg.thunder_values_url)
        thunder_values.setdefault("thunderServer", {})["publicUrl"] = cfg.thunder_url

        thunder_host = f"thunder.{cfg.domain_base}"
        thunder_values.setdefault("httproute", {})["hostnames"] = [thunder_host]
        thunder_config = thunder_values.setdefault("configuration", {})
        thunder_config.setdefault("server", {})["publicUrl"] = cfg.thunder_url
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
        for script_name, script_body in thunder_bootstrap_scripts.items():
            thunder_bootstrap_scripts[script_name] = script_body.replace(
                "http://openchoreo.localhost:8080", cfg.backstage_url
            ).replace("http://thunder.openchoreo.localhost:8080", cfg.thunder_url)

        thunder_bootstrap_scripts["99-assign-themes.sh"] = """#!/bin/bash
set -e

DB="/opt/thunder/repository/database/configdb.db"

log_info "Assigning default theme to applications..."

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

        if cfg.enable_flux or cfg.gitops_repo_url:
            thunder_bootstrap_scripts["61-backstage-fork-app.sh"] = f"""#!/bin/bash
set -e

THUNDER_URL="http://localhost:8090"

log_info "Checking if application 'Backstage Fork' already exists..."
existing_apps=$(curl -s --max-time 10 "${{THUNDER_URL}}/applications")

app_id=$(echo "$existing_apps" | tr '\n' ' ' | sed 's/" *: *"/":"/g' \
  | grep -o '"name":"Backstage Fork"[^}}]*"id":"[^"]*"\\|"id":"[^"]*"[^}}]*"name":"Backstage Fork"' \
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
  curl --location -X PUT "${{THUNDER_URL}}/applications/$app_id" \
    --header 'Content-Type: application/json' \
    --data "$APP_PAYLOAD" \
    --fail-with-body \
    --max-time 30 \
    --retry 3 \
    --retry-delay 5
  log_info "Application updated successfully"
else
  log_info "Application 'Backstage Fork' does not exist, creating..."
  curl --location "${{THUNDER_URL}}/applications" \
    --header 'Content-Type: application/json' \
    --data "$APP_PAYLOAD" \
    --fail-with-body \
    --max-time 30 \
    --retry 3 \
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

        thunder = k8s.helm.v3.Release(
            "thunder",
            k8s.helm.v3.ReleaseArgs(
                name="thunder",
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

        k8s.batch.v1.Job(
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

        self.result = ThunderResult(thunder=thunder, wait_thunder=wait_thunder)
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
    depends: list[pulumi.Resource] | None = None,
) -> ThunderResult:
    return Thunder(
        "thunder",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
