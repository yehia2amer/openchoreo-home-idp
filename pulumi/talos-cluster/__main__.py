from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pulumi
import pulumi_libvirt as libvirt
import pulumiverse_talos as talos
import yaml

cfg = pulumi.Config()

cluster_name = cfg.get("cluster_name") or "openchoreo"
talos_version = cfg.get("talos_version") or "v1.12.5"
kubernetes_version = cfg.get("kubernetes_version") or "1.33.0"
libvirt_uri = cfg.get("libvirt_uri") or "qemu+unix:///system?socket=/opt/homebrew/var/run/libvirt/libvirt-sock"
host_loopback = cfg.get("host_loopback") or "127.0.0.1"
kubernetes_api_port = cfg.get_int("kubernetes_api_port") or 64430
talos_api_port = cfg.get_int("talos_api_port") or 50000

control_plane_ip = cfg.get("control_plane_ip") or "10.5.0.2"
network_cidr = cfg.get("network_cidr") or "10.5.0.0/24"
network_gateway = cfg.get("network_gateway") or "10.5.0.1"
network_mode = cfg.get("network_mode") or "nat"

pool_path = str(Path.home() / ".talos" / "libvirt-pool")
kubeconfig_path = str(Path.home() / ".kube" / f"config-{cluster_name}-talos")
talosconfig_path = str(Path.home() / ".talos" / f"config-{cluster_name}")

vm_memory_mb = cfg.get_int("vm_memory_mb") or 12288
vm_vcpu = cfg.get_int("vm_vcpu") or 5
vm_disk_bytes = cfg.get_int("vm_disk_bytes") or 80 * 1024 * 1024 * 1024
architecture = cfg.get("architecture") or "arm64"

talos_endpoint = f"{host_loopback}:{talos_api_port}"
kubernetes_endpoint = f"https://{host_loopback}:{kubernetes_api_port}"
talos_node = host_loopback

libvirt_provider = libvirt.Provider("libvirt", uri=libvirt_uri)

if architecture == "arm64":
    domain_arch = "aarch64"
    domain_machine = "virt"
    domain_emulator = "/opt/homebrew/bin/qemu-system-aarch64"
elif architecture == "amd64":
    domain_arch = "x86_64"
    domain_machine = "q35"
    domain_emulator = None
else:
    msg = f"Unsupported Talos VM architecture: {architecture}"
    raise ValueError(msg)

network_device_model = "virtio-net-device" if architecture == "arm64" else "virtio-net-pci"


def as_client_configuration(config: pulumi.Input[object]) -> pulumi.Output[dict[str, pulumi.Input[str]]]:
    config_output = cast("pulumi.Output[object]", pulumi.Output.from_input(config))
    return config_output.apply(
        lambda value: {
            "ca_certificate": cast(dict[str, pulumi.Input[str]], value)["ca_certificate"],
            "client_certificate": cast(dict[str, pulumi.Input[str]], value)["client_certificate"],
            "client_key": cast(dict[str, pulumi.Input[str]], value)["client_key"],
        }
    )


def as_machine_client_configuration_input(
    config: pulumi.Input[object],
) -> pulumi.Output[talos.machine.ClientConfigurationArgs]:
    return as_client_configuration(config).apply(
        lambda value: talos.machine.ClientConfigurationArgs(
            ca_certificate=value["ca_certificate"],
            client_certificate=value["client_certificate"],
            client_key=value["client_key"],
        )
    )


def as_cluster_client_configuration_input(
    config: pulumi.Input[object],
) -> pulumi.Output[talos.cluster.KubeconfigClientConfigurationArgs]:
    return as_client_configuration(config).apply(
        lambda value: talos.cluster.KubeconfigClientConfigurationArgs(
            ca_certificate=value["ca_certificate"],
            client_certificate=value["client_certificate"],
            client_key=value["client_key"],
        )
    )


def as_machine_secrets(secrets: pulumi.Input[object]) -> pulumi.Output[dict[str, pulumi.Input[object]]]:
    secrets_output = cast("pulumi.Output[object]", pulumi.Output.from_input(secrets))
    return secrets_output.apply(
        lambda value: {
            "certs": cast(dict[str, pulumi.Input[object]], value)["certs"],
            "cluster": cast(dict[str, pulumi.Input[object]], value)["cluster"],
            "secrets": cast(dict[str, pulumi.Input[object]], value)["secrets"],
            "trustdinfo": cast(dict[str, pulumi.Input[object]], value)["trustdinfo"],
        }
    )


def as_machine_secrets_input(secrets: pulumi.Input[object]) -> pulumi.Output[talos.machine.MachineSecretsArgs]:
    return as_machine_secrets(secrets).apply(
        lambda value: talos.machine.MachineSecretsArgs(
            certs=cast(Any, value["certs"]),
            cluster=cast(Any, value["cluster"]),
            secrets=cast(Any, value["secrets"]),
            trustdinfo=cast(Any, value["trustdinfo"]),
        )
    )


def build_talosconfig_from_input(client_config: talos.machine.ClientConfigurationArgs) -> str:
    talosconfig_raw = render_talosconfig(client_config)
    path = Path(talosconfig_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(talosconfig_raw)
    return talosconfig_path


def render_talosconfig(client_config: talos.machine.ClientConfigurationArgs) -> str:
    talosconfig = {
        "context": cluster_name,
        "contexts": {
            cluster_name: {
                "endpoints": [talos_endpoint],
                "nodes": [talos_node],
                "ca": client_config.ca_certificate,
                "crt": client_config.client_certificate,
                "key": client_config.client_key,
            }
        },
    }
    return yaml.safe_dump(talosconfig, sort_keys=False)


def image_url(result: object, field: str) -> str:
    urls = getattr(result, "urls", None)
    if urls is None and isinstance(result, dict):
        urls = result.get("urls")

    if urls is None:
        msg = f"Talos image factory result did not contain urls for field '{field}'"
        raise ValueError(msg)

    value = getattr(urls, field, None)
    if value is None and isinstance(urls, dict):
        value = urls.get(field)

    if not isinstance(value, str):
        msg = f"Talos image factory urls did not contain a string value for field '{field}'"
        raise ValueError(msg)

    return value


def render_install_patch(image: str) -> str:
    return json.dumps(
        {
            "cluster": {
                "apiServer": {
                    "certSANs": [host_loopback, "localhost"],
                },
                "network": {
                    "cni": {"name": "none"},
                },
                "proxy": {"disabled": True},
                "allowSchedulingOnControlPlanes": True,
            },
            "machine": {
                "certSANs": [host_loopback, "localhost"],
                "install": {
                    "disk": "/dev/vda",
                    "image": image,
                },
                "network": {
                    "hostname": f"{cluster_name}-controlplane-1",
                },
            },
        }
    )


def persist_kubeconfig(raw: str) -> dict[str, str]:
    path = Path(kubeconfig_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw)
    loaded = yaml.safe_load(raw) or {}
    return {
        "path": str(path),
        "context": loaded.get("current-context", f"admin@{cluster_name}"),
    }


def render_qemu_user_network_xslt() -> str:
    host_forward_args = (
        f"user,id=talosnet0,"
        f"hostfwd=tcp:{host_loopback}:{talos_api_port}-:50000,"
        f"hostfwd=tcp:{host_loopback}:{kubernetes_api_port}-:6443"
    )

    return f"""<?xml version=\"1.0\"?>
<xsl:stylesheet version=\"1.0\"
                xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"
                xmlns:qemu=\"http://libvirt.org/schemas/domain/qemu/1.0\">
  <xsl:output method=\"xml\" omit-xml-declaration=\"yes\" indent=\"yes\"/>

  <xsl:template match=\"node()|@*\">
    <xsl:copy>
      <xsl:apply-templates select=\"node()|@*\"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match=\"/domain/devices/interface\"/>

  <xsl:template match=\"/domain\">
    <xsl:copy>
      <xsl:apply-templates select=\"@*\"/>
      <xsl:apply-templates select=\"node()\"/>
      <qemu:commandline>
        <qemu:arg value=\"-netdev\"/>
        <qemu:arg value=\"{host_forward_args}\"/>
        <qemu:arg value=\"-device\"/>
        <qemu:arg value=\"{network_device_model},netdev=talosnet0\"/>
      </qemu:commandline>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
"""


schematic = talos.imagefactory.Schematic(
    "schematic",
    schematic=yaml.safe_dump(
        {
            "customization": {
                "extraKernelArgs": ["net.ifnames=0"],
            }
        }
    ),
)

image_urls = talos.imagefactory.get_urls_output(
    talos_version=talos_version,
    schematic_id=schematic.id,
    architecture=architecture,
    platform="metal",
)

image_urls_output = cast("pulumi.Output[object]", image_urls)
boot_iso_source = image_urls_output.apply(lambda result: image_url(result, "iso"))
installer_image = image_urls_output.apply(lambda result: image_url(result, "installer"))

pool = libvirt.Pool(
    "talos-pool",
    type="dir",
    name=f"{cluster_name}-talos-pool",
    target=libvirt.PoolTargetArgs(path=pool_path),
    opts=pulumi.ResourceOptions(provider=libvirt_provider),
)

boot_iso = libvirt.Volume(
    "talos-boot-iso",
    name=f"{cluster_name}-talos.iso",
    pool=pool.name,
    format="raw",
    source=boot_iso_source,
    opts=pulumi.ResourceOptions(provider=libvirt_provider, depends_on=[pool]),
)

system_disk = libvirt.Volume(
    "talos-system-disk",
    name=f"{cluster_name}-controlplane.qcow2",
    pool=pool.name,
    size=vm_disk_bytes,
    format="qcow2",
    opts=pulumi.ResourceOptions(provider=libvirt_provider, depends_on=[pool]),
)

domain = libvirt.Domain(
    "control-plane",
    name=f"{cluster_name}-controlplane-1",
    type="qemu",
    arch=domain_arch,
    machine=domain_machine,
    emulator=domain_emulator,
    running=True,
    autostart=True,
    memory=vm_memory_mb,
    vcpu=vm_vcpu,
    qemu_agent=False,
    graphics=libvirt.DomainGraphicsArgs(
        type="vnc",
        listen_type="address",
        listen_address="127.0.0.1",
        autoport=True,
    ),
    consoles=[libvirt.DomainConsoleArgs(type="pty", target_port="0")],
    boot_devices=[libvirt.DomainBootDeviceArgs(devs=["cdrom", "hd"])],
    disks=[
        libvirt.DomainDiskArgs(volume_id=system_disk.id),
        libvirt.DomainDiskArgs(volume_id=boot_iso.id),
    ],
    network_interfaces=[],
    xml=libvirt.DomainXmlArgs(xslt=render_qemu_user_network_xslt()),
    opts=pulumi.ResourceOptions(provider=libvirt_provider, depends_on=[system_disk, boot_iso]),
)

machine_secrets = talos.machine.Secrets("machine-secrets", talos_version=talos_version)
machine_client_configuration = as_machine_client_configuration_input(machine_secrets.client_configuration)
cluster_client_configuration = as_cluster_client_configuration_input(machine_secrets.client_configuration)
machine_secrets_input = as_machine_secrets_input(machine_secrets.machine_secrets)
config_patch = installer_image.apply(render_install_patch)

machine_config = talos.machine.get_configuration_output(
    cluster_name=cluster_name,
    machine_type="controlplane",
    cluster_endpoint=kubernetes_endpoint,
    machine_secrets=machine_secrets_input,
    talos_version=talos_version,
    kubernetes_version=kubernetes_version,
    config_patches=pulumi.Output.all(config_patch),
)

config_apply = talos.machine.ConfigurationApply(
    "control-plane-config",
    client_configuration=machine_client_configuration,
    machine_configuration_input=machine_config.machine_configuration,
    node=talos_node,
    endpoint=talos_endpoint,
    apply_mode="auto",
    timeouts={"create": "20m", "update": "20m"},
    opts=pulumi.ResourceOptions(depends_on=[domain]),
)

bootstrap = talos.machine.Bootstrap(
    "bootstrap",
    node=talos_node,
    endpoint=talos_endpoint,
    client_configuration=machine_client_configuration,
    opts=pulumi.ResourceOptions(depends_on=[config_apply]),
)

kubeconfig = talos.cluster.Kubeconfig(
    "kubeconfig",
    client_configuration=cluster_client_configuration,
    node=talos_node,
    endpoint=talos_endpoint,
    timeouts={"create": "20m", "update": "20m"},
    opts=pulumi.ResourceOptions(depends_on=[bootstrap]),
)

kubeconfig_file = kubeconfig.kubeconfig_raw.apply(persist_kubeconfig)


talosconfig_file = machine_client_configuration.apply(build_talosconfig_from_input)
talosconfig_raw = machine_client_configuration.apply(render_talosconfig)

pulumi.export("cluster_name", cluster_name)
pulumi.export("control_plane_ip", host_loopback)
pulumi.export("network_gateway", network_gateway)
pulumi.export("kubeconfig_raw", kubeconfig.kubeconfig_raw)
pulumi.export("kubeconfig_path", kubeconfig_file.apply(lambda value: value["path"]))
pulumi.export("kubeconfig_context", kubeconfig_file.apply(lambda value: value["context"]))
pulumi.export("talosconfig_raw", pulumi.Output.secret(talosconfig_raw))
pulumi.export("talosconfig_path", talosconfig_file)
pulumi.export("installer_image", installer_image)
pulumi.export("talos_version", talos_version)
