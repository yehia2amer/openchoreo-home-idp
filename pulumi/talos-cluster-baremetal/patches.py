from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class PatchConfig:
    cluster_name: str = ""
    cluster_endpoint: str = ""
    schematic_id: str = ""
    talos_version: str = ""
    wipe_install_disk: bool = False
    network_interface: str = "enp0s1"
    network_addresses: list[str] = field(default_factory=list)
    network_gateway: str = ""
    dns_servers: list[str] = field(default_factory=lambda: ["8.8.8.8", "8.8.4.4"])
    cert_sans: list[str] = field(default_factory=list)
    longhorn_disk: str = ""
    install_disk_wwid: str = ""
    control_plane_node: str = ""
    enable_cloudflared: bool = False
    cloudflared_token: str = ""
    enable_nvidia: bool = False
    enable_zfs: bool = False
    registry_mirror_endpoint: str = ""


def render_install_image_patch(cfg: PatchConfig) -> str:
    if not cfg.schematic_id:
        return ""
    return json.dumps(
        {
            "machine": {
                "install": {
                    "image": f"factory.talos.dev/metal-installer/{cfg.schematic_id}:{cfg.talos_version}",
                    "wipe": cfg.wipe_install_disk,
                }
            }
        }
    )


def render_network_patch(cfg: PatchConfig) -> str:
    patch: dict = {
        "machine": {
            "features": {
                "hostDNS": {
                    "enabled": True,
                    "forwardKubeDNSToHost": False,
                }
            },
            "certSANs": cfg.cert_sans,
            "network": {
                "interfaces": [
                    {
                        "interface": cfg.network_interface,
                        "addresses": cfg.network_addresses,
                        "routes": [
                            {
                                "network": "0.0.0.0/0",
                                "gateway": cfg.network_gateway,
                                "metric": 1024,
                            }
                        ],
                        "mtu": 1500,
                    }
                ],
                "nameservers": cfg.dns_servers,
            },
        },
        "cluster": {
            "network": {"cni": {"name": "none"}},
            "proxy": {"disabled": True},
            "apiServer": {"certSANs": cfg.cert_sans},
        },
    }
    return json.dumps(patch)


def render_storage_patch(cfg: PatchConfig) -> str:
    if not cfg.longhorn_disk:
        return ""
    return json.dumps(
        {
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
                "install": {
                    "diskSelector": {"wwid": cfg.install_disk_wwid},
                },
                "disks": [
                    {
                        "device": cfg.longhorn_disk,
                        "partitions": [{"mountpoint": "/var/lib/longhorn"}],
                    }
                ],
            }
        }
    )


def render_kernel_drivers_patch(cfg: PatchConfig) -> str:
    modules: list[dict[str, str]] = [
        {"name": "vfio_pci"},
        {"name": "vfio_iommu_type1"},
        {"name": "cx23885"},
    ]
    if cfg.enable_zfs:
        modules.append({"name": "zfs"})

    return json.dumps(
        {
            "machine": {
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
                "registries": {},
                "kernel": {"modules": modules},
            }
        }
    )


def render_cluster_settings_patch(cfg: PatchConfig) -> str:
    return json.dumps(
        {
            "machine": {
                "kubelet": {
                    "extraArgs": {"max-pods": "250"},
                }
            },
            "cluster": {
                "allowSchedulingOnControlPlanes": True,
                "controlPlane": {
                    "endpoint": cfg.cluster_endpoint,
                },
                "clusterName": cfg.cluster_name,
            },
        }
    )


def render_logging_patch(cfg: PatchConfig) -> str:
    return json.dumps(
        {
            "machine": {
                "logging": {
                    "destinations": [
                        {
                            "endpoint": "tcp://127.0.0.1:6001/",
                            "format": "json_lines",
                            "extraTags": {
                                "cluster": cfg.cluster_name,
                            },
                        }
                    ]
                }
            }
        }
    )


def render_cloudflared_patch(cfg: PatchConfig) -> str:
    if not cfg.enable_cloudflared or not cfg.cloudflared_token:
        return ""
    return (
        "---\n"
        "apiVersion: v1alpha1\n"
        "kind: ExtensionServiceConfig\n"
        "name: cloudflared\n"
        "environment:\n"
        f"  - TUNNEL_TOKEN={cfg.cloudflared_token}\n"
        "  - TUNNEL_METRICS=localhost:2000\n"
    )


def render_nvidia_patch(cfg: PatchConfig) -> str:
    if not cfg.enable_nvidia:
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


def render_registry_mirrors_patch(cfg: PatchConfig) -> str:
    """Configure containerd registry mirrors so the kubelet can pull from an in-cluster registry.

    On Talos, containerd resolves registry hostnames via node DNS (not cluster DNS),
    so cluster-internal names like ``registry.<ns>.svc.cluster.local`` are unreachable.
    A mirror entry rewrites the pull to a NodePort endpoint reachable by the host.

    Two entries are created:
    - The cluster-internal name → NodePort endpoint (for pods using internal DNS)
    - The NodePort ``host:port`` → itself as HTTP (for direct NodePort references)
    """
    if not cfg.registry_mirror_endpoint:
        return ""
    # Extract host:port from endpoint URL (e.g. "http://192.168.0.100:30082" → "192.168.0.100:30082")
    from urllib.parse import urlparse

    parsed = urlparse(cfg.registry_mirror_endpoint)
    nodeport_host_port = parsed.netloc or parsed.path  # netloc for http://..., path for bare host:port

    patch: dict = {
        "machine": {
            "registries": {
                "mirrors": {
                    "registry.openchoreo-workflow-plane.svc.cluster.local:10082": {
                        "endpoints": [cfg.registry_mirror_endpoint],
                    },
                    nodeport_host_port: {
                        "endpoints": [cfg.registry_mirror_endpoint],
                    },
                },
                "config": {
                    nodeport_host_port: {
                        "tls": {
                            "insecureSkipVerify": True,
                        },
                    },
                },
            }
        }
    }
    return json.dumps(patch)


def build_control_plane_patches(cfg: PatchConfig) -> list[str]:
    common = [
        render_install_image_patch(cfg),
        render_cluster_settings_patch(cfg),
        render_kernel_drivers_patch(cfg),
        render_registry_mirrors_patch(cfg),
        render_logging_patch(cfg),
    ]
    control_plane_extras = [
        render_network_patch(cfg),
        render_storage_patch(cfg),
        render_cloudflared_patch(cfg),
        render_nvidia_patch(cfg),
    ]
    return [p for p in common + control_plane_extras if p]
