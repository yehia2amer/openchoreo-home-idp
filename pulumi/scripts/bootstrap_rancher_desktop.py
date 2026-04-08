#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# ///
"""Bootstrap Rancher Desktop for OpenChoreo and run Pulumi up.

Usage:
    uv run scripts/bootstrap_rancher_desktop.py

Assumes Rancher Desktop is already running with Kubernetes enabled.
This script validates the cluster, selects the rancher-desktop Pulumi stack,
and runs `pulumi up`.
"""

import shutil
import subprocess
import sys
from pathlib import Path

PULUMI_DIR = Path(__file__).resolve().parent.parent


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
    kubectl = check_tool("kubectl")
    pulumi = check_tool("pulumi")

    # Verify cluster is reachable
    print("==> Verifying Rancher Desktop cluster...")
    run([kubectl, "--context", "rancher-desktop", "cluster-info"])
    run([kubectl, "--context", "rancher-desktop", "get", "nodes"])

    # Run Pulumi
    print("==> Running Pulumi up (rancher-desktop stack)...")
    pulumi_cmd = [
        pulumi,
        "up",
        "--yes",
        "--stack",
        "rancher-desktop",
    ]
    run(pulumi_cmd, cwd=str(PULUMI_DIR))

    # Print results
    print()
    print("==> OpenChoreo deployed successfully on Rancher Desktop!")
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
        (" Data Plane Gateway", " http://openchoreo.localhost:19080"),
    ]:
        print(row.format(label, value))
    print("\u2560" + "\u2550" * L + "\u256c" + "\u2550" * R + "\u2563")
    secret_hint = " (pulumi stack output --show-secrets)"
    for label, value in [
        (" OpenBao Token", secret_hint),
        (" Default Login", " admin@openchoreo.dev / Admin@123"),
    ]:
        print(row.format(label, value))
    print("\u255a" + "\u2550" * L + "\u2569" + "\u2550" * R + "\u255d")


if __name__ == "__main__":
    main()
