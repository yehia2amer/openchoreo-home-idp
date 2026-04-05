# Draft: Phase 3 — FluxCD + Monitoring + HTTPRoutes for LAN Access

## Requirements (confirmed)
- User wants Phase 3: FluxCD for app workloads, monitoring stack, HTTPRoutes for LAN access
- "Each service should have an HTTP Route that I can access from another machine on my local network"
- Phase 2 is complete (31/31 tests, 51/51 pods, user accepted)

## Technical Decisions
- **DNS Strategy**: nip.io / sslip.io for now. Future: CoreDNS + Cloudflare (advanced DNS)
- **LAN Access**: Not tested yet — need to verify Cilium L2 LoadBalancer IPs work from LAN first
- **FluxCD Workloads**: Future app workloads too (full directory structure)
- **Repo Access**: Private repo, user has GitHub PAT ready
- **Monitoring**: Enable OpenChoreo observability plane (enable_observability=true) — uses existing Pulumi component
- **Services needing HTTPRoutes**: All existing (Backstage, API, Thunder, Argo Workflows) + monitoring (Grafana/Observer)
- **TLS**: Both HTTP and HTTPS — HTTPS with self-signed on existing ports + HTTP on port 80 for easy LAN access
- **HTTPRoute hostnames**: Use nip.io with the Gateway LoadBalancer IP (e.g., backstage.192.168.0.XX.sslip.io)

## Research Findings

### Explorer Findings — Current Codebase State

**FluxCD:**
- Full Pulumi component exists at `pulumi/components/flux_gitops.py` (178 lines) — READY to enable
- Currently disabled: `enable_flux: "false"` in `Pulumi.talos-baremetal.yaml`
- Component installs Flux from official release URL, creates GitRepository + 4 Kustomizations
- Expected directories at repo root: `./namespaces`, `./platform-shared`, `./namespaces/default/platform`, `./namespaces/default/projects` — NONE EXIST
- `github_pat` needed for private repo access (currently empty)
- Dev stack already has flux enabled (`Pulumi.dev.yaml`)
- Integration tests exist for flux (conditional on enable_flux)

**Gateway API / HTTPRoutes:**
- Gateway API CRDs v1.3.0 installed in Phase 1
- kgateway is the Gateway API controller (not Cilium gateway)
- OpenChoreo Helm charts already create Gateway + HTTPRoutes for: backstage, openchoreo-api, thunder, observer, rca-agent
- All use `*.openchoreo.local` domain
- Cilium L2 provides LoadBalancer IPs from pool `192.168.0.10-192.168.0.99`

**Monitoring:**
- `enable_observability` defaults to False for talos-baremetal
- Full observability plane component exists at `pulumi/components/observability_plane.py` (256 lines)
- When enabled, deploys: Observer, controller-manager, cluster-agent, OpenSearch + Fluent Bit, tracing, kube-prometheus-stack
- Has its own Gateway with HTTPRoutes for observer and rca-agent
- No standalone Grafana/Prometheus exists outside OpenChoreo's observability plane

**Network:**
- Cilium L2 announcements enabled with IP pool 192.168.0.10-192.168.0.99
- L2 interfaces: enp7s0, enp0s1, enp0s25
- Node IP: 192.168.0.100
- LoadBalancer services automatically get LAN IPs from Cilium

**Domain/TLS:**
- Domain: `openchoreo.local`
- TLS: enabled (self-signed CA via cert-manager)
- CP ports: HTTP 8080, HTTPS 8443
- DP ports: HTTP 19080, HTTPS 19443
- WP ports: Argo 10081, Registry 10082
- OP ports: HTTP 11080, HTTPS 11085

**Critical Architecture Insight:**
- Phase 1 Cilium: `gatewayAPI: {"enabled": False}` — CNI only
- Phase 2: `gateway_mode="kgateway"` — kgateway provides Gateway API controller
- Cilium provides L2 LoadBalancer IPs → kgateway envoy gets those IPs
- HTTPRoutes managed by kgateway's envoy

### Librarian Findings — Best Practices

**Monitoring Stack:**
- Recommended: kube-prometheus-stack (Prometheus Operator)
- Talos compatible (no host FS access needed)
- ~2-3GB RAM, ~1-2 CPU overhead (acceptable for home lab)
- Single-node optimizations: 10Gi storage, 7d retention
- Victoria Metrics lighter but more complex for home lab

**LAN Access:**
- Cilium L2 already configured — services get real LAN IPs
- Need DNS to resolve `*.openchoreo.local` to LoadBalancer IP
- Options: local DNS server, nip.io/sslip.io, /etc/hosts

**FluxCD Structure:**
- clusters/ → bootstrap
- flux/systems/ → monitoring, networking
- flux/apps/ → workloads
- Monitoring should be FluxCD-managed (not Pulumi) since it's K8s-native

**Dashboards:**
- Cluster Overview (ID 15760)
- Pod Resources (ID 9765)
- Node Exporter (ID 1860)
- Gateway API State (ID 19433)
- Plus custom: OpenChoreo health, cert-manager, Longhorn

## Open Questions
1. DNS strategy for LAN access (router DNS, Pi-hole, /etc/hosts, nip.io?)
2. Monitoring: enable existing OpenChoreo observability plane vs standalone kube-prometheus-stack vs both?
3. FluxCD: what apps/workloads beyond OpenChoreo?
4. GitHub PAT for private repo or make repo public?
5. Which services specifically need HTTPRoutes? (existing OpenChoreo services already have them)
6. Do existing OpenChoreo HTTPRoutes work from LAN today? (they should if DNS resolves)

## Scope Boundaries
- INCLUDE: FluxCD enablement, monitoring, HTTPRoutes for LAN access
- EXCLUDE: (pending discussion)

## Key Insight
The existing OpenChoreo services (backstage, API, thunder) ALREADY have HTTPRoutes and their Gateway services should already have LoadBalancer IPs from Cilium L2. The real blocker for LAN access may simply be DNS resolution of `*.openchoreo.local` from other machines. Need to verify if this is already working or not.
