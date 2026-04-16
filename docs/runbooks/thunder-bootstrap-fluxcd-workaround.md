# Thunder Bootstrap Issue: FluxCD Does Not Execute Helm Hooks

## TL;DR

When Thunder is deployed via FluxCD HelmRelease, the `pre-install` Helm hook (setup job) is **NOT executed**. This means the SQLite databases are initialized with empty tables but NO bootstrap data (OAuth apps, users, groups, schemas) is registered. Result: all OAuth flows fail with `server_error: Failed to process authorization request` or `invalid_request: Invalid client_id`.

**This happens on EVERY new environment deployment via FluxCD.**

---

## Symptoms

| What you see | What it means |
|---|---|
| Backstage login redirects to Thunder but Thunder returns `server_error` at `/oauth2/authorize` | The `APP_OAUTH_INBOUND_CONFIG` table exists but has no custom apps |
| Thunder gate shows error page with `errorCode=server_error&errorMessage=Failed+to+process+authorization+request` | Same — no OAuth app registered for the `client_id` |
| After manual app registration, error changes to `invalid_request: Invalid client_id` | Client was registered with wrong `client_id` or registration didn't persist |
| SQLite DB files exist on PVC but only have 3 default apps (`CONSOLE`, `REACT_SDK_SAMPLE`, `sample_app_client`) | Bootstrap scripts never ran |
| Thunder pod runs fine, health checks pass, logs show no errors | Thunder itself is healthy — it's just missing configuration data |

---

## Root Cause

Thunder's Helm chart (v0.28.0, `oci://ghcr.io/asgardeo/helm-charts/thunder`) uses a setup Job with `helm.sh/hook: pre-install` annotation in `templates/setup-job.yaml`. This Job:

1. Runs an `init-database` initContainer that copies SQLite DB seed files from the image to the PVC
2. Starts Thunder with `THUNDER_SKIP_SECURITY=true` (no auth required on any endpoint)
3. Executes all bootstrap scripts from `/opt/thunder/bootstrap/` directory
4. Registers OAuth apps, users, groups, schemas via Thunder's REST API on `http://localhost:8090`
5. Stops Thunder and exits

**FluxCD's Helm controller does NOT execute Helm hooks** (`pre-install`, `post-install`, etc.). This is by design — see [FluxCD docs on hooks](https://fluxcd.io/flux/components/helm/helmreleases/#hooks). So the setup Job never runs, and the bootstrap data is never created.

### Secondary Issue: Flux Variable Substitution Breaks Shell Scripts

The bootstrap scripts in the ConfigMap use `$${VAR}` (Flux escaping) intended to produce `${VAR}` (shell variables) after Flux processing. However, Flux's `postBuild.substituteFrom` substitutes ALL `${...}` patterns — including ones inside Helm values that become ConfigMap data. Shell variables like `${group_name}`, `${app_id}`, etc. get replaced with empty strings, breaking the scripts even if you run them manually from the rendered ConfigMap.

---

## Affected Components

| Component | Details |
|---|---|
| **Thunder Helm chart** | v0.28.0 (`oci://ghcr.io/asgardeo/helm-charts/thunder`) |
| **Setup Job template** | `templates/setup-job.yaml` (annotation: `helm.sh/hook: pre-install`) |
| **Bootstrap ConfigMap** | `thunder-bootstrap` (rendered from `bootstrap.configMap` Helm values) |
| **Setup ConfigMap** | `thunder-setup-config-map` (contains `deployment.yaml`) |
| **PVC** | `thunder-database-pvc` (SQLite DB storage, ReadWriteOnce) |
| **Deployment security context** | `runAsUser: 10001, runAsGroup: 10001, fsGroup: 10001` |

---

## Manual Fix Steps (Proven — Used on Every Environment)

### Prerequisites

```bash
# Set your kubectl context
export CTX="gke_pg-ae-n-app-173978_europe-west1_openchoreo-gke"

# Set your environment's URLs
export BACKSTAGE_REDIRECT_URI="https://backstage.idp.aistudio.consulting/api/auth/openchoreo-auth/handler/frame"
```

### Step 1: Scale Down Thunder

The PVC is ReadWriteOnce — only one pod can mount it at a time.

```bash
kubectl scale deployment thunder-deployment -n thunder --replicas=0 --context $CTX
sleep 10
# Verify no pods running
kubectl get pods -n thunder --context $CTX
```

### Step 2: Run One-Off Setup Pod

This pod starts Thunder with security disabled, registers the Backstage OAuth app via localhost, then exits. We inline the curl calls because the bootstrap ConfigMap has broken Flux variable substitution.

```bash
cat <<EOFPOD | kubectl apply -n thunder --context $CTX -f -
apiVersion: v1
kind: Pod
metadata:
  name: thunder-setup-job
  namespace: thunder
spec:
  restartPolicy: Never
  securityContext:
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
  containers:
  - name: setup
    image: ghcr.io/asgardeo/thunder:0.28.0
    command: ["/bin/bash", "-c"]
    args:
    - |
      set -e
      export THUNDER_SKIP_SECURITY=true
      cd /opt/thunder
      ./thunder &
      THUNDER_PID=\$!

      echo "Waiting for Thunder to start..."
      for i in \$(seq 1 60); do
        if curl -s http://localhost:8090/health/readiness > /dev/null 2>&1; then
          echo "Thunder is ready!"
          break
        fi
        sleep 1
      done

      T="http://localhost:8090"

      echo "=== Registering Backstage OAuth app ==="
      curl -s "\$T/applications" \\
        -H 'Content-Type: application/json' \\
        --data '{
          "name": "Backstage",
          "description": "OpenChoreo Backstage Portal",
          "allowed_user_types": ["openchoreo-user"],
          "inbound_auth_config": [{
            "type": "oauth2",
            "config": {
              "client_id": "openchoreo-backstage-client",
              "client_secret": "backstage-portal-secret",
              "redirect_uris": ["${BACKSTAGE_REDIRECT_URI}"],
              "grant_types": ["authorization_code", "client_credentials", "refresh_token"],
              "response_types": ["code"],
              "token_endpoint_auth_method": "client_secret_post",
              "pkce_required": false,
              "public_client": false,
              "token": {
                "access_token": {"expiry_time": 3600, "binding_type": "certificate"},
                "id_token": {"expiry_time": 3600, "audiences": ["openchoreo-backstage-client"]}
              }
            }
          }]
        }'
      echo ""

      echo "=== Verify registered apps ==="
      curl -s "\$T/applications" | grep -o '"client_id":"[^"]*"'

      kill \$THUNDER_PID 2>/dev/null
      wait \$THUNDER_PID 2>/dev/null || true
      echo "Done!"
    env:
    - name: THUNDER_SKIP_SECURITY
      value: "true"
    volumeMounts:
    - name: database-storage
      mountPath: /opt/thunder/repository/database
    - name: setup-config
      mountPath: /opt/thunder/repository/conf/deployment.yaml
      subPath: deployment.yaml
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
  volumes:
  - name: database-storage
    persistentVolumeClaim:
      claimName: thunder-database-pvc
  - name: setup-config
    configMap:
      name: thunder-setup-config-map
EOFPOD
```

### Step 3: Wait for Completion and Verify

```bash
# Watch the pod until it completes
kubectl logs thunder-setup-job -n thunder --context $CTX -f

# Should see:
# Thunder is ready!
# === Registering Backstage OAuth app ===
# {"id":"...","name":"Backstage","client_id":"openchoreo-backstage-client",...}
# === Verify registered apps ===
# "client_id":"openchoreo-backstage-client"
# Done!
```

### Step 4: Clean Up and Scale Back Up

```bash
kubectl delete pod thunder-setup-job -n thunder --context $CTX
kubectl scale deployment thunder-deployment -n thunder --replicas=1 --context $CTX
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=thunder -n thunder --timeout=60s --context $CTX
```

### Step 5: Verify OAuth Flow

```bash
curl -sk -D- -o /dev/null \
  "https://thunder.idp.aistudio.consulting/oauth2/authorize?response_type=code&redirect_uri=https://backstage.idp.aistudio.consulting/api/auth/openchoreo-auth/handler/frame&scope=openid+profile+email&state=test&client_id=openchoreo-backstage-client"

# ✅ Expected: HTTP/2 302, Location: .../gate/signin?applicationId=...
# ❌ Bad:     errorCode=server_error or errorCode=invalid_request
```

---

## Key Gotchas

1. **Security context MUST be `10001`**: The Thunder deployment uses `runAsUser: 10001, runAsGroup: 10001, fsGroup: 10001`. Using the wrong UID (e.g., 802 which is the `thunder` user in the base image) causes `permission denied` on `/opt/thunder/repository/resources/security/signing.key`.

2. **PVC is ReadWriteOnce**: Only one pod can mount it at a time — you MUST scale Thunder down before running the setup pod, or you'll get a mount conflict.

3. **Flux `$${}` escaping is broken in Helm values**: Shell variables like `${group_name}` inside bootstrap scripts get substituted by Flux even when escaped as `$${group_name}`. This is because the scripts live inside a Helm values ConfigMap processed by Flux Kustomization `postBuild.substituteFrom`. The escaping only works at the top level, not inside nested values.

4. **Thunder only listens on port 8090**: There is no separate admin port. When `THUNDER_SKIP_SECURITY=true`, all endpoints (including `/applications`, `/users`, etc.) are accessible without auth on 8090.

5. **DB files exist but apps aren't registered**: The initContainer copies seed SQLite files from the image which contain table schemas and 3 default apps (CONSOLE, REACT_SDK_SAMPLE, sample_app_client). Custom OpenChoreo apps come from the bootstrap scripts which never ran.

6. **The `setup.sh` in the image handles everything**: You don't need to write custom init logic — `./setup.sh` from the Thunder image orchestrates starting Thunder, running bootstrap scripts, and shutting down. The issue is that the bootstrap scripts ConfigMap has broken URLs (external HTTPS instead of localhost HTTP).

7. **If PVC is deleted/recreated, ALL data is lost**: The setup must run again from scratch. This includes all users, groups, OAuth apps, and configuration.

---

## Quick Diagnostic Commands

```bash
# Check if custom OAuth apps exist in the DB
kubectl exec -n thunder deployment/thunder-deployment --context $CTX -- \
  sqlite3 /opt/thunder/repository/database/configdb.db \
  "SELECT CLIENT_ID FROM APP_OAUTH_INBOUND_CONFIG;"
# Expected: openchoreo-backstage-client (plus defaults)
# Bad: only CONSOLE, REACT_SDK_SAMPLE, sample_app_client

# Check DB file sizes (should be >50KB each after bootstrap)
kubectl exec -n thunder deployment/thunder-deployment --context $CTX -- \
  ls -la /opt/thunder/repository/database/
# configdb.db should be ~900KB+ after bootstrap (vs ~266KB before)

# Test OAuth authorize flow directly
curl -sk -D- -o /dev/null \
  "https://thunder.idp.aistudio.consulting/oauth2/authorize?response_type=code&redirect_uri=https://backstage.idp.aistudio.consulting/api/auth/openchoreo-auth/handler/frame&scope=openid+profile+email&state=test&client_id=openchoreo-backstage-client"

# Check Thunder logs for auth errors
kubectl logs -n thunder deployment/thunder-deployment --context $CTX --tail=50 | grep -i error
```

---

## Automation Approaches

### Short-Term: Script It (Current Approach)

Create a shell script that wraps the manual steps above. Run it after every `flux reconcile` or new environment deployment:

```bash
#!/bin/bash
# scripts/thunder-bootstrap.sh
# Run after FluxCD deploys Thunder to register OAuth apps
set -e
CTX="${1:?Usage: $0 <kubectl-context> <backstage-redirect-uri>}"
REDIRECT_URI="${2:?Usage: $0 <kubectl-context> <backstage-redirect-uri>}"
# ... (steps 1-5 from above)
```

### Medium-Term: initContainer in the Thunder Deployment (Recommended)

Add an initContainer to the Thunder HelmRelease via `spec.postRenderers` that runs the bootstrap before the main container starts:

```yaml
# In thunder/helmrelease.yaml spec.postRenderers
- kustomize:
    patches:
    - target:
        kind: Deployment
        name: thunder-deployment
      patch: |
        - op: add
          path: /spec/template/spec/initContainers/-
          value:
            name: bootstrap
            image: ghcr.io/asgardeo/thunder:0.28.0
            command: ["./setup.sh"]
            env:
            - name: THUNDER_SKIP_SECURITY
              value: "true"
            securityContext:
              runAsUser: 10001
              runAsGroup: 10001
            volumeMounts:
            - name: database-storage
              mountPath: /opt/thunder/repository/database
            - name: bootstrap-scripts-local
              mountPath: /opt/thunder/bootstrap
            - name: deployment-yaml-volume
              mountPath: /opt/thunder/repository/conf/deployment.yaml
              subPath: deployment.yaml
```

**Why this is the best medium-term approach:**
- Runs before Thunder starts (PVC is available, no mount conflict)
- Uses `THUNDER_SKIP_SECURITY=true` (no auth needed)
- Runs on every pod restart (bootstrap scripts are idempotent — they check "already exists")
- No separate Job management needed
- No manual intervention required

**Challenge to solve**: The bootstrap scripts ConfigMap has broken Flux `$${}` escaping. Need a separate ConfigMap with localhost URLs hardcoded, or encode the scripts differently.

### Long-Term Production Solution

The proper production-grade fix has three parts:

#### 1. Use PostgreSQL Instead of SQLite

SQLite on a PVC is not production-grade:
- Single-writer (no concurrent access)
- No HA/replication
- PVC lock contention prevents running setup while Thunder is up
- Data loss if PVC is deleted

Thunder supports PostgreSQL via `configuration.database.config.type: postgres`. With PostgreSQL:
- Bootstrap data persists independently of pod lifecycle
- Multiple Thunder replicas can run simultaneously
- Standard backup/restore procedures apply
- No PVC mount conflicts

#### 2. Upstream PR to Thunder Helm Chart

Contribute a PR to [asgardeo/thunder](https://github.com/asgardeo/thunder) that adds a `setup.mode` Helm value:
- `setup.mode: hook` (default, current behavior — Helm `pre-install` hook)
- `setup.mode: initContainer` — moves setup logic into an initContainer on the Deployment
- `setup.mode: job` — creates a standalone Job resource (no Helm hook annotation)

This would make Thunder natively compatible with FluxCD and ArgoCD (which also skips hooks by default).

#### 3. Fix Flux Variable Substitution in Shell Scripts

Options (pick one):
- **Base64-encode scripts** in the ConfigMap to prevent Flux from seeing `${...}` patterns
- **Use a separate Kustomization** for the bootstrap ConfigMap that has NO `postBuild.substituteFrom`
- **Move bootstrap scripts into a container image** — build a custom image that embeds the scripts with correct localhost URLs
- **Use `envsubst`-style templating** instead of Flux substitution for scripts that contain shell variables

---

## Environment-Specific Redirect URIs

Each environment needs different redirect URIs in the Backstage OAuth app registration:

| Environment | Redirect URI |
|---|---|
| GKE | `https://backstage.idp.aistudio.consulting/api/auth/openchoreo-auth/handler/frame` |
| Baremetal | `https://backstage.amernas.work/api/auth/openchoreo-auth/handler/frame` |
| k3d local | `https://openchoreo.local:8443/api/auth/openchoreo-auth/handler/frame` |

Update the `redirect_uris` array in the setup pod's curl payload accordingly.

---

## Timeline

| When | What | Effort |
|---|---|---|
| **Now** | Run manual setup pod after each deployment | 5 min per environment |
| **Next sprint** | Add initContainer to HelmRelease via postRenderers | 1-2 days |
| **Next quarter** | Migrate to PostgreSQL + upstream PR | 1-2 weeks |
