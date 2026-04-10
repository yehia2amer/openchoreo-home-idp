"""Structural tests for the Kustomize component-based platform architecture."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from .conftest import PLATFORMS, WAVES, kustomize_build

pytestmark = pytest.mark.structural


def _parse_resources(raw_yaml: str) -> list[dict]:
    resources = []
    for doc in yaml.safe_load_all(raw_yaml):
        if doc and isinstance(doc, dict) and "kind" in doc:
            resources.append(doc)
    return resources


def _resource_key(resource: dict) -> str:
    kind = resource.get("kind", "")
    metadata = resource.get("metadata", {})
    name = metadata.get("name", "")
    namespace = metadata.get("namespace", "")
    return f"{kind}|{name}|{namespace}"


def _platform_wave_ids() -> list[tuple[str, str]]:
    return [(p, w) for p in PLATFORMS for w in WAVES]


@pytest.mark.parametrize(
    "platform,wave",
    _platform_wave_ids(),
    ids=[f"{p}/{w}" for p, w in _platform_wave_ids()],
)
def test_all_platforms_build(
    platforms_dir: Path,
    platform: str,
    wave: str,
) -> None:
    wave_path = platforms_dir / platform / wave
    if not wave_path.is_dir():
        pytest.skip(f"{wave_path} does not exist")

    success, output = kustomize_build(wave_path)
    assert success, f"kustomize build failed for {platform}/{wave}:\n{output}"

    _parse_resources(output)


def test_baremetal_k3d_component_difference(platforms_dir: Path) -> None:
    bm_path = platforms_dir / "baremetal" / "05-network"
    k3d_path = platforms_dir / "k3d" / "05-network"

    bm_ok, bm_output = kustomize_build(bm_path)
    assert bm_ok, f"baremetal/05-network build failed:\n{bm_output}"

    k3d_ok, k3d_output = kustomize_build(k3d_path)
    assert k3d_ok, f"k3d/05-network build failed:\n{k3d_output}"

    bm_resources = _parse_resources(bm_output)
    k3d_resources = _parse_resources(k3d_output)

    bm_kinds = {r["kind"] for r in bm_resources}
    k3d_kinds = {r["kind"] for r in k3d_resources}

    assert "CiliumL2AnnouncementPolicy" in bm_kinds, (
        "baremetal/05-network should contain CiliumL2AnnouncementPolicy"
    )
    assert "CiliumL2AnnouncementPolicy" not in k3d_kinds, (
        "k3d/05-network should NOT contain CiliumL2AnnouncementPolicy"
    )


@pytest.mark.parametrize("platform", PLATFORMS, ids=PLATFORMS)
def test_no_duplicate_resources(platforms_dir: Path, platform: str) -> None:
    all_keys: list[str] = []

    for wave in WAVES:
        wave_path = platforms_dir / platform / wave
        if not wave_path.is_dir():
            continue
        success, output = kustomize_build(wave_path)
        if not success:
            pytest.fail(f"kustomize build failed for {platform}/{wave}:\n{output}")
        for res in _parse_resources(output):
            all_keys.append(_resource_key(res))

    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for key in all_keys:
        seen[key] = seen.get(key, 0) + 1
        if seen[key] == 2:
            duplicates.append(key)

    assert not duplicates, f"Duplicate resources in {platform}:\n" + "\n".join(duplicates)


def test_components_build_independently(components_dir: Path) -> None:
    failures: list[str] = []
    tested = 0

    for component_path in sorted(components_dir.iterdir()):
        if not component_path.is_dir():
            continue
        kustomization = component_path / "kustomization.yaml"
        if not kustomization.exists():
            kustomization = component_path / "kustomization.yml"
        if not kustomization.exists():
            continue

        tested += 1
        success, output = kustomize_build(component_path)
        if not success:
            failures.append(f"  {component_path.name}: {output.strip()}")

    assert tested > 0, "No components with kustomization.yaml found"
    assert not failures, f"{len(failures)} component(s) failed to build:\n" + "\n".join(failures)


def test_component_toggling(platforms_dir: Path) -> None:
    def _total_resources(platform: str) -> int:
        total = 0
        for wave in WAVES:
            wave_path = platforms_dir / platform / wave
            if not wave_path.is_dir():
                continue
            success, output = kustomize_build(wave_path)
            if success:
                total += len(_parse_resources(output))
        return total

    bm_total = _total_resources("baremetal")
    aws_total = _total_resources("aws")

    assert bm_total > 0, "baremetal produced zero resources"
    assert bm_total > aws_total, (
        f"baremetal ({bm_total}) should have MORE resources than aws ({aws_total}) "
        "due to component toggling"
    )


def test_no_flux_spec_components(gitops_repo_path: Path) -> None:
    """Guard against FluxCD bug #1506: ``spec.components`` must not appear in cluster YAML."""
    clusters_dir = gitops_repo_path / "clusters"
    if not clusters_dir.is_dir():
        pytest.skip("clusters/ directory not found")

    violations: list[str] = []

    for yaml_file in sorted(clusters_dir.rglob("*.yaml")):
        content = yaml_file.read_text()
        for doc in yaml.safe_load_all(content):
            if not isinstance(doc, dict):
                continue
            spec = doc.get("spec")
            if isinstance(spec, dict) and "components" in spec:
                rel = yaml_file.relative_to(clusters_dir)
                violations.append(str(rel))

    assert not violations, (
        "Found spec.components in cluster YAML (FluxCD bug #1506):\n"
        + "\n".join(f"  {v}" for v in violations)
    )
