"""OpenBao Helm values builder."""

from __future__ import annotations


def get_values(openbao_root_token: str, opensearch_username: str, opensearch_password: str) -> dict:
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
                _post_start_script(openbao_root_token, opensearch_username, opensearch_password),
            ],
        },
    }


def _post_start_script(token: str, os_user: str, os_pass: str) -> str:
    return f"""\
sleep 5
export BAO_ADDR=http://127.0.0.1:8200
export BAO_TOKEN={token}

bao auth enable kubernetes 2>/dev/null || true
bao write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

bao policy write openchoreo-secret-reader-policy - <<POLICY
path "secret/data/*" {{ capabilities = ["read"] }}
path "secret/metadata/*" {{ capabilities = ["list", "read"] }}
POLICY

bao policy write openchoreo-secret-writer-policy - <<POLICY
path "secret/data/*" {{ capabilities = ["create", "read", "update", "delete"] }}
path "secret/metadata/*" {{ capabilities = ["create", "read", "update", "delete", "list"] }}
POLICY

bao write auth/kubernetes/role/openchoreo-secret-reader-role \
  bound_service_account_names=default \
  bound_service_account_namespaces="dp*" \
  policies=openchoreo-secret-reader-policy ttl=20m

bao write auth/kubernetes/role/openchoreo-secret-writer-role \
  bound_service_account_names="*" \
  bound_service_account_namespaces="openbao,openchoreo-workflow-plane" \
  policies=openchoreo-secret-writer-policy ttl=20m

bao kv put secret/npm-token value="fake-npm-token-for-development"
bao kv put secret/docker-username value="dev-user"
bao kv put secret/docker-password value="dev-password"
bao kv put secret/github-pat value="fake-github-token-for-development"
bao kv put secret/git-token git-token="fake-github-token-for-development"
bao kv put secret/gitops-token git-token="fake-github-token-for-development"
bao kv put secret/username value="dev-user"
bao kv put secret/password value="dev-password"

bao kv put secret/backstage-backend-secret value="local-dev-backend-secret"
bao kv put secret/backstage-client-secret value="backstage-portal-secret"
bao kv put secret/backstage-jenkins-api-key value="placeholder-not-in-use"
bao kv put secret/observer-oauth-client-secret value="openchoreo-observer-resource-reader-client-secret"
bao kv put secret/rca-oauth-client-secret value="openchoreo-rca-agent-secret"
bao kv put secret/opensearch-username value="{os_user}"
bao kv put secret/opensearch-password value="{os_pass}"
"""
