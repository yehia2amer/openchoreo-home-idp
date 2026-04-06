"""OpenBao Helm values builder."""

from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Any


def get_values(
    openbao_root_token: str,
    opensearch_username: str,
    opensearch_password: str,
    is_dev_stack: bool,
) -> dict[str, Any]:
    """Return Helm values for the OpenBao chart (dev mode with postStart seed)."""
    return {
        "injector": {"enabled": False},
        "server": {
            "dev": {
                "enabled": True,
                "devRootToken": openbao_root_token,
            },
            "postStart": [
                "/bin/sh",
                "-c",
                _post_start_script(
                    openbao_root_token,
                    opensearch_username,
                    opensearch_password,
                    is_dev_stack=is_dev_stack,
                ),
            ],
        },
    }


def _post_start_script(token: str, os_user: str, os_pass: str, *, is_dev_stack: bool) -> str:
    template_path = Path(__file__).resolve().parent.parent / "templates" / "openbao_post_start.sh.tpl"
    tpl = Template(template_path.read_text())

    dev_secrets_block = ""
    if is_dev_stack:
        dev_secrets_block = (
            'bao kv put secret/npm-token value="fake-npm-token-for-development"\n'
            'bao kv put secret/docker-username value="dev-user"\n'
            'bao kv put secret/docker-password value="dev-password"\n'
            'bao kv put secret/github-pat value="fake-github-token-for-development"\n'
            'bao kv put secret/git-token git-token="fake-github-token-for-development"\n'
            'bao kv put secret/gitops-token git-token="fake-github-token-for-development"\n'
            'bao kv put secret/username value="dev-user"\n'
            'bao kv put secret/password value="dev-password"\n'
            "\n"
            'bao kv put secret/backstage-backend-secret value="local-dev-backend-secret"\n'
            'bao kv put secret/backstage-client-secret value="backstage-portal-secret"\n'
            'bao kv put secret/backstage-jenkins-api-key value="placeholder-not-in-use"\n'
            'bao kv put secret/observer-oauth-client-secret value="openchoreo-observer-resource-reader-client-secret"\n'
            'bao kv put secret/rca-oauth-client-secret value="openchoreo-rca-agent-secret"\n'
            'bao kv put secret/rca-llm-api-key value="REPLACE_WITH_YOUR_LLM_API_KEY"\n'
            f'bao kv put secret/opensearch-username value="{os_user}"\n'
            f'bao kv put secret/opensearch-password value="{os_pass}"\n'
            "\n"
            "# ── DNS / Gateway secrets (sf8.5) ──\n"
            "# Cloudflare DNS API token\n"
            'bao kv put secret/apps/external-dns/cloudflare api-token="cfut_uaRooKcWkb77Ygz9CNr7KXwsNnJCiNUALAe5RULDcfd4b1b7"\n'
            "# AdGuard Home on TrueNAS\n"
            "bao kv put secret/apps/external-dns/adguard-truenas"
            " url='http://192.168.0.129:3000'"
            " user='yehia'"
            " password='t9QVO!wg$C7$1dAHZ@%j6HH'\n"
            "# AdGuard Home on K8s — deployed by sf8.10\n"
            "bao kv put secret/apps/external-dns/adguard-k8s"
            ' url="http://adguard-home-k8s.external-dns.svc.cluster.local:3000"'
            ' user="admin"'
            ' password="pI03loPa6Nhlele"\n'
            "# Keepalived VRRP auth password\n"
            'bao kv put secret/apps/external-dns/keepalived auth-pass="HHsiI0T7"\n'
        )

    return tpl.substitute(token=token, dev_secrets_block=dev_secrets_block)
