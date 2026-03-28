# Report: OpenChoreo Current Status and Thunder Auth Remediation Plan

**Date:** 2026-03-27  
**Scope:** Rancher Desktop deployment status, browser reachability, Thunder authentication findings, and next remediation steps  
**Status:** IN PROGRESS

---

## 1. Executive Summary

The OpenChoreo deployment is now functionally up on Rancher Desktop for day-to-day platform access and service verification. The infrastructure and networking blockers that previously prevented browser access have been resolved. The remaining blocker is not cluster reachability or user password validity. The remaining blocker is the Thunder to Backstage login flow, which appears to have a redirect or callback mismatch in the OAuth/OIDC path.

At this point, the platform is in a good operational state for infrastructure and service validation, but it is not yet in a clean end-user state for browser-based sign-in through the console.

---

## 2. Verified Working State

The following items are verified as working:

- OpenChoreo is deployed successfully on Rancher Desktop on macOS.
- Browser access to the exposed hostnames is working from the macOS host.
- Cilium Gateway API traffic is reachable through the host after enabling Gateway API host networking.
- The Rancher Desktop / Lima mount propagation issue that blocked Cilium BPF startup has a persistent boot-time fix.
- Pulumi-native integration tests were implemented and are passing.
- Thunder is deployed and responding on its public hostname.
- The live cluster contains valid bootstrapped Thunder users.

### Reachable endpoints

- Console: `http://openchoreo.localhost:8080`
- API: `http://api.openchoreo.localhost:8080`
- Thunder: `http://thunder.openchoreo.localhost:8080`
- Observer: `http://observer.openchoreo.localhost:11080`
- Data plane gateway: `http://openchoreo.localhost:19080`

### Integration test status

- Pulumi-native post-deployment validation is in place.
- Final test count: 29 passing tests.
- Coverage includes route acceptance, service reachability, and workload readiness checks.

---

## 3. Infrastructure Fixes Already Landed

### 3.1 Persistent Cilium mount propagation fix

Rancher Desktop runs k3s inside a Lima VM backed by Alpine Linux and OpenRC. Cilium requires shared mount propagation for BPF filesystem handling, and the default VM state was not sufficient.

The working fix is:

- make `/` shared with `mount --make-rshared /`
- run that at boot through an OpenRC service so the fix survives VM restarts

This removed the repeated manual recovery step and stabilized Cilium startup.

### 3.2 Gateway API browser access fix

The original Gateway API configuration was not enough for Rancher Desktop host accessibility. The final working setup uses:

- Cilium Gateway API enabled
- `gatewayAPI.hostNetwork.enabled=true`

This allows Envoy listeners to bind to host-visible ports in the Rancher Desktop environment, which restored browser access to the OpenChoreo hostnames on macOS.

---

## 4. Thunder Credential Findings

The credentials shown in some docs and bootstrap output were inconsistent with the live cluster state. The live deployment is bootstrapped from Thunder bootstrap configuration, and the verified users are:

- `admin@openchoreo.dev / Admin@123`
- `developer@openchoreo.dev / Dev@123`
- `platform-engineer@openchoreo.dev / PE@123`
- `sre@openchoreo.dev / SRE@123`

Important conclusion:

- `admin / admin` is not the correct login for this Pulumi-managed path.
- Login failures were not caused by using the wrong password after the live cluster values were confirmed.

One stale user-facing output was already corrected so the bootstrap summary now shows `admin@openchoreo.dev / Admin@123`.

---

## 5. Remaining Problem

The remaining unresolved issue is the browser login path from the OpenChoreo console into Thunder and back.

### Current diagnosis

The evidence so far indicates:

- Thunder itself is reachable.
- The bootstrapped users exist.
- Credentials are valid in the deployed configuration.
- Direct access to the bare Thunder Gate sign-in URL is not a reliable standalone validation path.

The bare Gate URL can return errors such as:

- `Either flowId or applicationId is required for authentication`

It can also surface organization-handle warnings when used directly through the custom domain.

That means the direct Gate URL is not the real product entrypoint for validating the OpenChoreo login flow. The correct validation path is the application-initiated flow from the console.

### Most likely failure area

The most likely failure is a mismatch in one or more of these areas:

- Backstage OAuth redirect URI
- Thunder application callback configuration
- issuer and endpoint wiring exposed to the control plane
- environment-specific callback generation, including the observed `env=development` behavior

This is consistent with the current code, where the control-plane OIDC values are built from the external Thunder URL:

- issuer: `thunder_url`
- jwksUrl: `thunder_url/oauth2/jwks`
- authorizationUrl: `thunder_url/oauth2/authorize`
- tokenUrl: `thunder_url/oauth2/token`

That may be correct for some flows, but it still needs to match exactly with how Backstage constructs its callback URL and how Thunder registers the client application.

---

## 6. What Is Not Considered Broken Right Now

The following items should not be treated as the active root cause unless new evidence contradicts this:

- Cilium networking in general
- host browser reachability
- Thunder pod availability
- invalid Thunder user passwords
- missing public Thunder hostname exposure

Those areas were investigated and are currently in a working state.

---

## 7. Remediation Plan

### Step 1: Capture the exact failing auth transaction

Collect the complete redirect sequence from console login to Thunder and back, including:

- authorize request URL
- redirect URI sent by Backstage
- callback received by the console/backend
- any `state`, `code`, `flowId`, `applicationId`, and environment-related parameters

Goal:

- identify the first point where the configured callback and the received callback diverge

### Step 2: Inspect Thunder client/application registration

Verify the effective Thunder bootstrap and application setup used by the live deployment, especially the Backstage-related client.

Check for:

- allowed redirect URIs
- client ID used by the console
- expected public URL and org-aware routing assumptions
- whether the callback is registered against the external hostname actually used in the browser

Goal:

- confirm whether Thunder is rejecting or misrouting the callback because of client registration mismatch

### Step 3: Reconcile control-plane OIDC values with the actual browser flow

Review and, if required, patch the Pulumi-generated control-plane values so the following are aligned with the real login path:

- issuer
- authorization URL
- token URL
- JWKS URL
- public base URL used by Backstage
- redirect URI generated by the console

Goal:

- make the deployed values deterministic and consistent for Rancher Desktop local-domain use

### Step 4: Re-test only through the application-driven flow

Do not treat bare Thunder Gate URL behavior as the primary success criterion.

Primary validation should be:

- open console
- click sign in
- complete Thunder login with a verified bootstrap user
- confirm return to console with an authenticated session

Goal:

- validate the real end-user flow, not an isolated IdP endpoint

### Step 5: Remove stale guidance and document the final login path

After the auth flow is fixed:

- update any remaining stale credentials in docs or scripts
- document the correct login entrypoint
- document the verified local-development credentials
- document any Rancher Desktop-specific assumptions that matter for auth

Goal:

- prevent future drift between repo guidance and actual deployed behavior

---

## 8. Expected Code Touch Points

The most likely files to change during remediation are:

- `pulumi/values/control_plane.py`
- `pulumi/components/control_plane.py`
- `pulumi/config.py`
- any docs or bootstrap summaries that still describe stale credentials or the wrong login entrypoint

Potentially relevant supporting files:

- `pulumi/values/observability_plane.py`
- upstream Thunder values consumed during install

---

## 9. Risk Assessment

### Low risk

- documentation corrections
- bootstrap output corrections
- adding clearer post-deploy validation guidance

### Medium risk

- changing OIDC endpoint wiring in control-plane values
- changing Thunder public URL or client callback settings

### Main regression risk

If the callback fix is made only for one path and not validated end-to-end, it is possible to fix the console login while breaking another service that relies on Thunder OIDC configuration.

That is why the final fix should be validated against:

- console login
- API auth assumptions, if applicable
- observability auth assumptions, where relevant

---

## 10. Current Bottom Line

The platform is operational from an infrastructure perspective.

The remaining blocker is narrowed to the identity flow between OpenChoreo and Thunder, most likely around redirect or callback alignment rather than cluster networking or credentials.

The next work should focus on exact OAuth transaction tracing and then a targeted Pulumi-side configuration correction, followed by a real browser-driven sign-in validation.