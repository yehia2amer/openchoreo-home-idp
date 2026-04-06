# DNS Epic (sf8) — Execution Plan

**Epic**: Split-Horizon DNS with Gateway Consolidation
**Design spec**: `docs/superpowers/specs/2026-04-06-split-horizon-dns-gateway-consolidation-design.md`
**ADR**: `docs/adr/001-pulumi-fluxcd-boundary.md`
**Approach**: Option C — new infra via FluxCD GitOps, Pulumi for imperative only

---

## Repos Involved

| Repo | What changes | How |
|------|-------------|-----|
| `openchoreo-home-idp` (this repo) | Pulumi bootstrap (sf8.5, sf8.15 partial), Talos config (sf8.14), cleanup (sf8.6) | `pulumi up` + git push |
| `yehia2amer/openchoreo-gitops` | All FluxCD manifests (sf8.3, sf8.4, sf8.8, sf8.9, sf8.10, sf8.11, sf8.12, sf8.15 partial) | git push → FluxCD auto-reconcile |

---

## Phase 1: Foundation (Zero Disruption)

### Wave 0 — Bootstrap (2 parallel tracks)

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  TRACK A: Pulumi Bootstrap  │     │  TRACK B: GitOps Bootstrap  │
│                             │     │                             │
│  sf8.5  OpenBao secrets     │     │  sf8.15  FluxCD infra       │
│  ├─ Add 4 secret policies   │     │          Kustomization      │
│  ├─ pulumi up               │     │  ├─ Add oc-infrastructure   │
│  └─ Manual: seed values     │     │  │  to flux_gitops.py       │
│     via kubectl exec        │     │  ├─ pulumi up               │
│                             │     │  ├─ Create infrastructure/  │
│  ~1.5h active               │     │  │  dir in gitops repo      │
│  (includes manual seeding)  │     │  └─ Verify Kustomization    │
│                             │     │     shows Ready             │
│                             │     │                             │
│                             │     │  ~1h active                 │
└─────────────────────────────┘     └─────────────────────────────┘
         │                                    │
         └──────────┬─────────────────────────┘
                    │
              Both must finish
              before Wave 1
```

**Track A (sf8.5)** — Pulumi + manual:
1. Modify `pulumi/values/openbao.py` — add 4 secret paths + policies
2. Run `pulumi up` on talos-baremetal stack
3. Manually seed actual secret values via `kubectl exec`
4. Verify: `bao kv get` succeeds for all 4 paths

**Track B (sf8.15)** — Pulumi + gitops repo:
1. Add `oc-infrastructure` Kustomization to `pulumi/components/flux_gitops.py`
2. Run `pulumi up`
3. Create `infrastructure/kustomization.yaml` in gitops repo (empty initially)
4. Verify: `flux get kustomizations` shows `oc-infrastructure` Ready

**These two tracks have ZERO dependencies on each other — full parallel.**

---

### Wave 1 — Core Infrastructure (3 parallel tracks)

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  TRACK A: Gateway    │  │  TRACK B: DNS Resolver│  │  TRACK C: TLS        │
│                      │  │                       │  │                      │
│  sf8.8  Shared GW    │  │  sf8.10  AdGuard Home │  │  sf8.9  Wildcard TLS │
│  ├─ Namespace YAML   │  │  ├─ Deployment YAML   │  │  ├─ ClusterIssuer    │
│  ├─ Gateway YAML     │  │  ├─ ConfigMap YAML    │  │  ├─ ExternalSecret   │
│  ├─ 7 ReferenceGrant │  │  ├─ Service YAML      │  │  ├─ Certificate YAML │
│  └─ git push         │  │  └─ git push          │  │  └─ git push         │
│                      │  │                       │  │                      │
│  Depends: sf8.15     │  │  Depends: sf8.15      │  │  Depends: sf8.5,     │
│           sf8.5      │  │                       │  │           sf8.15     │
│           sf8.9*     │  │  ~1h active           │  │                      │
│                      │  │                       │  │  ~1h active          │
│  ~2h active          │  │                       │  │  (+ wait for LE      │
│                      │  │                       │  │   cert issuance)     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

* sf8.8 Gateway HTTPS listener references the wildcard TLS cert from sf8.9.
  Strategy: deploy Gateway with HTTP-only first, add HTTPS after sf8.9 completes.
  OR: deploy both simultaneously — cert-manager will create the Secret when ready,
  Gateway will pick it up automatically.
```

**Track A (sf8.8)** — GitOps manifests:
1. `infrastructure/namespaces/openchoreo-gateway.yaml`
2. `infrastructure/openchoreo-gateway/gateway-shared.yaml` (HTTP + HTTPS listeners)
3. `infrastructure/openchoreo-gateway/reference-grants/*.yaml` (7 files)
4. Git push → FluxCD reconciles
5. Verify: Gateway shows Programmed=True, LB IP is 192.168.0.10

**Track B (sf8.10)** — GitOps manifests:
1. `infrastructure/adguard-home/deployment.yaml` (hostNetwork, port 53)
2. `infrastructure/adguard-home/configmap.yaml` (upstream DNS, ad blocking)
3. `infrastructure/adguard-home/service.yaml` (ClusterIP for internal access)
4. Git push → FluxCD reconciles
5. Verify: `dig @<node-ip> google.com` works, web UI at port 3000

**Track C (sf8.9)** — GitOps manifests:
1. `infrastructure/cert-manager/externalsecret-cloudflare-token.yaml`
2. `infrastructure/cert-manager/dns01-clusterissuer.yaml`
3. `infrastructure/cert-manager/wildcard-certificate.yaml`
4. Git push → FluxCD reconciles → cert-manager issues Let's Encrypt cert
5. Verify: Certificate Ready=True, Secret `wildcard-amernas-work-tls` exists

**All 3 tracks can run in parallel.** Gateway will automatically pick up the TLS cert when cert-manager creates it.

---

### Wave 2 — DNS Automation (2 parallel tracks)

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  TRACK A: Public DNS         │  │  TRACK B: Internal DNS       │
│                              │  │                              │
│  sf8.3  ExternalDNS CF       │  │  sf8.4  ExternalDNS AG x2   │
│  ├─ HelmRepository YAML     │  │  ├─ HelmRelease #1 (TrueNAS)│
│  ├─ HelmRelease YAML        │  │  ├─ ExternalSecret #1        │
│  ├─ ExternalSecret YAML     │  │  ├─ HelmRelease #2 (K8s)    │
│  └─ git push                │  │  ├─ ExternalSecret #2        │
│                              │  │  └─ git push                │
│  Depends: sf8.5, sf8.8,     │  │                              │
│           sf8.15             │  │  Depends: sf8.5, sf8.8,     │
│                              │  │           sf8.10, sf8.15    │
│  ~1.5h active                │  │                              │
│                              │  │  ~2h active                 │
└──────────────────────────────┘  └──────────────────────────────┘
```

**Track A (sf8.3)** — GitOps manifests:
1. `infrastructure/sources/external-dns-helmrepo.yaml` (HelmRepository)
2. `infrastructure/external-dns/cloudflare/helmrelease.yaml`
3. `infrastructure/external-dns/cloudflare/externalsecret.yaml`
4. Git push → FluxCD reconciles → ExternalDNS pod starts → creates Cloudflare records
5. Verify: `dig` from internet returns Cloudflare proxy IP

**Track B (sf8.4)** — GitOps manifests:
1. `infrastructure/external-dns/adguard-truenas/helmrelease.yaml` + `externalsecret.yaml`
2. `infrastructure/external-dns/adguard-k8s/helmrelease.yaml` + `externalsecret.yaml`
3. Git push → FluxCD reconciles → 2 ExternalDNS pods start → write AdGuard rewrite rules
4. Verify: DNS rewrites appear in both AdGuard instances

**Both tracks can run in parallel.** They share the HelmRepository source (created by Track A, but Track B can include it too or use the same one).

---

### Wave 2b — VIP (starts as soon as sf8.5 + sf8.10 + sf8.15 done)

```
┌──────────────────────────────┐
│  sf8.11  Keepalived VIP      │
│  ├─ DaemonSet YAML           │
│  ├─ ConfigMap YAML           │
│  ├─ ExternalSecret YAML      │
│  └─ git push                 │
│                              │
│  Depends: sf8.5, sf8.10,    │
│           sf8.15             │
│  Prereq: TrueNAS keepalived │
│           running (manual)   │
│                              │
│  ~1.5h active                │
└──────────────────────────────┘
```

**sf8.11 can run in parallel with Wave 2 tracks.** Its only deps are sf8.5 (secrets), sf8.10 (AdGuard for health check), and sf8.15 (FluxCD Kustomization) — all completed in earlier waves.

---

## Phase 2: Traffic Migration (Controlled Cutover)

### Wave 3 — Route Migration (sequential, careful)

```
┌──────────────────────────────────────────────────────────────┐
│  sf8.12  HTTPRoute Migration                                 │
│                                                              │
│  Create ~13 HTTPRoutes in gitops repo:                       │
│  infrastructure/openchoreo-gateway/httproutes/               │
│  ├─ backstage.yaml    (talos.amernas.work)                   │
│  ├─ api.yaml          (api.amernas.work)                     │
│  ├─ thunder.yaml      (thunder.amernas.work)                 │
│  ├─ hubble.yaml       (hubble.amernas.work)                  │
│  ├─ longhorn.yaml     (longhorn.amernas.work)                │
│  ├─ argo.yaml         (argo.amernas.work)                    │
│  ├─ openbao.yaml      (openbao.amernas.work)                │
│  ├─ grafana.yaml      (grafana.amernas.work)                │
│  ├─ prometheus.yaml   (prometheus.amernas.work)              │
│  ├─ opensearch.yaml   (opensearch.amernas.work)              │
│  ├─ alertmanager.yaml (alertmanager.amernas.work)            │
│  ├─ rca-agent.yaml    (rca-agent.amernas.work)              │
│  └─ wildcard-dp.yaml  (*.amernas.work → data-plane)         │
│                                                              │
│  Strategy: Deploy ALL routes at once via single git push.    │
│  Old per-plane routes still active — zero disruption.        │
│  Test each subdomain via curl against 192.168.0.10:443.      │
│                                                              │
│  Depends: sf8.8, sf8.9, sf8.15                               │
│  ~3h active (create + test each route)                       │
└──────────────────────────────────────────────────────────────┘
```

**This is sequential** — all routes in one commit, tested as a batch. Old routes remain active so there's no disruption.

---

### Wave 4 — DNS Cutover (2 parallel tracks)

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  sf8.14  Argo Tunnel Update  │  │  sf8.13  Router DHCP         │
│                              │  │  (MANUAL)                    │
│  Update Cloudflare Tunnel    │  │                              │
│  routing to point             │  │  1. Login to TL-R480T+      │
│  *.amernas.work →            │  │  2. DHCP DNS → 192.168.0.53 │
│  192.168.0.10:443            │  │  3. Reserve VIP in DHCP      │
│                              │  │  4. Renew DHCP on devices    │
│  Depends: sf8.12             │  │                              │
│  ~30min active               │  │  Depends: sf8.11             │
│                              │  │  ~30min active               │
└──────────────────────────────┘  └──────────────────────────────┘

⚠️  CUTOVER POINT — After these two tasks, DNS queries from LAN
    go through Keepalived VIP → AdGuard. Internet traffic goes
    through updated Argo Tunnel → shared gateway.
    
    TEST IMMEDIATELY:
    - dig talos.amernas.work from LAN → 192.168.0.10
    - dig talos.amernas.work from internet → Cloudflare IP
    - curl https://talos.amernas.work from both → Backstage loads
```

---

## Phase 3: Cleanup (After 1 Week Stable)

### Wave 5 — Remove Old Infrastructure

```
┌──────────────────────────────────────────────────────────────┐
│  sf8.6  Phase 3 Cleanup                                      │
│                                                              │
│  In this repo (Pulumi):                                      │
│  ├─ Delete pulumi/components/coredns_lan.py                  │
│  ├─ Remove CoreDNS LAN from __main__.py                      │
│  ├─ Remove gateway_pin_ip_dp, gateway_pin_ip_op from config  │
│  ├─ Remove per-plane ServicePatch loop                       │
│  ├─ Remove per-plane TLS patch loop                          │
│  ├─ Remove inline _infra_routes HTTPRoutes                   │
│  ├─ Update Helm values (gateway_endpoint references)         │
│  └─ pulumi up (removes old resources from cluster)           │
│                                                              │
│  Depends: sf8.14, sf8.13 + 1 week stable                    │
│  ~3h active                                                  │
└──────────────────────────────────────────────────────────────┘
```

### Wave 6 — Final Verification

```
┌──────────────────────────────────────────────────────────────┐
│  sf8.7  Migration Complete — Verify All Success Criteria     │
│                                                              │
│  12 success criteria from design spec:                       │
│  □ dig from LAN → 192.168.0.10                              │
│  □ dig from internet → Cloudflare proxy IP                   │
│  □ curl https from LAN → direct to gateway                  │
│  □ curl https from internet → via Argo Tunnel               │
│  □ All 11+ subdomains resolve and route                      │
│  □ TLS valid (Let's Encrypt, no warnings)                   │
│  □ Kill K8s AdGuard → TrueNAS DNS uninterrupted             │
│  □ Kill TrueNAS AdGuard → K8s takes VIP in <3s              │
│  □ New HTTPRoute → DNS in CF + AdGuard in <5min             │
│  □ CoreDNS LAN fully removed                                │
│  □ No custom ports in URLs                                   │
│  □ gateway_pin_ip_dp/op removed from config                  │
│                                                              │
│  Depends: sf8.6                                              │
│  ~2h active                                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Timeline Summary

```
WEEK 1
──────────────────────────────────────────────────────────────────
Day 1-2:  Wave 0  │ sf8.5 (Pulumi) ║ sf8.15 (Pulumi+GitOps)
                   │                ║
Day 2-3:  Wave 1  │ sf8.8 (GW)     ║ sf8.10 (AdGuard)  ║ sf8.9 (TLS)
                   │                ║                    ║
Day 3-4:  Wave 2  │ sf8.3 (CF DNS) ║ sf8.4 (AG DNS x2) ║ sf8.11 (VIP)
                   │                ║                    ║
Day 4-5:  Wave 3  │ sf8.12 (HTTPRoutes — sequential, careful)
                   │
Day 5:    Wave 4  │ sf8.14 (Tunnel) ║ sf8.13 (Router DHCP)
                   │ ⚠️ CUTOVER POINT

WEEK 2 (soak period — monitor, fix issues)
──────────────────────────────────────────────────────────────────

WEEK 3
──────────────────────────────────────────────────────────────────
Day 1:    Wave 5  │ sf8.6 (Cleanup old Pulumi components)
Day 1-2:  Wave 6  │ sf8.7 (Final verification — all 12 criteria)
```

## Effort Estimates

| Wave | Tasks | Active Hours | Calendar | Parallelism |
|------|-------|-------------|----------|-------------|
| 0 | sf8.5 + sf8.15 | 2.5h | 1 day | 2 tracks |
| 1 | sf8.8 + sf8.10 + sf8.9 | 4h | 1-2 days | 3 tracks |
| 2 | sf8.3 + sf8.4 + sf8.11 | 5h | 1-2 days | 3 tracks |
| 3 | sf8.12 | 3h | 1 day | sequential |
| 4 | sf8.14 + sf8.13 | 1h | 0.5 day | 2 tracks |
| 5 | sf8.6 | 3h | 0.5 day | sequential |
| 6 | sf8.7 | 2h | 0.5 day | sequential |
| | **TOTAL** | **~20.5h** | **~2.5 weeks** | |

## Manual Prerequisites (Before Wave 0)

- [ ] AdGuard Home installed on TrueNAS via TrueNAS Apps
- [ ] Keepalived installed on TrueNAS as Docker container (MASTER priority 100, VIP 192.168.0.53)
- [ ] Cloudflare API token created (Zone:DNS:Edit for amernas.work)
- [ ] AdGuard credentials noted for both instances (TrueNAS + K8s URLs, user, password)
- [ ] VRRP auth password generated
- [ ] 192.168.0.53 reserved in router DHCP exclusion range

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| FluxCD doesn't reconcile new manifests | Wave 0 verifies oc-infrastructure Kustomization is Ready before proceeding |
| Let's Encrypt rate limiting | Use staging ACME server first, switch to production after testing |
| ExternalDNS writes wrong records | TXT owner IDs prevent cross-instance conflicts; deploy alongside existing DNS |
| Gateway HTTPS fails without cert | Deploy HTTP listener first; cert-manager creates Secret async; Gateway picks it up |
| Keepalived VIP conflict | K8s is BACKUP (pri 50), TrueNAS is MASTER (pri 100) — no conflict |
| HTTPRoute migration breaks services | Old per-plane routes remain active; new routes are additive; test before cutover |
| Router DHCP change disrupts network | Devices refresh DNS on next DHCP renew; can force renew on critical devices |

## Rollback Plan

| Phase | Rollback |
|-------|----------|
| Phase 1 (Foundation) | Delete FluxCD manifests from gitops repo → FluxCD prunes resources. No impact on existing services. |
| Phase 2 (Cutover) | Revert router DHCP to old DNS servers. Revert Argo Tunnel config. Old per-plane gateways still running. |
| Phase 3 (Cleanup) | `git revert` the Pulumi cleanup commit → `pulumi up` restores old components. |
