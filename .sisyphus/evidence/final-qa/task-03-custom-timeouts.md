# Task 3: CustomTimeouts on Helm Chart/Release resources

## Scenarios

### 3.1 prerequisites.py — All v4.Chart resources have CustomTimeouts
- **cert-manager** (line 97): `custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")`
- **external-secrets** (line 119): `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")`
- **kgateway-crds** (line 146): `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")`
- **kgateway** (line 184): `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")`
- **openbao** (line 211): `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")`
- **Result**: PASS

### 3.2 workflow_plane.py — Helm resources have CustomTimeouts
- **docker-registry v4.Chart** (line 63): `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")`
- **WP helm.v3.Release** (line 91): `custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")`
- **Result**: PASS

### 3.3 data_plane.py — Helm resources have CustomTimeouts
- **dp_chart helm.v3.Release** (line 103): `custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")`
- **Result**: PASS

### 3.4 observability_plane.py — All 4 helm.v3.Release resources have CustomTimeouts
- Lines 149, 169, 188, 213: All have `custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")`
- **Result**: PASS

### 3.5 flux_gitops.py — No Helm Chart resources
- Uses `yaml.v2.ConfigGroup` for Flux install and `CustomResource` for kustomizations
- No Helm charts that need timeouts — Task 3 does not apply
- **Result**: N/A (correctly no changes needed)

## Verdict: 4/4 PASS (1 N/A)
