from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pulumi
import pulumiverse_talos as talos
import yaml

cfg = pulumi.Config()

cluster_name = cfg.get("cluster_name") or "openchoreo"
talos_version = cfg.get("talos_version") or "v1.12.5"
kubernetes_version = cfg.get("kubernetes_version") or "1.33.0"
control_plane_node = cfg.get("control_plane_node") or "127.0.0.1"
talos_api_endpoint = cfg.get("talos_api_endpoint") or control_plane_node
kubernetes_api_host = cfg.get("kubernetes_api_host") or control_plane_node
kubernetes_api_port = cfg.get_int("kubernetes_api_port") or 6443
control_plane_install_disk = cfg.get("control_plane_install_disk") or "/dev/sda"
control_plane_hostname = cfg.get("control_plane_hostname") or f"{cluster_name}-controlplane-1"
schematic_id = cfg.get("schematic_id") or ""
network_interface = cfg.get("network_interface") or "enp0s1"
network_address = cfg.get("network_address") or ""
network_gateway = cfg.get("network_gateway") or ""
longhorn_disk = cfg.get("longhorn_disk") or ""
install_disk_wwid = cfg.get("install_disk_wwid") or ""
cert_sans_raw = cfg.get("cert_sans") or "[]"
cert_sans_extra = json.loads(cert_sans_raw) if cert_sans_raw else []
enable_cloudflared = cfg.get_bool("enable_cloudflared") or False
cloudflared_token = cfg.get("cloudflared_token") or ""
enable_nvidia = cfg.get_bool("enable_nvidia") or False

patches = __import__("patches")

patches.schematic_id = schematic_id
patches.talos_version = talos_version
patches.network_interface = network_interface
patches.network_address = network_address
patches.network_gateway = network_gateway
patches.longhorn_disk = longhorn_disk
patches.install_disk_wwid = install_disk_wwid
patches.control_plane_node = control_plane_node
patches.cert_sans_extra = cert_sans_extra
patches.enable_cloudflared = enable_cloudflared
patches.cloudflared_token = cloudflared_token
patches.enable_nvidia = enable_nvidia

kubeconfig_path = str(Path.home() / ".kube" / f"config-{cluster_name}-talos-baremetal")
talosconfig_path = str(Path.home() / ".talos" / f"config-{cluster_name}-baremetal")

kubernetes_endpoint = f"https://{kubernetes_api_host}:{kubernetes_api_port}"


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


def render_talosconfig(client_config: talos.machine.ClientConfigurationArgs) -> str:
    talosconfig = {
        "context": cluster_name,
        "contexts": {
            cluster_name: {
                "endpoints": [talos_api_endpoint],
                "nodes": [control_plane_node],
                "ca": client_config.ca_certificate,
                "crt": client_config.client_certificate,
                "key": client_config.client_key,
            }
        },
    }
    return yaml.safe_dump(talosconfig, sort_keys=False)


def build_talosconfig_from_input(client_config: talos.machine.ClientConfigurationArgs) -> str:
    talosconfig_raw = render_talosconfig(client_config)
    path = Path(talosconfig_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(talosconfig_raw)
    return talosconfig_path


def persist_kubeconfig(raw: str) -> dict[str, str]:
    path = Path(kubeconfig_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw)
    loaded = yaml.safe_load(raw) or {}
    return {
        "path": str(path),
        "context": loaded.get("current-context", f"admin@{cluster_name}"),
    }


machine_secrets = talos.machine.Secrets("machine-secrets", talos_version=talos_version)
machine_client_configuration = as_machine_client_configuration_input(machine_secrets.client_configuration)
cluster_client_configuration = as_cluster_client_configuration_input(machine_secrets.client_configuration)
machine_secrets_input = as_machine_secrets_input(machine_secrets.machine_secrets)
config_patches = [
    p
    for p in [
        patches.render_install_patch(),
        patches.render_factory_image_patch(),
        patches.render_network_patch(),
        patches.render_storage_patch(),
        patches.render_kernel_patch(),
        patches.render_cluster_settings_patch(),
        patches.render_cloudflared_patch(),
        patches.render_nvidia_patch(),
    ]
    if p
]

machine_config = talos.machine.get_configuration_output(
    cluster_name=cluster_name,
    machine_type="controlplane",
    cluster_endpoint=kubernetes_endpoint,
    machine_secrets=machine_secrets_input,
    talos_version=talos_version,
    kubernetes_version=kubernetes_version,
    config_patches=config_patches,
)

config_apply = talos.machine.ConfigurationApply(
    "control-plane-config",
    client_configuration=machine_client_configuration,
    machine_configuration_input=machine_config.machine_configuration,
    node=control_plane_node,
    endpoint=talos_api_endpoint,
    apply_mode="auto",
    timeouts={"create": "20m", "update": "20m"},
)

bootstrap = talos.machine.Bootstrap(
    "bootstrap",
    node=control_plane_node,
    endpoint=talos_api_endpoint,
    client_configuration=machine_client_configuration,
    opts=pulumi.ResourceOptions(depends_on=[config_apply]),
)

kubeconfig = talos.cluster.Kubeconfig(
    "kubeconfig",
    client_configuration=cluster_client_configuration,
    node=control_plane_node,
    endpoint=talos_api_endpoint,
    timeouts={"create": "20m", "update": "20m"},
    opts=pulumi.ResourceOptions(depends_on=[bootstrap]),
)

kubeconfig_file = kubeconfig.kubeconfig_raw.apply(persist_kubeconfig)
talosconfig_file = machine_client_configuration.apply(build_talosconfig_from_input)
talosconfig_raw = machine_client_configuration.apply(render_talosconfig)

pulumi.export("cluster_name", cluster_name)
pulumi.export("control_plane_ip", control_plane_node)
pulumi.export("kubeconfig_raw", kubeconfig.kubeconfig_raw)
pulumi.export("kubeconfig_path", kubeconfig_file.apply(lambda value: value["path"]))
pulumi.export("kubeconfig_context", kubeconfig_file.apply(lambda value: value["context"]))
pulumi.export("talosconfig_raw", pulumi.Output.secret(talosconfig_raw))
pulumi.export("talosconfig_path", talosconfig_file)
pulumi.export("talos_version", talos_version)
