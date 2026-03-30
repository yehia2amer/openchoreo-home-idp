#!/usr/bin/env -S uv run
"""Bootstrap Talos bare-metal cluster and then deploy OpenChoreo app stack."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLUSTER_DIR = ROOT / "talos-cluster-baremetal"
APP_DIR = ROOT
DEFAULT_CLUSTER_STACK = "dev"
DEFAULT_CLUSTER_PASSPHRASE = "openchoreo-talos-baremetal-dev"
DEFAULT_APP_STACK = "talos-baremetal"


def check_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        print(f"ERROR: '{name}' not found in PATH. Please install it first.")
        sys.exit(1)
    return path


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print(f"  $ {' '.join(cmd)}")
    env = dict(os.environ)
    env.setdefault("PULUMI_CONFIG_PASSPHRASE", DEFAULT_CLUSTER_PASSPHRASE)
    return subprocess.run(cmd, check=True, cwd=str(cwd) if cwd else None, text=True, capture_output=False, env=env)


def get_stack_output(stack: str, key: str, cwd: Path) -> str:
    env = dict(os.environ)
    env.setdefault("PULUMI_CONFIG_PASSPHRASE", DEFAULT_CLUSTER_PASSPHRASE)
    result = subprocess.run(
        ["pulumi", "stack", "output", key, "--stack", stack, "--json"],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return json.loads(result.stdout)


def ensure_stack_initialized() -> None:
    env = dict(os.environ)
    env.setdefault("PULUMI_CONFIG_PASSPHRASE", DEFAULT_CLUSTER_PASSPHRASE)
    result = subprocess.run(
        ["pulumi", "stack", "ls", "--json"],
        cwd=str(CLUSTER_DIR),
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    stacks = json.loads(result.stdout)
    if any(stack.get("name") == DEFAULT_CLUSTER_STACK for stack in stacks):
        return
    run(["pulumi", "stack", "init", DEFAULT_CLUSTER_STACK, "--secrets-provider", "passphrase"], cwd=CLUSTER_DIR)


def write_text_file(path_str: str, content: str) -> str:
    path = Path(path_str).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return str(path)


def ensure_kubeconfig_file(stack: str) -> tuple[str, str]:
    kubeconfig_raw = get_stack_output(stack, "kubeconfig_raw", CLUSTER_DIR)
    kubeconfig_path = get_stack_output(stack, "kubeconfig_path", CLUSTER_DIR)
    kubeconfig_context = get_stack_output(stack, "kubeconfig_context", CLUSTER_DIR)
    write_text_file(kubeconfig_path, kubeconfig_raw)
    return kubeconfig_path, kubeconfig_context


def ensure_talosconfig_file(stack: str) -> str:
    talosconfig_raw = get_stack_output(stack, "talosconfig_raw", CLUSTER_DIR)
    talosconfig_path = get_stack_output(stack, "talosconfig_path", CLUSTER_DIR)
    parsed = yaml.safe_load(talosconfig_raw)
    write_text_file(talosconfig_path, yaml.safe_dump(parsed, sort_keys=False))
    return talosconfig_path


def main() -> None:
    check_tool("pulumi")

    print("==> Bootstrapping Talos bare-metal cluster with Pulumi...")
    ensure_stack_initialized()
    run(["pulumi", "up", "--yes", "--stack", DEFAULT_CLUSTER_STACK], cwd=CLUSTER_DIR)

    kubeconfig_path, kubeconfig_context = ensure_kubeconfig_file(DEFAULT_CLUSTER_STACK)
    talosconfig_path = ensure_talosconfig_file(DEFAULT_CLUSTER_STACK)

    print(f"    Wrote kubeconfig to {kubeconfig_path}")
    print(f"    Wrote talosconfig to {talosconfig_path}")

    print("==> Deploying OpenChoreo on Talos bare metal...")
    run(
        [
            "pulumi",
            "up",
            "--yes",
            "--stack",
            DEFAULT_APP_STACK,
            "--config",
            f"openchoreo:kubeconfig_path={kubeconfig_path}",
            "--config",
            f"openchoreo:kubeconfig_context={kubeconfig_context}",
        ],
        cwd=APP_DIR,
    )


if __name__ == "__main__":
    main()
