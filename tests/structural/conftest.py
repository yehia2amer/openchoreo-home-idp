"""Fixtures for structural tests validating the Kustomize platform architecture."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

PLATFORMS = ["baremetal", "k3d", "gcp", "aws", "azure"]
WAVES = [
    "00-crds",
    "01-prerequisites",
    "02-tls",
    "03-platform",
    "04-registration",
    "05-network",
]


@pytest.fixture(scope="session")
def gitops_repo_path() -> Path:
    """Root of the gitops repository."""
    raw = os.environ.get("GITOPS_REPO_PATH", "/tmp/openchoreo-gitops")
    path = Path(raw)
    if not path.is_dir():
        pytest.skip(f"GitOps repo not found at {path}")
    return path


@pytest.fixture(scope="session")
def platforms_dir(gitops_repo_path: Path) -> Path:
    d = gitops_repo_path / "infrastructure" / "platforms"
    if not d.is_dir():
        pytest.skip(f"platforms directory not found: {d}")
    return d


@pytest.fixture(scope="session")
def components_dir(gitops_repo_path: Path) -> Path:
    d = gitops_repo_path / "infrastructure" / "components"
    if not d.is_dir():
        pytest.skip(f"components directory not found: {d}")
    return d


def kustomize_build(path: Path) -> tuple[bool, str]:
    """Run ``kustomize build <path>`` and return (success, output).

    Uses subprocess with a list of arguments (no shell=True).
    """
    try:
        result = subprocess.run(
            ["kustomize", "build", str(path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr
    except FileNotFoundError:
        pytest.skip("kustomize binary not found on PATH")
        return False, ""  # unreachable, keeps type-checker happy
    except subprocess.TimeoutExpired:
        return False, "kustomize build timed out after 60s"
