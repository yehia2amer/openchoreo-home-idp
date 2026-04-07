# TrueNAS Keepalived Setup Guide

This documents the manual configuration performed on the TrueNAS SCALE server (`192.168.0.129`) to deploy keepalived as a VRRP backup for the DNS VIP `192.168.0.53`. The primary VRRP node runs on the Talos K8s cluster; TrueNAS is the failover backup.

## Architecture

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  Talos K8s (192.168.0.100)  │     │  TrueNAS (192.168.0.129)   │
│                             │     │                             │
│  keepalived (DaemonSet)     │     │  keepalived (Docker app)    │
│  state: MASTER              │     │  state: BACKUP              │
│  priority: 80               │     │  priority: 50               │
│  interface: enp7s0          │     │  interface: eno1             │
│  health: 192.168.0.100:53   │     │  health: 192.168.0.129:53   │
│                             │     │                             │
│  AdGuard Home (hostNetwork) │     │  AdGuard Home (Docker app)  │
│  bind: 192.168.0.100,       │     │  bind: 192.168.0.129,       │
│        192.168.0.53         │     │        192.168.0.53         │
└──────────────┬──────────────┘     └──────────────┬──────────────┘
               │  VRRP (virtual_router_id 53)      │
               └──────────┬───────────────────────-─┘
                          │
                  VIP: 192.168.0.53
                  (Router DHCP → all clients)
```

**Normal operation**: K8s owns the VIP and serves DNS.
**Failover**: K8s keepalived dies → TrueNAS promotes to MASTER → TrueNAS AdGuard serves DNS on the VIP.

## Prerequisites

- TrueNAS SCALE 25.04+ (Electric Eel — uses Docker Compose for apps)
- AdGuard Home already running on TrueNAS, bound to `192.168.0.129:53` and `192.168.0.53:53`
- Network interface `eno1` with IP `192.168.0.129`

## Files

| File | Location on TrueNAS | Purpose |
|------|---------------------|---------|
| `keepalived.conf` | `/mnt/AmerData/appdata/keepalived/keepalived.conf` | VRRP + health check config |
| Docker Compose | Managed via TrueNAS API (Custom App) | Container definition |

Both files are stored in this repo under `docs/truenas/` for reference.

## Step-by-Step Setup

### 1. Create the config directory

```bash
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/filesystem/mkdir/' \
  -H 'Content-Type: application/json' \
  -d '{"path": "/mnt/AmerData/appdata/keepalived"}'
```

### 2. Upload keepalived.conf

```bash
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/filesystem/put/' \
  -F 'data={"path":"/mnt/AmerData/appdata/keepalived/keepalived.conf"}' \
  -F "file=@docs/truenas/keepalived.conf"
```

### 3. Create the Custom App

```bash
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/app/create/' \
  -H 'Content-Type: application/json' \
  -d '{
    "custom_app": true,
    "app_name": "keepalived",
    "custom_compose_config_string": "<contents of docker-compose.keepalived.yaml>"
  }'
```

This returns an async job ID. Poll for completion:

```bash
curl -s -k -u 'USER:PASS' \
  'https://192.168.0.129/api/v2.0/core/get_jobs?id=<JOB_ID>'
```

### 4. Start the app

The app is STOPPED after creation. Start it:

```bash
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/app/start/' \
  -H 'Content-Type: application/json' \
  -d '"keepalived"'
```

### 5. Verify

Check that TrueNAS keepalived enters BACKUP state (K8s should be MASTER with priority 80 > 50):

```bash
# TrueNAS should NOT have the VIP when K8s is healthy
curl -s -k -u 'USER:PASS' \
  'https://192.168.0.129/api/v2.0/interface?name=eno1' | python3 -c "
import sys,json
data = json.load(sys.stdin)
for iface in data:
    for sa in iface.get('state',{}).get('aliases',[]):
        addr = sa.get('address','')
        if '.' in str(addr): print(f'  {addr}')
"
# Expected: only 192.168.0.129 (NOT 192.168.0.53)
```

## Key Design Decisions

### osixia entrypoint bypass

The `osixia/keepalived:2.0.20` image has a custom entrypoint that runs `sed -i` on config files during startup. This fails on bind-mounted files (`Resource busy` error). The solution is to bypass the osixia entrypoint entirely and run keepalived directly:

```yaml
entrypoint:
  - /usr/local/sbin/keepalived    # NOT /usr/sbin/keepalived (doesn't exist in osixia)
  - --dont-fork
  - --log-console
  - --log-detail
  - --dump-conf
  - -f
  - /etc/keepalived/keepalived.conf
```

The binary path in the osixia image is `/usr/local/sbin/keepalived`, not the standard `/usr/sbin/keepalived`.

### weight 0 health check strategy

The `vrrp_script` uses `weight 0` (not a negative weight). This means:

- **Script succeeds**: keepalived advertises its configured priority (50 for TrueNAS)
- **Script fails** (after `fall 3` consecutive failures): keepalived advertises **priority 0** → immediate failover

This is safer than negative weights (e.g., `weight -25`) where arithmetic could still leave a broken node with a non-zero priority, causing unpredictable election outcomes.

### Specific IP binds for AdGuard

AdGuard on TrueNAS binds to `['192.168.0.129', '192.168.0.53']` — not `0.0.0.0`. This avoids conflicts with Docker's internal dnsmasq on TrueNAS which listens on `10.92.243.x:53`. Binding `0.0.0.0:53` causes a fatal `address already in use` error.

AdGuard can bind to the VIP `192.168.0.53` even when TrueNAS doesn't own the IP — the socket just starts receiving traffic when VRRP assigns the VIP.

### nopreempt behavior

The K8s keepalived does NOT use `nopreempt`, so after a failover-and-recovery cycle:
1. K8s keepalived dies → TrueNAS promotes to MASTER
2. K8s keepalived restarts → enters BACKUP (TrueNAS has `nopreempt`)
3. To restore K8s as MASTER: bounce TrueNAS keepalived (`app/stop` then `app/start`)

This prevents flapping during K8s node reboots or brief network partitions.

## Updating the Config

To update keepalived.conf:

```bash
# 1. Upload new config
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/filesystem/put/' \
  -F 'data={"path":"/mnt/AmerData/appdata/keepalived/keepalived.conf"}' \
  -F "file=@docs/truenas/keepalived.conf"

# 2. Stop the app
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/app/stop/' \
  -H 'Content-Type: application/json' -d '"keepalived"'

# 3. Start the app (reads new config)
curl -s -k -u 'USER:PASS' -X POST \
  'https://192.168.0.129/api/v2.0/app/start/' \
  -H 'Content-Type: application/json' -d '"keepalived"'
```

## Updating the Docker Compose

To change the container config (image version, volumes, capabilities):

```bash
curl -s -k -u 'USER:PASS' -X PUT \
  'https://192.168.0.129/api/v2.0/app/id/keepalived/' \
  -H 'Content-Type: application/json' \
  -d '{
    "custom_compose_config_string": "<new docker-compose YAML as string>"
  }'
```

## Failover Test Procedure

```bash
# 1. Verify normal state (K8s MASTER)
dig @192.168.0.53 google.com +short

# 2. Kill K8s keepalived
kubectl delete pod -n keepalived -l app.kubernetes.io/name=keepalived --force --grace-period=0

# 3. Wait 8 seconds for VRRP failover

# 4. Verify TrueNAS took over
dig @192.168.0.53 google.com +short   # Should still resolve
# Check TrueNAS now owns VIP:
curl -s -k -u 'USER:PASS' 'https://192.168.0.129/api/v2.0/interface?name=eno1'
# Should show 192.168.0.53 in aliases

# 5. K8s keepalived auto-respawns (DaemonSet) but enters BACKUP

# 6. Restore K8s as MASTER: bounce TrueNAS keepalived
curl -s -k -u 'USER:PASS' -X POST 'https://192.168.0.129/api/v2.0/app/stop/' \
  -H 'Content-Type: application/json' -d '"keepalived"'
sleep 8
curl -s -k -u 'USER:PASS' -X POST 'https://192.168.0.129/api/v2.0/app/start/' \
  -H 'Content-Type: application/json' -d '"keepalived"'

# 7. Verify K8s reclaimed MASTER
dig @192.168.0.53 google.com +short
```

## TrueNAS API Reference (used in this setup)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v2.0/filesystem/mkdir/` | POST | Create directories (no `-p`, must create parents manually) |
| `/api/v2.0/filesystem/put/` | POST | Upload files (multipart) |
| `/api/v2.0/filesystem/get/` | POST | Download file contents |
| `/api/v2.0/filesystem/listdir/` | POST | List directory contents |
| `/api/v2.0/app/create/` | POST | Create custom Docker Compose app (async, returns job ID) |
| `/api/v2.0/app/start/` | POST | Start an app (async) |
| `/api/v2.0/app/stop/` | POST | Stop an app (async) |
| `/api/v2.0/app/id/<name>/` | PUT | Update app config (Docker Compose string) |
| `/api/v2.0/core/get_jobs?id=<id>` | GET | Poll async job status |
| `/api/v2.0/interface?name=<iface>` | GET | Check network interface IPs |

## Troubleshooting

**Keepalived won't start**: Check that the config file exists and is readable. The volume mount is `:ro` so the file must exist before the container starts.

**VIP not assigned**: Check logs — the most common issue is the wrong network interface name. Use `/api/v2.0/interface` to find the correct one.

**DNS doesn't work on failover**: AdGuard must bind to the VIP address (`192.168.0.53`). Check `bind_hosts` in `/mnt/.ix-apps/app_mounts/adguard-home/config/AdGuardHome.yaml`.

**Both nodes claim MASTER**: Check `virtual_router_id` matches on both nodes (must be `53`), and `auth_pass` matches. Also verify multicast/VRRP packets aren't being blocked by a firewall.

**Spinning disks active**: The keepalived config is stored on the `AmerData` pool (spinning disks). This is a 521-byte file read once at container start — it should not cause continuous disk activity. If disks are spinning, check AdGuard logs/work directories or other apps on the HDD pool.
