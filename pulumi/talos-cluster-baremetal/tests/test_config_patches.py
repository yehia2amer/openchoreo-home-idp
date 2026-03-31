import json
from dataclasses import replace

from patches import (
    PatchConfig,
    build_control_plane_patches,
    render_cloudflared_patch,
    render_cluster_settings_patch,
    render_install_image_patch,
    render_kernel_drivers_patch,
    render_logging_patch,
    render_network_patch,
    render_nvidia_patch,
    render_storage_patch,
)

# ---------------------------------------------------------------------------
# render_install_image_patch
# ---------------------------------------------------------------------------


def test_install_image_patch_uses_schematic_and_version(patch_cfg: PatchConfig):
    data = json.loads(render_install_image_patch(patch_cfg))

    assert data["machine"]["install"]["image"] == ("factory.talos.dev/metal-installer/test-schematic-abc123:v1.12.5")
    assert data["machine"]["install"]["wipe"] is True


def test_install_image_patch_wipe_false(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, wipe_install_disk=False)
    data = json.loads(render_install_image_patch(cfg))

    assert data["machine"]["install"]["wipe"] is False


def test_install_image_patch_returns_empty_when_no_schematic(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, schematic_id="")
    assert render_install_image_patch(cfg) == ""


# ---------------------------------------------------------------------------
# render_network_patch
# ---------------------------------------------------------------------------


def test_network_patch_structure(patch_cfg: PatchConfig):
    data = json.loads(render_network_patch(patch_cfg))

    # machine-level cert SANs
    assert data["machine"]["certSANs"] == ["192.168.0.100", "talos.amernas.work"]

    # hostDNS
    assert data["machine"]["features"]["hostDNS"] == {
        "enabled": True,
        "forwardKubeDNSToHost": False,
    }

    # interface config with route metric and MTU
    iface = data["machine"]["network"]["interfaces"][0]
    assert iface["interface"] == "enp0s1"
    assert iface["addresses"] == ["192.168.0.100/24"]
    assert iface["routes"] == [{"network": "0.0.0.0/0", "gateway": "192.168.0.1", "metric": 1024}]
    assert iface["mtu"] == 1500

    # cluster-level CNI and proxy
    assert data["cluster"]["network"]["cni"]["name"] == "none"
    assert data["cluster"]["proxy"]["disabled"] is True

    # cluster-level cert SANs
    assert data["cluster"]["apiServer"]["certSANs"] == [
        "192.168.0.100",
        "talos.amernas.work",
    ]


# ---------------------------------------------------------------------------
# render_storage_patch
# ---------------------------------------------------------------------------


def test_storage_patch_includes_mounts_disk_and_wwid(patch_cfg: PatchConfig):
    data = json.loads(render_storage_patch(patch_cfg))

    assert data["machine"]["kubelet"]["extraMounts"] == [
        {
            "destination": "/var/lib/longhorn",
            "type": "bind",
            "source": "/var/lib/longhorn",
            "options": ["bind", "rshared", "rw"],
        }
    ]
    assert data["machine"]["disks"] == [
        {
            "device": "/dev/disk/by-id/ata-test-disk",
            "partitions": [{"mountpoint": "/var/lib/longhorn"}],
        }
    ]
    assert data["machine"]["install"]["diskSelector"]["wwid"] == "naa.5002538e7026fcb7"


def test_storage_patch_returns_empty_when_no_longhorn_disk(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, longhorn_disk="")
    assert render_storage_patch(cfg) == ""


# ---------------------------------------------------------------------------
# render_kernel_drivers_patch
# ---------------------------------------------------------------------------


def test_kernel_drivers_patch_default_modules(patch_cfg: PatchConfig):
    data = json.loads(render_kernel_drivers_patch(patch_cfg))

    modules = data["machine"]["kernel"]["modules"]
    module_names = [m["name"] for m in modules]
    assert "vfio_pci" in module_names
    assert "vfio_iommu_type1" in module_names
    assert "cx23885" in module_names
    # ZFS disabled in default fixture
    assert "zfs" not in module_names


def test_kernel_drivers_patch_includes_zfs_when_enabled(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, enable_zfs=True)
    data = json.loads(render_kernel_drivers_patch(cfg))

    module_names = [m["name"] for m in data["machine"]["kernel"]["modules"]]
    assert "zfs" in module_names


def test_kernel_drivers_patch_containerd_config(patch_cfg: PatchConfig):
    data = json.loads(render_kernel_drivers_patch(patch_cfg))

    file_entry = data["machine"]["files"][0]
    assert file_entry["path"] == "/etc/cri/conf.d/20-customization.part"
    assert file_entry["op"] == "create"
    assert "[plugins]" in file_entry["content"]
    assert "io.containerd.grpc.v1.cri" in file_entry["content"]
    assert "io.containerd.cri.v1.runtime" in file_entry["content"]


def test_kernel_drivers_patch_includes_empty_registries(patch_cfg: PatchConfig):
    data = json.loads(render_kernel_drivers_patch(patch_cfg))
    assert data["machine"]["registries"] == {}


# ---------------------------------------------------------------------------
# render_cluster_settings_patch
# ---------------------------------------------------------------------------


def test_cluster_settings_patch(patch_cfg: PatchConfig):
    data = json.loads(render_cluster_settings_patch(patch_cfg))

    assert data["machine"]["kubelet"]["extraArgs"]["max-pods"] == "250"
    assert data["cluster"]["allowSchedulingOnControlPlanes"] is True
    assert data["cluster"]["controlPlane"]["endpoint"] == "https://192.168.0.100:6443"
    assert data["cluster"]["clusterName"] == "test-cluster"


# ---------------------------------------------------------------------------
# render_logging_patch
# ---------------------------------------------------------------------------


def test_logging_patch_structure(patch_cfg: PatchConfig):
    data = json.loads(render_logging_patch(patch_cfg))

    dest = data["machine"]["logging"]["destinations"][0]
    assert dest["endpoint"] == "tcp://127.0.0.1:6001/"
    assert dest["format"] == "json_lines"
    assert dest["extraTags"]["cluster"] == "test-cluster"


# ---------------------------------------------------------------------------
# render_cloudflared_patch
# ---------------------------------------------------------------------------


def test_cloudflared_patch_returns_yaml_when_enabled(patch_cfg: PatchConfig):
    result = render_cloudflared_patch(patch_cfg)

    assert result.startswith("---\n")
    assert "apiVersion: v1alpha1" in result
    assert "kind: ExtensionServiceConfig" in result
    assert "name: cloudflared" in result
    assert "TUNNEL_TOKEN=test-token-xyz" in result
    assert "TUNNEL_METRICS=localhost:2000" in result


def test_cloudflared_patch_returns_empty_when_disabled(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, enable_cloudflared=False)
    assert render_cloudflared_patch(cfg) == ""


def test_cloudflared_patch_returns_empty_when_no_token(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, cloudflared_token="")
    assert render_cloudflared_patch(cfg) == ""


# ---------------------------------------------------------------------------
# render_nvidia_patch
# ---------------------------------------------------------------------------


def test_nvidia_patch_returns_yaml_with_two_configs(patch_cfg: PatchConfig):
    result = render_nvidia_patch(patch_cfg)

    assert result.startswith("---\n")
    assert result.count("kind: PCIDriverRebindConfig") == 2
    assert "0000:03:00.0" in result
    assert "0000:03:00.1" in result
    assert "targetDriver: vfio-pci" in result


def test_nvidia_patch_returns_empty_when_disabled(patch_cfg: PatchConfig):
    cfg = replace(patch_cfg, enable_nvidia=False)
    assert render_nvidia_patch(cfg) == ""


# ---------------------------------------------------------------------------
# build_control_plane_patches (aggregation)
# ---------------------------------------------------------------------------


def test_build_control_plane_patches_returns_all_patches(patch_cfg: PatchConfig):
    """With everything enabled, we expect 8 non-empty patches."""
    patches = build_control_plane_patches(patch_cfg)

    # install_image, cluster_settings, kernel_drivers, logging,
    # network, storage, cloudflared, nvidia = 8
    assert len(patches) == 8
    assert all(isinstance(p, str) for p in patches)
    assert all(len(p) > 0 for p in patches)


def test_build_control_plane_patches_filters_empty(patch_cfg: PatchConfig):
    """With conditionals disabled / empty, empty patches are stripped."""
    cfg = replace(
        patch_cfg,
        schematic_id="",  # install_image -> ""
        longhorn_disk="",  # storage -> ""
        enable_cloudflared=False,  # cloudflared -> ""
        enable_nvidia=False,  # nvidia -> ""
    )
    patches = build_control_plane_patches(cfg)

    # Only: cluster_settings, kernel_drivers, logging, network = 4
    assert len(patches) == 4


def test_build_control_plane_patches_order(patch_cfg: PatchConfig):
    """Common patches come before control-plane extras."""
    patches = build_control_plane_patches(patch_cfg)

    # First four are common: install_image, cluster_settings, kernel_drivers, logging
    # Then: network, storage, cloudflared, nvidia
    # Verify by checking known unique content in each position
    assert "factory.talos.dev" in patches[0]  # install_image
    assert "max-pods" in patches[1]  # cluster_settings
    assert "vfio_pci" in patches[2]  # kernel_drivers
    assert "json_lines" in patches[3]  # logging
    assert '"cni"' in patches[4]  # network
    assert "longhorn" in patches[5]  # storage
    assert "cloudflared" in patches[6]  # cloudflared
    assert "PCIDriverRebindConfig" in patches[7]  # nvidia
