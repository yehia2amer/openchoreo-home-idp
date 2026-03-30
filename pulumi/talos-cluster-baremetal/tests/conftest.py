import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # pyright: ignore[reportMissingImports]

import patches  # pyright: ignore[reportMissingImports]


@pytest.fixture(autouse=True)
def reset_patches_config():
    patches.schematic_id = "test-schematic-abc123"
    patches.talos_version = "v1.12.5"
    patches.network_interface = "enp0s1"
    patches.network_address = "192.168.0.100/24"
    patches.network_gateway = "192.168.0.1"
    patches.longhorn_disk = "/dev/disk/by-id/ata-test-disk"
    patches.install_disk_wwid = "naa.5002538e7026fcb7"
    patches.control_plane_node = "192.168.0.100"
    patches.cert_sans_extra = ["192.168.0.100", "talos.amernas.work"]
    patches.enable_cloudflared = True
    patches.cloudflared_token = "test-token-xyz"
    patches.enable_nvidia = True
    yield
    patches.schematic_id = ""
    patches.talos_version = ""
    patches.network_interface = "enp0s1"
    patches.network_address = ""
    patches.network_gateway = ""
    patches.longhorn_disk = ""
    patches.install_disk_wwid = ""
    patches.control_plane_node = ""
    patches.cert_sans_extra = []
    patches.enable_cloudflared = False
    patches.cloudflared_token = ""
    patches.enable_nvidia = False
