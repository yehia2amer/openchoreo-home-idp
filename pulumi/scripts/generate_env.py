#!/usr/bin/env python3
"""Generate .env file from Pulumi stack outputs.

Run after `pulumi up` to create a .env file with deployment URLs and credentials.

Usage:
    python scripts/generate_env.py
    # or
    pulumi stack output --json | python scripts/generate_env.py --stdin
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_outputs_from_pulumi() -> dict:
    result = subprocess.run(
        ["pulumi", "stack", "output", "--json", "--show-secrets"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def get_outputs_from_stdin() -> dict:
    return json.load(sys.stdin)


def generate_env(outputs: dict, env_path: Path) -> None:
    env_vars = {
        "BACKSTAGE_URL": outputs.get("backstage_url", ""),
        "API_URL": outputs.get("api_url", ""),
        "THUNDER_URL": outputs.get("thunder_url", ""),
        "ARGO_WORKFLOWS_URL": outputs.get("argo_workflows_url", ""),
        "OBSERVER_URL": outputs.get("observer_url", ""),
        "OPENSEARCH_DASHBOARDS_URL": outputs.get("opensearch_dashboards_url", ""),
        "DATA_PLANE_GATEWAY_HTTP": outputs.get("data_plane_gateway_http", ""),
        "DATA_PLANE_GATEWAY_HTTPS": outputs.get("data_plane_gateway_https", ""),
        "OPENSEARCH_USERNAME": outputs.get("opensearch_username", ""),
        "OPENSEARCH_PASSWORD": outputs.get("opensearch_password", ""),
        "OPENBAO_ROOT_TOKEN": outputs.get("openbao_root_token", ""),
        "KUBECONFIG_CONTEXT": outputs.get("kubeconfig_context", ""),
        "DOMAIN_BASE": outputs.get("domain_base", ""),
        "OPENCHOREO_VERSION": outputs.get("openchoreo_version", ""),
        "PLATFORM": outputs.get("platform", ""),
        "EDITION": outputs.get("edition", ""),
        "CILIUM_ENABLED": str(outputs.get("cilium_enabled", False)).lower(),
        "FLUX_ENABLED": str(outputs.get("flux_enabled", False)).lower(),
        "OBSERVABILITY_ENABLED": str(outputs.get("observability_enabled", False)).lower(),
    }

    namespaces = outputs.get("namespaces", {})
    if namespaces:
        env_vars["NS_CONTROL_PLANE"] = namespaces.get("control_plane", "")
        env_vars["NS_DATA_PLANE"] = namespaces.get("data_plane", "")
        env_vars["NS_WORKFLOW_PLANE"] = namespaces.get("workflow_plane", "")
        env_vars["NS_OBSERVABILITY_PLANE"] = namespaces.get("observability_plane", "")

    lines = [f"{k}={v}" for k, v in sorted(env_vars.items()) if v]
    env_path.write_text("\n".join(lines) + "\n")
    print(f"Generated {env_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate .env from Pulumi outputs")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output path")
    args = parser.parse_args()

    if args.output:
        env_path = args.output
    else:
        env_path = Path(__file__).resolve().parent.parent / ".env"

    if args.stdin:
        outputs = get_outputs_from_stdin()
    else:
        outputs = get_outputs_from_pulumi()

    generate_env(outputs, env_path)


if __name__ == "__main__":
    main()
