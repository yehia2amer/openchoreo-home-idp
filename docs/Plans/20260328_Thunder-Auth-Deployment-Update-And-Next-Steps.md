# Plan: Thunder Auth Deployment Update and Next Steps

**Date:** 2026-03-28  
**Scope:** Save the deployed auth-only fix for the Rancher Desktop + Cilium setup, record why the first rollout was insufficient, and capture the remaining follow-up work.  
**Status:** FIX DEPLOYED, RUNTIME VERIFIED, BROWSER SIGN-IN VALIDATION PENDING

---

## 1. Current Result

The auth-only fix is now deployed to the `rancher-desktop` Pulumi stack.

The original source-level change removed the non-upstream Backstage callback mutation that appended `?env=development`. That change alone was not enough for an existing cluster, because the Thunder chart uses hook-managed bootstrap resources that are not refreshed on a normal Helm upgrade.

The final deployed fix does two things:

- keeps the corrected Backstage callback path in Pulumi-generated values
- manages Thunder bootstrap scripts through a normal Kubernetes ConfigMap and reruns Thunder setup when bootstrap content changes

---

## 2. Root Cause

The root cause was not Cilium and not the basic OIDC endpoint wiring alone.

The actual issue was deployment lifecycle behavior in the Thunder chart:

- Thunder bootstrap scripts are installed through pre-install hook resources
- the original stale bootstrap ConfigMap in the cluster still contained `http://openchoreo.localhost:8080/api/auth/openchoreo-auth/handler/frame?env=development`
- after the Pulumi source fix, Helm upgrade did not replace that hook-created ConfigMap or rerun setup automatically
- therefore the live Thunder Backstage application registration remained stale even though the Pulumi code was corrected

---

## 3. Code Changes Applied

### Auth callback correction

The following Pulumi logic now produces the plain Backstage callback path without the development query suffix:

- `pulumi/values/control_plane.py`
- `pulumi/components/control_plane.py`

### Bootstrap refresh mechanism

The control plane component was extended so that Thunder bootstrap changes are applied on upgrades:

- create a managed ConfigMap: `thunder-bootstrap-managed`
- point the Thunder release at that managed ConfigMap
- create a one-shot Job: `thunder-setup-rerun`
- trigger that job when the bootstrap script checksum changes

This closes the gap between corrected source values and the live Thunder application registration.

---

## 4. Deployment Outcome

The final Pulumi apply completed successfully.

### Verified results

- `pulumi up -s rancher-desktop --yes` succeeded
- Thunder setup rerun job completed successfully
- control-plane and Thunder workloads remained healthy
- Pulumi integration tests passed during the update

### Live cluster verification

Verified in the cluster after the final apply:

- managed ConfigMap `thunder-bootstrap-managed` contains:
  - `http://openchoreo.localhost:8080/api/auth/openchoreo-auth/handler/frame`
- rerun job logs show that the existing Backstage application was updated in Thunder
- the live Backstage application registration now contains:
  - `redirect_uris: ["http://openchoreo.localhost:8080/api/auth/openchoreo-auth/handler/frame"]`

Important note:

- the old hook-created ConfigMap `thunder-bootstrap` still exists and still shows the stale `?env=development` value
- that is now an inactive leftover artifact, not the active bootstrap source used by the managed rerun flow

---

## 5. What Still Needs To Be Done

### Step 1: Browser sign-in validation

Run the real end-user validation path:

- open `http://openchoreo.localhost:8080`
- click sign in
- complete Thunder login with a bootstrapped user
- confirm return to the console with an authenticated session

This is the main remaining verification step.

### Step 2: Optional cleanup of stale Thunder hook artifacts

Decide whether to leave or clean up the old hook-era bootstrap artifact:

- stale ConfigMap: `thunder-bootstrap`

It is not required for correctness now, but removing or documenting it would reduce future confusion during debugging.

### Step 3: Optional hardening

If this pattern will be reused, keep the managed bootstrap plus rerun-job approach as the standard path for any future Thunder bootstrap change, especially:

- callback URI changes
- client registration changes
- default application updates

---

## 6. Bottom Line

The auth-only fix for the Rancher Desktop + Cilium setup is saved and deployed.

The live Thunder Backstage OAuth client now uses the correct callback path with no `?env=development` suffix.

The only meaningful remaining work is end-to-end browser sign-in validation, plus optional cleanup of stale hook-era resources.