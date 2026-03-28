#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "httpx>=0.25.0",
#   "pyyaml>=6.0",
# ]
# requires-python = ">=3.9"
# ///
"""Bootstrap k3d cluster for OpenChoreo and run Pulumi up.

Usage:
    uv run scripts/bootstrap_k3d.py [cluster-name]
    uv run scripts/bootstrap_k3d.py [cluster-name] --cilium

Cross-platform Python replacement for the bash bootstrap script.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx  # ty: ignore[unresolved-import]
import yaml

CONFIG_URL = (
    "https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/single-cluster/config.yaml"
)

PULUMI_DIR = Path(__file__).resolve().parent.parent

# Script mounted into k3d containers to prepare BPF/cgroup mounts for Cilium.
# k3d executes /bin/k3d-entrypoint-*.sh scripts before starting k3s.
K3D_ENTRYPOINT_CILIUM = """\
#!/bin/sh
set -e
echo "Mounting bpf on node"
mount bpffs -t bpf /sys/fs/bpf
mount --make-shared /sys/fs/bpf
echo "Mounting cgroups v2 to /run/cilium/cgroupv2 on node"
mkdir -p /run/cilium/cgroupv2
mount -t cgroup2 none /run/cilium/cgroupv2
mount --make-shared /run/cilium/cgroupv2/
"""


def check_tool(name: str) -> str:
    """Verify a CLI tool exists and return its path."""
    path = shutil.which(name)
    if not path:
        print(f"ERROR: '{name}' not found in PATH. Please install it first.")
        sys.exit(1)
    return path


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, printing it and failing on error."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def main():
    cluster_name = sys.argv[1] if len(sys.argv) > 1 else "openchoreo"

    # Check required tools
    k3d = check_tool("k3d")
    kubectl = check_tool("kubectl")
    pulumi = check_tool("pulumi")

    # Download k3d config
    print("==> Downloading k3d config...")
    resp = httpx.get(CONFIG_URL, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    config = yaml.safe_load(resp.text)

    # Patch cluster name
    if cluster_name != "openchoreo":
        config["metadata"]["name"] = cluster_name
        print(f"    Patched cluster name to '{cluster_name}'")

    # Patch for Cilium: disable Flannel, network-policy, kube-proxy; disable k3d LB;
    # mount BPF entrypoint script for Cilium to work in k3d containers.
    enable_cilium = "--cilium" in sys.argv
    if enable_cilium:
        extra_args = config.setdefault("options", {}).setdefault("k3s", {}).setdefault("extraArgs", [])
        extra_args.append({"arg": "--flannel-backend=none", "nodeFilters": ["server:*"]})
        extra_args.append({"arg": "--disable-network-policy", "nodeFilters": ["server:*"]})

        # Write the BPF/cgroup mount script and mount it into all k3d containers.
        # k3d auto-executes /bin/k3d-entrypoint-*.sh before starting k3s.
        entrypoint_path = Path(tempfile.gettempdir()) / "k3d-entrypoint-cilium.sh"
        entrypoint_path.write_text(K3D_ENTRYPOINT_CILIUM)
        entrypoint_path.chmod(0o755)
        volumes = config.setdefault("volumes", [])
        volumes.append(
            {
                "volume": f"{entrypoint_path}:/bin/k3d-entrypoint-cilium.sh",
                "nodeFilters": ["all"],
            }
        )

        print("    Patched config for Cilium CNI (disabled Flannel + network-policy)")
        print(f"    Mounted BPF entrypoint script: {entrypoint_path}")

    # Mount host CA certificates into k3d nodes (fixes TLS issues with corporate proxies)
    if sys.platform == "darwin":
        ca_bundle = Path(tempfile.gettempdir()) / "k3d-ca-bundle.pem"
        bundle_parts = []
        # System keychain certs (includes corporate/proxy CAs)
        result = subprocess.run(
            ["security", "find-certificate", "-a", "-p", "/Library/Keychains/System.keychain"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            bundle_parts.append(result.stdout)
        # Standard macOS CA bundle
        system_pem = Path("/etc/ssl/cert.pem")
        if system_pem.exists():
            bundle_parts.append(system_pem.read_text())
        if bundle_parts:
            ca_bundle.write_text("\n".join(bundle_parts))
            volumes = config.setdefault("volumes", [])
            volumes.append(
                {
                    "volume": f"{ca_bundle}:/etc/ssl/certs/ca-certificates.crt",
                    "nodeFilters": ["server:*"],
                }
            )
            print(f"    Mounted host CA bundle ({ca_bundle}) into k3d nodes")

    # Write config to temp file
    config_file = Path(tempfile.gettempdir()) / f"k3d-{cluster_name}-config.yaml"
    config_file.write_text(yaml.dump(config, default_flow_style=False), encoding="utf-8")
    print(f"    Config saved to {config_file}")

    # Check if cluster exists
    print(f"==> Creating k3d cluster '{cluster_name}'...")
    result = subprocess.run(
        [k3d, "cluster", "list", "-o", "json"],
        capture_output=True,
        text=True,
    )
    import json

    clusters = json.loads(result.stdout) if result.stdout.strip() else []
    exists = any(c.get("name") == cluster_name for c in clusters)

    if exists:
        print(f"    Cluster '{cluster_name}' already exists, skipping creation.")
    else:
        run([k3d, "cluster", "create", "--config", str(config_file)])

    # Verify cluster
    print("==> Verifying cluster...")
    run([kubectl, "cluster-info"])
    run([kubectl, "get", "nodes"])

    # Run Pulumi
    print("==> Running Pulumi up...")
    pulumi_cmd = [
        pulumi,
        "up",
        "--yes",
        "--stack",
        "dev",
        "--config",
        f"openchoreo-k3d:kubeconfig_context=k3d-{cluster_name}",
        "--config",
        f"openchoreo-k3d:k3d_cluster_name={cluster_name}",
    ]
    if enable_cilium:
        pulumi_cmd.extend(["--config", "openchoreo-k3d:enable_cilium=true"])
    run(pulumi_cmd, cwd=str(PULUMI_DIR))

    # Print results
    print()
    print(f"==> OpenChoreo deployed successfully on k3d cluster '{cluster_name}'!")
    print()
    L, R, W = 30, 31, 62
    row = "\u2551" + "{0}".ljust(L) + "\u2551" + "{1}".ljust(R) + "\u2551"
    print("\u2554" + "\u2550" * W + "\u2557")
    print("\u2551" + "OpenChoreo v1.0.0 \u2014 Deployed".center(W) + "\u2551")
    print("\u2560" + "\u2550" * L + "\u2566" + "\u2550" * R + "\u2563")
    for label, value in [
        (" Backstage UI", " http://openchoreo.localhost:8080"),
        (" API", " http://api.openchoreo.localhost:8080"),
        (" Thunder (IdP)", " http://thunder.openchoreo.localhost:8080"),
        (" Argo Workflows", " http://localhost:10081"),
        (" Observer API", " http://observer.openchoreo.localhost:11080"),
        (" OpenSearch Dashboards", " http://localhost:11081"),
        (" Data Plane Gateway", " http://openchoreo.localhost:19080"),
    ]:
        print(row.format(label, value))
    print("\u2560" + "\u2550" * L + "\u256c" + "\u2550" * R + "\u2563")
    secret_hint = " (pulumi stack output --show-secrets)"
    for label, value in [
        (" OpenSearch User", " admin"),
        (" OpenSearch Pass", secret_hint),
        (" OpenBao Token", secret_hint),
        (" Default Login", " admin@openchoreo.dev / Admin@123"),
    ]:
        print(row.format(label, value))
    print("\u255a" + "\u2550" * L + "\u2569" + "\u2550" * R + "\u255d")


if __name__ == "__main__":
    main()
