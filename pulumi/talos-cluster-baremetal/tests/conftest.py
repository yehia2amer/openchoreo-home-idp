import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # pyright: ignore[reportMissingImports]

from patches import PatchConfig  # pyright: ignore[reportMissingImports]


@pytest.fixture()
def patch_cfg() -> PatchConfig:
    """Default PatchConfig used by all patch tests."""
    return PatchConfig(
        cluster_name="test-cluster",
        cluster_endpoint="https://192.168.0.100:6443",
        schematic_id="test-schematic-abc123",
        talos_version="v1.12.5",
        wipe_install_disk=True,
        network_interface="enp0s1",
        network_addresses=["192.168.0.100/24"],
        network_gateway="192.168.0.1",
        dns_servers=["8.8.8.8", "8.8.4.4"],
        cert_sans=["192.168.0.100", "talos.amernas.work"],
        longhorn_disk="/dev/disk/by-id/ata-test-disk",
        install_disk_wwid="naa.5002538e7026fcb7",
        control_plane_node="192.168.0.100",
        enable_cloudflared=True,
        cloudflared_token="test-token-xyz",
        enable_nvidia=True,
        enable_zfs=False,
    )
