sleep 5
export BAO_ADDR=http://127.0.0.1:8200
export BAO_TOKEN=$token

bao auth enable kubernetes 2>/dev/null || true
bao write auth/kubernetes/config \
  kubernetes_host="https://$$KUBERNETES_PORT_443_TCP_ADDR:443"

bao policy write openchoreo-secret-reader-policy - <<POLICY
path "secret/data/*" { capabilities = ["read"] }
path "secret/metadata/*" { capabilities = ["list", "read"] }
POLICY

bao policy write openchoreo-secret-writer-policy - <<POLICY
path "secret/data/*" { capabilities = ["create", "read", "update", "delete"] }
path "secret/metadata/*" { capabilities = ["create", "read", "update", "delete", "list"] }
POLICY

bao write auth/kubernetes/role/openchoreo-secret-reader-role \
  bound_service_account_names=default \
  bound_service_account_namespaces="dp*" \
  policies=openchoreo-secret-reader-policy ttl=20m

bao write auth/kubernetes/role/openchoreo-secret-writer-role \
  bound_service_account_names="*" \
  bound_service_account_namespaces="openbao,openchoreo-workflow-plane" \
  policies=openchoreo-secret-writer-policy ttl=20m

$dev_secrets_block
