#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "kubernetes>=31.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Discover all user-facing services on the OpenChoreo cluster and export access info.

Outputs:
  - Pretty table to stdout
  - services.md   — Markdown reference
  - etc-hosts.txt — Copy-paste block for /etc/hosts
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from kubernetes import client, config
from rich.console import Console
from rich.table import Table

# ── Config ──────────────────────────────────────────────────────────────────

KUBECONFIG = "pulumi/talos-cluster-baremetal/outputs/kubeconfig"
CONTEXT = "admin@openchoreo"

GATEWAY_IPS: dict[str, str] = {
    "openchoreo-control-plane": "192.168.0.10",
    "openchoreo-data-plane": "192.168.0.11",
    "openchoreo-observability-plane": "192.168.0.12",
}

GATEWAY_PORTS: dict[str, dict[str, int]] = {
    "openchoreo-control-plane": {"http": 8080, "https": 8443},
    "openchoreo-data-plane": {"http": 19080, "https": 19443},
    "openchoreo-observability-plane": {"http": 11080, "https": 11085},
}

# Services we skip (not user-facing)
SKIP_HOSTNAMES = {"*.openchoreo.local"}


@dataclass
class ServiceInfo:
    name: str
    hostname: str
    gateway_ns: str
    gateway_ip: str
    http_port: int
    https_port: int
    http_url: str = ""
    https_url: str = ""
    http_status: int = 0
    https_status: int = 0
    description: str = ""


def load_k8s() -> client.CustomObjectsApi:
    config.load_kube_config(config_file=KUBECONFIG, context=CONTEXT)
    return client.CustomObjectsApi()


def discover_httproutes(api: client.CustomObjectsApi) -> list[ServiceInfo]:
    """Fetch all HTTPRoutes across namespaces and map to accessible services."""
    routes = api.list_cluster_custom_object(
        group="gateway.networking.k8s.io",
        version="v1",
        plural="httproutes",
    )

    services: list[ServiceInfo] = []
    for route in routes.get("items", []):
        meta = route["metadata"]
        spec = route["spec"]
        hostnames = spec.get("hostnames", [])

        for hostname in hostnames:
            if hostname in SKIP_HOSTNAMES:
                continue

            # Find which gateway this route targets
            gateway_ns = ""
            for ref in spec.get("parentRefs", []):
                gateway_ns = ref.get("namespace", meta.get("namespace", ""))
                break

            if gateway_ns not in GATEWAY_IPS:
                continue

            ip = GATEWAY_IPS[gateway_ns]
            ports = GATEWAY_PORTS[gateway_ns]

            # Backend info for description
            backends = []
            for rule in spec.get("rules", []):
                for br in rule.get("backendRefs", []):
                    backends.append(f"{br.get('namespace', meta['namespace'])}/{br['name']}:{br.get('port', '?')}")

            svc = ServiceInfo(
                name=meta["name"],
                hostname=hostname,
                gateway_ns=gateway_ns,
                gateway_ip=ip,
                http_port=ports["http"],
                https_port=ports["https"],
                http_url=f"http://{hostname}:{ports['http']}",
                https_url=f"https://{hostname}:{ports['https']}",
                description=", ".join(backends),
            )
            services.append(svc)

    # Sort: control plane first, then data, then observability
    order = {"openchoreo-control-plane": 0, "openchoreo-data-plane": 1, "openchoreo-observability-plane": 2}
    services.sort(key=lambda s: (order.get(s.gateway_ns, 9), s.hostname))
    return services


def probe(url: str, timeout: int = 5) -> int:
    """Curl a URL and return HTTP status code. 0 = unreachable."""
    try:
        r = subprocess.run(
            ["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}",
             "--connect-timeout", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 2,
        )
        return int(r.stdout.strip())
    except Exception:
        return 0


def probe_all(services: list[ServiceInfo]) -> None:
    for svc in services:
        svc.http_status = probe(svc.http_url)
        svc.https_status = probe(svc.https_url)


def status_icon(code: int) -> str:
    if code == 0:
        return "❌ down"
    if 200 <= code < 400:
        return f"✅ {code}"
    if code in (401, 403):
        return f"🔒 {code}"
    return f"⚠️  {code}"


def print_table(services: list[ServiceInfo]) -> None:
    console = Console()
    table = Table(title="OpenChoreo Services — LAN Access", show_lines=True)
    table.add_column("Service", style="bold cyan")
    table.add_column("HTTP URL", style="blue")
    table.add_column("HTTP", justify="center")
    table.add_column("HTTPS URL", style="blue")
    table.add_column("HTTPS", justify="center")
    table.add_column("Gateway IP")
    table.add_column("Backend")

    for svc in services:
        table.add_row(
            svc.name,
            svc.http_url,
            status_icon(svc.http_status),
            svc.https_url,
            status_icon(svc.https_status),
            svc.gateway_ip,
            svc.description,
        )

    console.print(table)


def export_etc_hosts(services: list[ServiceInfo], path: Path) -> None:
    """Generate /etc/hosts lines grouped by IP."""
    ip_to_hosts: dict[str, list[str]] = {}
    for svc in services:
        ip_to_hosts.setdefault(svc.gateway_ip, []).append(svc.hostname)

    lines = [
        "# ── OpenChoreo services (/etc/hosts) ──",
        "# Generated by scripts/discover-services.py",
        "# Add these lines to /etc/hosts:",
        "#   sudo tee -a /etc/hosts < etc-hosts.txt",
        "#",
        "# macOS treats .local as mDNS, so /etc/resolver won't work.",
        "# /etc/hosts is the reliable approach.",
        "",
    ]
    for ip, hosts in sorted(ip_to_hosts.items()):
        lines.append(f"{ip}  {' '.join(sorted(hosts))}")
    lines.append("")

    path.write_text("\n".join(lines))
    print(f"\n📄 /etc/hosts entries written to: {path}")


def export_markdown(services: list[ServiceInfo], path: Path) -> None:
    lines = [
        "# OpenChoreo Services — LAN Access Guide",
        "",
        "> Auto-generated by `scripts/discover-services.py`",
        "",
        "## Prerequisites",
        "",
        "Add to `/etc/hosts` (macOS `.local` TLD needs this):",
        "",
        "```bash",
        "sudo tee -a /etc/hosts << 'HOSTS'",
    ]

    ip_to_hosts: dict[str, list[str]] = {}
    for svc in services:
        ip_to_hosts.setdefault(svc.gateway_ip, []).append(svc.hostname)
    for ip, hosts in sorted(ip_to_hosts.items()):
        lines.append(f"{ip}  {' '.join(sorted(hosts))}")

    lines += [
        "HOSTS",
        "```",
        "",
        "## Services",
        "",
        "| Service | HTTP URL | HTTPS URL | Status | Backend |",
        "|---------|----------|-----------|--------|---------|",
    ]

    for svc in services:
        h = status_icon(svc.http_status).replace("|", "\\|")
        lines.append(
            f"| **{svc.name}** | {svc.http_url} | {svc.https_url} | {h} | `{svc.description}` |"
        )

    lines += [
        "",
        "## Gateway Map",
        "",
        "| Gateway | IP | HTTP Port | HTTPS Port |",
        "|---------|-----|-----------|------------|",
        "| Control Plane | 192.168.0.10 | 8080 | 8443 |",
        "| Data Plane | 192.168.0.11 | 19080 | 19443 |",
        "| Observability | 192.168.0.12 | 11080 | 11085 |",
        "",
        "## Quick Test",
        "",
        "```bash",
        "# Backstage UI",
        "open http://openchoreo.local:8080",
        "",
        "# Thunder (auth server)",
        "open http://thunder.openchoreo.local:8080/console",
        "",
        "# Longhorn storage UI",
        "open http://longhorn.openchoreo.local:8080",
        "",
        "# Hubble network observability",
        "open http://hubble.openchoreo.local:8080",
        "",
        "# Argo workflows",
        "open http://argo.openchoreo.local:8080",
        "",
        "# Prometheus metrics",
        "open http://prometheus.openchoreo.local:11080",
        "```",
        "",
    ]

    path.write_text("\n".join(lines))
    print(f"📄 Service guide written to: {path}")


def main() -> None:
    print("🔍 Discovering services from cluster...")
    api = load_k8s()
    services = discover_httproutes(api)
    print(f"   Found {len(services)} routed services\n")

    print("🏓 Probing accessibility from this machine...")
    probe_all(services)

    print_table(services)

    out_dir = Path("docs")
    out_dir.mkdir(exist_ok=True)

    export_etc_hosts(services, out_dir / "etc-hosts.txt")
    export_markdown(services, out_dir / "services.md")

    # Also dump as JSON for automation
    data = [
        {
            "name": s.name,
            "hostname": s.hostname,
            "http_url": s.http_url,
            "https_url": s.https_url,
            "http_status": s.http_status,
            "https_status": s.https_status,
            "gateway_ip": s.gateway_ip,
        }
        for s in services
    ]
    json_path = out_dir / "services.json"
    json_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"📄 JSON export written to: {json_path}")


if __name__ == "__main__":
    main()
