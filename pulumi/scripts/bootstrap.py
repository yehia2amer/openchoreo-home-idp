#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "httpx>=0.25.0",
#   "pyyaml>=6.0",
# ]
# requires-python = ">=3.9"
# ///
"""Bootstrap OpenChoreo on any supported platform.

Usage:
    uv run scripts/bootstrap.py k3d [cluster-name]
    uv run scripts/bootstrap.py rancher-desktop

Dispatches to the platform-specific bootstrap script.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

PLATFORMS = {
    "k3d": "bootstrap_k3d.py",
    "rancher-desktop": "bootstrap_rancher_desktop.py",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: uv run scripts/bootstrap.py <platform> [args...]")
        print(f"Supported platforms: {', '.join(sorted(PLATFORMS))}")
        sys.exit(0 if "--help" in sys.argv else 1)

    platform = sys.argv[1].lower().strip()
    if platform not in PLATFORMS:
        print(f"ERROR: Unknown platform '{platform}'.")
        print(f"Supported: {', '.join(sorted(PLATFORMS))}")
        sys.exit(1)

    script = SCRIPTS_DIR / PLATFORMS[platform]
    extra_args = sys.argv[2:]

    print(f"==> Bootstrapping OpenChoreo on {platform}...")
    cmd = ["uv", "run", str(script)] + extra_args
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
