import json

import patches


def test_render_install_patch_builds_sorted_deduped_cert_sans():
    data = json.loads(patches.render_install_patch())

    expected_cert_sans = sorted({"192.168.0.100", "localhost", *["192.168.0.100", "talos.amernas.work"]})

    assert data["cluster"]["apiServer"]["certSANs"] == expected_cert_sans
    assert data["cluster"]["network"]["cni"]["name"] == "none"
    assert data["cluster"]["proxy"]["disabled"] is True
    assert data["cluster"]["allowSchedulingOnControlPlanes"] is True
    assert data["machine"]["certSANs"] == expected_cert_sans


def test_render_factory_image_patch_uses_schematic_and_version():
    data = json.loads(patches.render_factory_image_patch())

    assert data["machine"]["install"]["image"] == "factory.talos.dev/metal-installer/test-schematic-abc123:v1.12.5"
    assert data["machine"]["install"]["wipe"] is True


def test_render_factory_image_patch_returns_empty_when_missing_schematic_id():
    patches.schematic_id = ""

    assert patches.render_factory_image_patch() == ""


def test_render_network_patch_includes_interfaces_when_configured():
    data = json.loads(patches.render_network_patch())

    assert data["machine"]["network"]["nameservers"] == ["1.1.1.1", "8.8.8.8"]
    assert data["machine"]["features"]["hostDNS"] == {"enabled": True, "forwardKubeDNSToHost": False}
    assert data["machine"]["network"]["interfaces"] == [
        {
            "interface": "enp0s1",
            "addresses": ["192.168.0.100/24"],
            "routes": [{"network": "0.0.0.0/0", "gateway": "192.168.0.1"}],
        }
    ]


def test_render_network_patch_omits_interfaces_when_incomplete():
    patches.network_interface = ""

    data = json.loads(patches.render_network_patch())

    assert "interfaces" not in data["machine"]["network"]


def test_render_storage_patch_includes_mounts_disk_and_wwid_selector():
    data = json.loads(patches.render_storage_patch())

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


def test_render_storage_patch_returns_empty_when_missing_disk():
    patches.longhorn_disk = ""

    assert patches.render_storage_patch() == ""


def test_render_kernel_patch_contains_modules_and_containerd_config():
    data = json.loads(patches.render_kernel_patch())

    assert data["machine"]["kernel"]["modules"] == [{"name": "vfio_pci"}, {"name": "vfio_iommu_type1"}]
    file_entry = data["machine"]["files"][0]
    assert file_entry["path"] == "/etc/cri/conf.d/20-customization.part"
    assert file_entry["op"] == "create"
    assert "[plugins]" in file_entry["content"]
    assert "io.containerd.grpc.v1.cri" in file_entry["content"]
    assert "io.containerd.cri.v1.runtime" in file_entry["content"]


def test_render_cluster_settings_patch_sets_max_pods_and_control_plane_scheduling():
    data = json.loads(patches.render_cluster_settings_patch())

    assert data["machine"]["kubelet"]["extraArgs"]["max-pods"] == "250"
    assert data["cluster"]["allowSchedulingOnControlPlanes"] is True


def test_render_cloudflared_patch_returns_yaml_when_enabled():
    result = patches.render_cloudflared_patch()

    assert result.startswith("---\n")
    assert "apiVersion: v1alpha1" in result
    assert "kind: ExtensionServiceConfig" in result
    assert "name: cloudflared" in result
    assert "TUNNEL_TOKEN=test-token-xyz" in result


def test_render_cloudflared_patch_returns_empty_when_disabled_or_missing_token():
    patches.enable_cloudflared = False
    assert patches.render_cloudflared_patch() == ""

    patches.enable_cloudflared = True
    patches.cloudflared_token = ""
    assert patches.render_cloudflared_patch() == ""


def test_render_nvidia_patch_returns_yaml_with_two_configs():
    result = patches.render_nvidia_patch()

    assert result.startswith("---\n")
    assert result.count("kind: PCIDriverRebindConfig") == 2
    assert "0000:03:00.0" in result
    assert "0000:03:00.1" in result
    assert "targetDriver: vfio-pci" in result


def test_render_nvidia_patch_returns_empty_when_disabled():
    patches.enable_nvidia = False

    assert patches.render_nvidia_patch() == ""
