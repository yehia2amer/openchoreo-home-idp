from __future__ import annotations

import json

schematic_id: str = ""
talos_version: str = ""
network_interface: str = "enp0s1"
network_address: str = ""
network_gateway: str = ""
longhorn_disk: str = ""
install_disk_wwid: str = ""
control_plane_node: str = ""
cert_sans_extra: list[str] = []
enable_cloudflared: bool = False
cloudflared_token: str = ""
enable_nvidia: bool = False


def render_install_patch() -> str:
    cert_sans = sorted({control_plane_node, "localhost", *cert_sans_extra})
    return json.dumps(
        {
            "cluster": {
                "apiServer": {"certSANs": cert_sans},
                "network": {"cni": {"name": "none"}},
                "proxy": {"disabled": True},
                "allowSchedulingOnControlPlanes": True,
            },
            "machine": {
                "certSANs": cert_sans,
                "network": {"hostname": "openchoreo-controlplane-1"},
            },
        }
    )


def render_factory_image_patch() -> str:
    if not schematic_id:
        return ""
    return json.dumps(
        {
            "machine": {
                "install": {
                    "image": f"factory.talos.dev/metal-installer/{schematic_id}:{talos_version}",
                    "wipe": True,
                }
            }
        }
    )


def render_network_patch() -> str:
    patch: dict[str, object] = {
        "machine": {
            "network": {
                "nameservers": ["1.1.1.1", "8.8.8.8"],
            },
            "features": {
                "hostDNS": {
                    "enabled": True,
                    "forwardKubeDNSToHost": False,
                }
            },
        }
    }
    if network_interface and network_address and network_gateway:
        patch_machine = patch["machine"]
        if isinstance(patch_machine, dict):
            patch_network = patch_machine.get("network")
            if isinstance(patch_network, dict):
                patch_network["interfaces"] = [
                    {
                        "interface": network_interface,
                        "addresses": [network_address],
                        "routes": [{"network": "0.0.0.0/0", "gateway": network_gateway}],
                    }
                ]
    return json.dumps(patch)


def render_storage_patch() -> str:
    if not longhorn_disk:
        return ""
    patch: dict[str, object] = {
        "machine": {
            "kubelet": {
                "extraMounts": [
                    {
                        "destination": "/var/lib/longhorn",
                        "type": "bind",
                        "source": "/var/lib/longhorn",
                        "options": ["bind", "rshared", "rw"],
                    }
                ]
            },
            "disks": [
                {
                    "device": longhorn_disk,
                    "partitions": [{"mountpoint": "/var/lib/longhorn"}],
                }
            ],
        }
    }
    if install_disk_wwid:
        patch_machine = patch["machine"]
        if isinstance(patch_machine, dict):
            patch_machine["install"] = {"diskSelector": {"wwid": install_disk_wwid}}
    return json.dumps(patch)


def render_kernel_patch() -> str:
    return json.dumps(
        {
            "machine": {
                "kernel": {
                    "modules": [
                        {"name": "vfio_pci"},
                        {"name": "vfio_iommu_type1"},
                    ]
                },
                "files": [
                    {
                        "content": (
                            "[plugins]\n"
                            '  [plugins."io.containerd.grpc.v1.cri"]\n'
                            "    device_ownership_from_security_context = true\n"
                            '  [plugins."io.containerd.cri.v1.runtime"]\n'
                            "    device_ownership_from_security_context = true\n"
                        ),
                        "path": "/etc/cri/conf.d/20-customization.part",
                        "op": "create",
                    }
                ],
            }
        }
    )


def render_cluster_settings_patch() -> str:
    return json.dumps(
        {
            "machine": {
                "kubelet": {
                    "extraArgs": {"max-pods": "250"},
                }
            },
            "cluster": {
                "allowSchedulingOnControlPlanes": True,
            },
        }
    )


def render_cloudflared_patch() -> str:
    if not enable_cloudflared or not cloudflared_token:
        return ""
    return (
        "---\n"
        "apiVersion: v1alpha1\n"
        "kind: ExtensionServiceConfig\n"
        "name: cloudflared\n"
        "environment:\n"
        f"  - TUNNEL_TOKEN={cloudflared_token}\n"
        "  - TUNNEL_METRICS=localhost:2000\n"
    )


def render_nvidia_patch() -> str:
    if not enable_nvidia:
        return ""
    return (
        "---\n"
        "apiVersion: v1alpha1\n"
        "kind: PCIDriverRebindConfig\n"
        "name: 0000:03:00.0\n"
        "targetDriver: vfio-pci\n"
        "---\n"
        "apiVersion: v1alpha1\n"
        "kind: PCIDriverRebindConfig\n"
        "name: 0000:03:00.1\n"
        "targetDriver: vfio-pci"
    )
