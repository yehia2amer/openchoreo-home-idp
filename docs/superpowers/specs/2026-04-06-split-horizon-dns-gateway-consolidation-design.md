# Split-Horizon DNS with Gateway Consolidation

## Overview

Migrate DNS from the current CoreDNS LAN approach to a split-horizon ExternalDNS architecture. Users access services via `*.amernas.work` — the same URL from LAN and internet. LAN resolves to local Cilium L2 IPs; internet resolves to Cloudflare Tunnel. A keepalived VIP provides DNS HA across TrueNAS and the K8s cluster.

Simultaneously, consolidate the three per-plane gateways (each with custom ports and separate IPs) into a single shared gateway on `192.168.0.10:80/443` with hostname-based routing.

**Domain**: `amernas.work` (Cloudflare zone `330e3b1404378ac294a9814bc059a19a`)

---

## Architecture

```
                         Internet
                            │
                   ┌────────▼────────┐
                   │    Cloudflare    │
                   │  *.amernas.work  │
                   │  (proxied CDN)   │
                   └────────┬────────┘
                            │ Argo Tunnel (cloudflared on Talos node)
                            │ Tunnel ID: 9552dd63-a9cb-4f0f-a668-1c576ab28fc8
                            ▼
═══════════════════════════════════════════════════════
                   LAN (192.168.0.0/24)
═══════════════════════════════════════════════════════
                            │
              ┌─────────────┼──────────────┐
              │             │              │
    ┌─────────▼──────┐     │     ┌────────▼────────┐
    │ TL-R480T+ Router│     │     │  LEDE Router     │
    │  192.168.0.1    │     │     │  TL-MR3420       │
    │  DHCP: DNS →    │     │     │  Tertiary DNS    │
    │  192.168.0.53   │     │     │  (dumb forwarder)│
    └─────────────────┘     │     └─────────────────┘
                            │
              All LAN devices query 192.168.0.53
                            │
                   ┌────────▼────────┐
                   │  Keepalived VIP  │
                   │  192.168.0.53    │
                   │  VRRP ID: 53     │
                   └───┬─────────┬───┘
                       │         │
          ┌────────────▼─┐   ┌──▼────────────┐
          │ TrueNAS       │   │ K8s Cluster    │
          │ HP ProDesk     │   │ Dell T7610     │
          │                │   │ 192.168.0.100  │
          │ AdGuard Home   │   │                │
          │ keepalived     │   │ AdGuard Home   │
          │ MASTER pri=100 │   │ keepalived     │
          │                │   │ BACKUP pri=50  │
          │                │   │                │
          │     ◄──────────│───│ ExternalDNS    │
          │  (records      │   │ ├─ Cloudflare  │
          │   written by   │   │ └─ AdGuard ×2  │
          │   ExternalDNS) │   │                │
          └────────────────┘   │ Shared Gateway │
                               │ 192.168.0.10   │
                               │ :80/443         │
                               └────────────────┘
```

### DNS Resolution Paths

**From LAN:**
```
Device → 192.168.0.53 (VIP → AdGuard Home)
  → grafana.amernas.work → 192.168.0.10 (direct to shared gateway)
  → google.com → upstream 1.1.1.1
```

**From Internet:**
```
Browser → Cloudflare DNS
  → grafana.amernas.work → Cloudflare proxy → Argo Tunnel → 192.168.0.10:443
```

### Failure Matrix

| Scenario | Internet? | Local DNS? | Notes |
|----------|-----------|-----------|-------|
| All up | ✅ | ✅ local IPs | Normal operation |
| K8s down | ✅ | ✅ TrueNAS has records | Services unreachable but DNS correct |
| TrueNAS down | ✅ | ✅ K8s AdGuard takes VIP | 1-3s failover via VRRP |
| Both down | ✅ via LEDE | ❌ local resolution | LEDE forwards to 1.1.1.1; Cloudflare tunnel also down |
| All three DNS down | ❌ | ❌ | Catastrophic — all infrastructure offline |

---

## Component 1: Shared Gateway

### What Changes

Replace three per-plane gateways with one shared gateway in a dedicated namespace.

**Before:**
- `openchoreo-control-plane/gateway-default` → `192.168.0.10:8080/8443`
- `openchoreo-data-plane/gateway-default` → `192.168.0.11:19080/19443`
- `openchoreo-observability-plane/gateway-default` → `192.168.0.12:11080/11085`

**After:**
- `openchoreo-gateway/gateway-shared` → `192.168.0.10:80/443`

### Gateway Resource

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: gateway-shared
  namespace: openchoreo-gateway
  annotations:
    io.cilium/lb-ipam-ips: "192.168.0.10"
spec:
  gatewayClassName: cilium  # or kgateway, depending on platform
  listeners:
    - name: http
      port: 80
      protocol: HTTP
      allowedRoutes:
        namespaces:
          from: All
    - name: https
      port: 443
      protocol: HTTPS
      hostname: "*.amernas.work"
      tls:
        mode: Terminate
        certificateRefs:
          - name: wildcard-amernas-work-tls
      allowedRoutes:
        namespaces:
          from: All
```

### ReferenceGrants

Each backend namespace needs a ReferenceGrant allowing `openchoreo-gateway` to route to its Services:

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-gateway-routing
  namespace: <backend-namespace>
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: openchoreo-gateway
  to:
    - group: ""
      kind: Service
```

Required in namespaces: `openchoreo-control-plane`, `openchoreo-data-plane`, `openchoreo-observability-plane`, `openchoreo-workflow-plane`, `kube-system`, `longhorn-system`, `openbao`.

### HTTPRoute Migration

All existing HTTPRoutes move to `openchoreo-gateway` namespace, referencing `gateway-shared`:

| Subdomain | Backend Service | Backend Namespace | Backend Port |
|-----------|----------------|-------------------|-------------|
| `talos.amernas.work` | backstage | openchoreo-control-plane | 7007 |
| `api.amernas.work` | openchoreo-api | openchoreo-control-plane | 8080 |
| `thunder.amernas.work` | thunder | openchoreo-control-plane | (port from chart) |
| `hubble.amernas.work` | hubble-ui | kube-system | 80 |
| `longhorn.amernas.work` | longhorn-frontend | longhorn-system | 80 |
| `argo.amernas.work` | argo-server | openchoreo-workflow-plane | 10081 |
| `openbao.amernas.work` | openbao | openbao | 8200 |
| `grafana.amernas.work` | observer (Grafana) | openchoreo-observability-plane | (port from chart) |
| `prometheus.amernas.work` | openchoreo-observability-prometheus | openchoreo-observability-plane | 9091 |
| `opensearch.amernas.work` | opensearch | openchoreo-observability-plane | 9200 |
| `alertmanager.amernas.work` | openchoreo-observability-alertmanager | openchoreo-observability-plane | 9093 |
| `rca-agent.amernas.work` | rca-agent | openchoreo-observability-plane | (port from chart) |
| `*.amernas.work` | data-plane-gateway | openchoreo-data-plane | 443 |

### Cilium L2 IP Retirement

- **Keep**: `192.168.0.10` for the shared gateway
- **Retire**: `192.168.0.11` (DP) and `192.168.0.12` (OP) — return to DHCP pool
- Remove `gateway_pin_ip_dp` and `gateway_pin_ip_op` from Pulumi config
- Rename `gateway_pin_ip` to `gateway_ip` (clarity)

### Internal Service References

Components that reference gateway endpoints internally must be updated:

- `workflow_plane.py`: `gateway_endpoint` changes from `gateway-default.{NS_CONTROL_PLANE}:8080` to `gateway-shared.openchoreo-gateway:80`
- URL config (`backstage_url`, `api_url`, `thunder_url`, `observer_url`) drops port numbers

### TLS Certificate

Wildcard cert for `*.amernas.work` via Let's Encrypt DNS01 challenge:

- cert-manager ClusterIssuer with Cloudflare DNS01 solver
- Automatic renewal
- Uses same Cloudflare API token as ExternalDNS

---

## Component 2: ExternalDNS — Cloudflare (Public)

Helm chart deployment in K8s. Watches Gateway HTTPRoutes and creates Cloudflare DNS records.

| Setting | Value |
|---------|-------|
| Chart | `external-dns/external-dns` v1.18.x |
| Namespace | `external-dns` |
| Provider | `cloudflare` |
| Sources | `gateway-httproute`, `gateway-grpcroute`, `gateway-tlsroute`, `ingress`, `service` |
| Domain filter | `amernas.work` |
| Zone ID filter | `330e3b1404378ac294a9814bc059a19a` |
| Proxy mode | `--cloudflare-proxied` |
| Default target | `9552dd63-a9cb-4f0f-a668-1c576ab28fc8.cfargotunnel.com` |
| TXT owner ID | `cloudflare-public` |
| Policy | `sync` (creates and deletes) |
| Gateway namespace | Watch `openchoreo-gateway` |

**Secret**: Cloudflare API token from OpenBao via ExternalSecret at path `apps/external-dns/cloudflare`.

---

## Component 3: ExternalDNS — AdGuard (Internal) × 2

Two deployments, each targeting a different AdGuard instance. Both watch the same K8s resources.

### ExternalDNS AdGuard #1 (targets TrueNAS AdGuard)

| Setting | Value |
|---------|-------|
| Chart | `external-dns/external-dns` v1.18.x |
| Namespace | `external-dns` |
| Release name | `external-dns-adguard-truenas` |
| Provider | `webhook` (AdGuard provider sidecar) |
| Webhook image | `ghcr.io/muhlba91/external-dns-provider-adguard:v9.x` |
| TXT owner ID | `adguard-truenas` |
| ADGUARD_URL | TrueNAS AdGuard URL (from secret) |
| Sources | Same as Cloudflare instance |

### ExternalDNS AdGuard #2 (targets K8s AdGuard)

| Setting | Value |
|---------|-------|
| Release name | `external-dns-adguard-k8s` |
| TXT owner ID | `adguard-k8s` |
| ADGUARD_URL | K8s AdGuard URL (e.g., `http://adguard-k8s.external-dns.svc:3000`) |
| Everything else | Same as #1 |

**Why two deployments**: ExternalDNS webhook provider targets one endpoint per instance. To write identical records to both AdGuard instances, we run two ExternalDNS pods.

**What ExternalDNS writes**: DNS rewrite rules mapping `*.amernas.work` subdomains to `192.168.0.10` (shared gateway LB IP).

---

## Component 4: AdGuard Home — K8s Pod

Replaces the current CoreDNS LAN component. Runs on hostNetwork.

| Setting | Value |
|---------|-------|
| Namespace | `external-dns` |
| Deployment | `adguard-home-k8s` |
| Network | `hostNetwork: true` |
| DNS port | 53 (UDP + TCP) on node LAN IP |
| Web UI | Port 3000 |
| Upstream DNS | `1.1.1.1`, `8.8.8.8` |
| Ad blocking | Enabled |
| DNS rewrites | Auto-managed by ExternalDNS AdGuard #2 |
| Replaces | `coredns_lan.py` component |

Deployed as raw K8s Deployment + ConfigMap + Service (not Helm).

---

## Component 5: Keepalived — VIP Failover

### On K8s (Talos node)

| Setting | Value |
|---------|-------|
| VIP | `192.168.0.53` |
| VRRP instance | `DNS_VIP` |
| VRRP ID | `53` |
| Priority | `50` (BACKUP) |
| Interface | Primary LAN NIC |
| Health check | `dig @127.0.0.1 amernas.work` |
| Auth | VRRP password from OpenBao |

Preferred deployment: Talos system extension (survives kubelet restarts).

### On TrueNAS (prerequisite, manual)

| Setting | Value |
|---------|-------|
| VIP | `192.168.0.53` |
| Priority | `100` (MASTER) |
| VRRP ID | `53` |
| Health check | AdGuard port 53 |
| Deployment | TrueNAS app (Docker container) |

---

## Component 6: OpenBao Secrets

| Secret Path | Keys | Used By |
|-------------|------|---------|
| `apps/external-dns/cloudflare` | `api-token` | ExternalDNS Cloudflare + cert-manager |
| `apps/external-dns/adguard-truenas` | `url`, `user`, `password` | ExternalDNS AdGuard #1 |
| `apps/external-dns/adguard-k8s` | `url`, `user`, `password` | ExternalDNS AdGuard #2 |
| `apps/external-dns/keepalived` | `auth-pass` | Keepalived VRRP auth |

---

## Component 7: Router DHCP (Manual, one-time)

1. Log into TL-R480T+ at `192.168.0.1`
2. Set DHCP DNS Server 1: `192.168.0.53` (keepalived VIP)
3. Set DHCP DNS Server 2: TrueNAS real IP (direct fallback)
4. Set DHCP DNS Server 3: LEDE IP (optional dumb fallback)
5. Reserve `192.168.0.53` in DHCP exclusion range

---

## Component 8: LEDE Router — Dumb Fallback (Optional)

| Setting | Value |
|---------|-------|
| Device | TP-Link TL-MR3420 v2 (LEDE/OpenWrt) |
| Software | dnsmasq |
| Config | Forward all queries to `1.1.1.1` and `8.8.8.8` |
| When used | Only if both TrueNAS and K8s are down |

---

## What Gets Removed

| Component | Files | Action |
|-----------|-------|--------|
| CoreDNS LAN | `components/coredns_lan.py`, `values/coredns_lan.py` | Delete |
| Gateway pin IPs (DP, OP) | `config.py`, `Pulumi.talos-baremetal.yaml` | Remove fields |
| Per-plane gateways | `__main__.py` Step 7.5, ServicePatch loop | Replace |
| Custom port config | `config.py` cp/dp/op port fields | Simplify |
| Per-plane TLS patches | `__main__.py` TLS patch loop | Replace with wildcard |
| Inline HTTPRoutes | `__main__.py` `_infra_routes` section | Move to gateway ns |

---

## Migration Sequence

### Phase 1: Foundation (no service disruption)
1. Create `openchoreo-gateway` namespace
2. Deploy wildcard TLS cert (`*.amernas.work`)
3. Deploy shared gateway alongside existing gateways (parallel)
4. Deploy ExternalDNS Cloudflare + AdGuard instances
5. Provision OpenBao secrets
6. Deploy AdGuard Home on K8s (alongside CoreDNS LAN)

### Phase 2: Traffic Migration (controlled cutover)
7. Create HTTPRoutes on shared gateway (duplicate of existing routes)
8. Verify all services accessible via `*.amernas.work:443` on shared gateway
9. Update Argo Tunnel config to point to shared gateway IP
10. Switch DNS (router DHCP → VIP, Cloudflare → tunnel target update)
11. Verify split-horizon: LAN → local IP, internet → Cloudflare

### Phase 3: Cleanup (after 1 week stable)
12. Remove per-plane gateways and ServicePatch annotations
13. Remove CoreDNS LAN component
14. Remove gateway_pin_ip_dp and gateway_pin_ip_op config
15. Simplify port configuration
16. Update internal service references to shared gateway
17. Update documentation

---

## Prerequisites (Manual, before automation)

1. **AdGuard Home on TrueNAS** — install via TrueNAS Apps
2. **Keepalived on TrueNAS** — install as Docker container, MASTER priority 100
3. **Reserve 192.168.0.53** — in router DHCP
4. **Cloudflare API token** — Zone:DNS:Edit, store in OpenBao
5. **AdGuard credentials** — note URL/user/password for both instances, store in OpenBao
6. **LEDE router** (optional) — power on, configure dnsmasq

---

## Success Criteria

- [ ] `dig talos.amernas.work` from LAN → returns `192.168.0.10`
- [ ] `dig talos.amernas.work` from internet → returns Cloudflare proxy IP
- [ ] `curl https://talos.amernas.work` from LAN → Backstage loads (direct)
- [ ] `curl https://talos.amernas.work` from internet → Backstage loads (via tunnel)
- [ ] All 11+ subdomains resolve and route correctly
- [ ] TLS certificate valid (Let's Encrypt, no browser warnings)
- [ ] Kill K8s AdGuard pod → VIP stays on TrueNAS, DNS uninterrupted
- [ ] Kill TrueNAS AdGuard → VIP moves to K8s in <3s, DNS continues
- [ ] New HTTPRoute created → DNS record appears in Cloudflare AND both AdGuards within 5 minutes
- [ ] CoreDNS LAN component fully removed from codebase
- [ ] No custom port numbers in any user-facing URL
- [ ] `gateway_pin_ip_dp` and `gateway_pin_ip_op` removed from config
