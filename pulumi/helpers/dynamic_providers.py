"""Pulumi dynamic providers for Kubernetes operations.

These replace pulumi_command.local.Command instances with proper Pulumi resources
that use the kubernetes Python client directly, providing:
- No shell escaping issues (cross-platform)
- No kubectl dependency at runtime for these operations
- Proper create/diff lifecycle in Pulumi state
- Credentials not exposed in process lists
"""

# ruff: noqa: SIM105
# pyright: reportIncompatibleMethodOverride=false

from __future__ import annotations

from typing import Any

import pulumi
from pulumi.dynamic import CreateResult, DiffResult, ResourceProvider, UpdateResult

from helpers import k8s_ops

# ──────────────────────────────────────────────────────────────
# CopyCA: read a TLS secret CA cert, create ConfigMap in target namespace
# ──────────────────────────────────────────────────────────────


def _input_diff(olds: dict[str, Any], news: dict[str, Any], keys: list[str]) -> DiffResult:
    """Compare specific input keys and return a DiffResult."""
    changes = any(olds.get(k) != news.get(k) for k in keys)
    return DiffResult(changes=changes, replaces=[], stables=[], delete_before_replace=False)


class _CopyCAProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        ca_crt = k8s_ops.read_secret_data(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["secret_name"],
            inputs["source_namespace"],
            "ca.crt",
        )
        k8s_ops.ensure_configmap(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["configmap_name"],
            inputs["target_namespace"],
            {"ca.crt": ca_crt},
        )
        return CreateResult(
            id_=f"{inputs['target_namespace']}/{inputs['configmap_name']}",
            outs={**inputs, "ca_crt": ca_crt},
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["secret_name", "source_namespace", "configmap_name", "target_namespace"])

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        k8s_ops.delete_configmap(
            props["kubeconfig_path"],
            props["context"],
            props["configmap_name"],
            props["target_namespace"],
        )


class CopyCA(pulumi.dynamic.Resource):
    """Copy a TLS secret's CA cert into a ConfigMap in another namespace."""

    ca_crt: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        secret_name: str,
        source_namespace: str,
        configmap_name: str,
        target_namespace: str,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _CopyCAProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "secret_name": secret_name,
                "source_namespace": source_namespace,
                "configmap_name": configmap_name,
                "target_namespace": target_namespace,
                "ca_crt": None,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# RegisterPlane: wait for TLS secret, read agent CA, create/patch CRD
# ──────────────────────────────────────────────────────────────


class _RegisterPlaneProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        # Wait for the agent TLS secret to be ready
        k8s_ops.wait_for_secret_type(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["secret_name"],
            inputs["namespace"],
            timeout=inputs.get("timeout", 240),
        )

        # Read the agent CA cert
        ca_crt = k8s_ops.read_secret_data(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["secret_name"],
            inputs["namespace"],
            "ca.crt",
        )

        # Build the custom resource body
        spec = {
            "planeID": "default",
            "clusterAgent": {"clientCA": {"value": ca_crt}},
            **inputs.get("extra_spec", {}),
        }

        if inputs.get("secret_store_ref"):
            spec["secretStoreRef"] = inputs["secret_store_ref"]

        body = {
            "apiVersion": f"{inputs['group']}/{inputs['version']}",
            "kind": inputs["kind"],
            "metadata": {"name": inputs["cr_name"]},
            "spec": spec,
        }

        k8s_ops.apply_cluster_custom_object(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["group"],
            inputs["version"],
            inputs["plural"],
            inputs["cr_name"],
            body,
        )

        return CreateResult(id_=inputs["cr_name"], outs={**inputs, "ca_crt": ca_crt})

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(
            olds, news, ["kind", "cr_name", "secret_name", "namespace", "extra_spec", "secret_store_ref"]
        )

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        k8s_ops.delete_cluster_custom_object(
            props["kubeconfig_path"],
            props["context"],
            props["group"],
            props["version"],
            props["plural"],
            props["cr_name"],
        )


class RegisterPlane(pulumi.dynamic.Resource):
    """Wait for agent TLS secret and register a ClusterXxxPlane custom resource."""

    ca_crt: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        namespace: str,
        kind: str,
        cr_name: str = "default",
        secret_name: str = "cluster-agent-tls",
        group: str = "openchoreo.dev",
        version: str = "v1alpha1",
        plural: str | None = None,
        extra_spec: dict | None = None,
        secret_store_ref: dict | None = None,
        timeout: int = 240,
        opts: pulumi.ResourceOptions | None = None,
    ):
        # Derive plural from kind: ClusterDataPlane -> clusterdataplanes
        if plural is None:
            plural = kind.lower() + "s"

        super().__init__(
            _RegisterPlaneProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "namespace": namespace,
                "kind": kind,
                "cr_name": cr_name,
                "secret_name": secret_name,
                "group": group,
                "version": version,
                "plural": plural,
                "extra_spec": extra_spec or {},
                "secret_store_ref": secret_store_ref,
                "timeout": timeout,
                "ca_crt": None,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# LinkPlanes: patch DP/WP with observability plane reference
# ──────────────────────────────────────────────────────────────


class _LinkPlanesProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        patch = {"spec": {"observabilityPlaneRef": {"kind": "ClusterObservabilityPlane", "name": "default"}}}

        for plural in inputs["plurals"]:
            k8s_ops.patch_cluster_custom_object(
                inputs["kubeconfig_path"],
                inputs["context"],
                inputs["group"],
                inputs["version"],
                plural,
                "default",
                patch,
            )

        return CreateResult(id_="link-planes", outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["plurals", "group", "version"])

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        # Remove the observabilityPlaneRef from patched resources
        patch = {"spec": {"observabilityPlaneRef": None}}
        for plural in props["plurals"]:
            try:
                k8s_ops.patch_cluster_custom_object(
                    props["kubeconfig_path"],
                    props["context"],
                    props["group"],
                    props["version"],
                    plural,
                    "default",
                    patch,
                )
            except Exception:
                pass  # resource may already be deleted


class LinkPlanes(pulumi.dynamic.Resource):
    """Patch ClusterDataPlane and ClusterWorkflowPlane with observability ref."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        group: str = "openchoreo.dev",
        version: str = "v1alpha1",
        plurals: list[str] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        if plurals is None:
            plurals = ["clusterdataplanes", "clusterworkflowplanes"]

        super().__init__(
            _LinkPlanesProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "group": group,
                "version": version,
                "plurals": plurals,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# LabelNamespace: add labels to a namespace
# ──────────────────────────────────────────────────────────────


class _LabelNamespaceProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        k8s_ops.patch_namespace_labels(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["namespace"],
            inputs["labels"],
        )
        return CreateResult(id_=inputs["namespace"], outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["namespace", "labels"])

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        k8s_ops.remove_namespace_labels(
            props["kubeconfig_path"],
            props["context"],
            props["namespace"],
            list(props["labels"].keys()),
        )


class LabelNamespace(pulumi.dynamic.Resource):
    """Add labels to a Kubernetes namespace."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        namespace: str,
        labels: dict[str, str],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _LabelNamespaceProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "namespace": namespace,
                "labels": labels,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# WaitPodReady: wait for a pod to become Ready
# ──────────────────────────────────────────────────────────────


class _WaitPodReadyProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        k8s_ops.wait_for_pod_ready(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["pod_name"],
            inputs["namespace"],
            timeout=inputs.get("timeout", 240),
        )
        return CreateResult(id_=f"{inputs['namespace']}/{inputs['pod_name']}", outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["pod_name", "namespace"])

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # read-only wait — nothing to clean up


class WaitPodReady(pulumi.dynamic.Resource):
    """Wait for a pod to become Ready."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        pod_name: str,
        namespace: str,
        timeout: int = 240,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _WaitPodReadyProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "pod_name": pod_name,
                "namespace": namespace,
                "timeout": timeout,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# WaitDeployments: wait for deployments to become Available
# ──────────────────────────────────────────────────────────────


class _WaitDeploymentsProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        k8s_ops.wait_for_deployments_available(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["deployment_names"],
            inputs["namespace"],
            timeout=inputs.get("timeout", 600),
        )
        return CreateResult(id_=f"{inputs['namespace']}/deployments", outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["deployment_names", "namespace"])

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # read-only wait — nothing to clean up


class WaitDeployments(pulumi.dynamic.Resource):
    """Wait for multiple deployments to become Available."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        deployment_names: list[str],
        namespace: str,
        timeout: int = 600,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _WaitDeploymentsProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "deployment_names": deployment_names,
                "namespace": namespace,
                "timeout": timeout,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# OpenBaoSecrets: store secrets in OpenBao via hvac
# ──────────────────────────────────────────────────────────────


class _OpenBaoSecretsProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        import subprocess
        import time as _time

        import hvac

        # Port-forward OpenBao so hvac can reach it from the host
        port = int(inputs["local_port"])
        pf = subprocess.Popen(
            [
                "kubectl",
                "port-forward",
                f"pod/{inputs['pod_name']}",
                f"{port}:8200",
                "-n",
                inputs["namespace"],
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            _time.sleep(3)  # wait for port-forward to establish
            client = hvac.Client(
                url=f"http://127.0.0.1:{port}",
                token=inputs["root_token"],
            )
            for secret in inputs["secrets"]:
                client.secrets.kv.v2.create_or_update_secret(
                    path=secret["path"],
                    secret=secret["data"],
                    mount_point=inputs.get("mount_point", "secret"),
                )
        finally:
            pf.terminate()
            pf.wait(timeout=5)

        return CreateResult(id_="openbao-secrets", outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["secrets", "mount_point"])

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # secrets are cleaned up when the cluster is destroyed


class OpenBaoSecrets(pulumi.dynamic.Resource):
    """Store secrets in OpenBao using the hvac Python library via port-forward."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        namespace: str,
        root_token: str,
        secrets: list[dict],
        pod_name: str = "openbao-0",
        local_port: int = 18200,
        mount_point: str = "secret",
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _OpenBaoSecretsProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "namespace": namespace,
                "root_token": root_token,
                "secrets": secrets,
                "pod_name": pod_name,
                "local_port": local_port,
                "mount_point": mount_point,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# ValidateOpenBaoSecrets: check that expected secrets exist in OpenBao
# ──────────────────────────────────────────────────────────────


class _ValidateOpenBaoSecretsProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        k8s_ops.validate_openbao_secrets(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["namespace"],
            inputs["root_token"],
            inputs["expected_paths"],
            pod_name=inputs.get("pod_name", "openbao-0"),
            local_port=inputs.get("local_port", 18201),
        )
        return CreateResult(id_="validate-openbao", outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["expected_paths"])

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        result = self.create(news)
        return UpdateResult(outs=result.outs)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # read-only validation


class ValidateOpenBaoSecrets(pulumi.dynamic.Resource):
    """Validate that expected secrets exist in OpenBao with correct fields."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        namespace: str,
        root_token: str,
        expected_paths: list[dict],
        pod_name: str = "openbao-0",
        local_port: int = 18201,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _ValidateOpenBaoSecretsProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "namespace": namespace,
                "root_token": root_token,
                "expected_paths": expected_paths,
                "pod_name": pod_name,
                "local_port": local_port,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# WaitCustomResourceCondition: wait for a CR condition to be True
# ──────────────────────────────────────────────────────────────


class _WaitCRConditionProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        k8s_ops.wait_for_custom_resource_condition(
            inputs["kubeconfig_path"],
            inputs["context"],
            inputs["group"],
            inputs["version"],
            inputs["plural"],
            inputs["name"],
            inputs.get("namespace"),
            condition_type=inputs.get("condition_type", "Ready"),
            timeout=inputs.get("timeout", 300),
        )
        resource_id = f"{inputs['plural']}/{inputs.get('namespace', 'cluster')}/{inputs['name']}"
        return CreateResult(id_=resource_id, outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        return _input_diff(olds, news, ["group", "version", "plural", "name", "namespace", "condition_type"])

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # read-only wait


class WaitCustomResourceCondition(pulumi.dynamic.Resource):
    """Wait for a custom resource to report a condition as True."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        group: str,
        version: str,
        plural: str,
        resource_name: str,
        namespace: str | None = None,
        condition_type: str = "Ready",
        timeout: int = 300,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _WaitCRConditionProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "group": group,
                "version": version,
                "plural": plural,
                "name": resource_name,
                "namespace": namespace,
                "condition_type": condition_type,
                "timeout": timeout,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# IntegrationTest: run a health check against a deployed service
# ──────────────────────────────────────────────────────────────

# Test type constants
TEST_HTTPROUTE_STATUS = "httproute_status"
TEST_SERVICE_HTTP = "service_http"
TEST_DEPLOYMENT = "deployment"
TEST_STATEFULSET = "statefulset"
TEST_DAEMONSET = "daemonset"
TEST_CRD = "crd"
TEST_DEPLOY_LABEL = "deploy_label"
TEST_CR_CONDITION = "cr_condition"
TEST_SECRET_EXISTS = "secret_exists"
TEST_OPENBAO_SECRETS = "openbao_secrets"


class _IntegrationTestProvider(ResourceProvider):
    def _run_check(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Run the integration test and return outs dict."""
        test_type = inputs["test_type"]
        kp = inputs["kubeconfig_path"]
        ctx = inputs["context"]
        result: dict[str, object]

        if test_type == TEST_HTTPROUTE_STATUS:
            result = k8s_ops.check_httproute_accepted(
                kp,
                ctx,
                inputs["route_name"],
                inputs["route_namespace"],
            )
        elif test_type == TEST_SERVICE_HTTP:
            result = k8s_ops.check_service_http(
                kp,
                ctx,
                inputs["service_name"],
                inputs["namespace"],
                int(inputs["service_port"]),
                path=inputs.get("path", "/"),
                expected_statuses=inputs.get("expected_statuses", [200]),
                timeout=int(inputs.get("timeout", 30)),
            )
        elif test_type == TEST_DEPLOYMENT:
            result = k8s_ops.check_deployment_ready(
                kp,
                ctx,
                inputs["resource_name"],
                inputs["namespace"],
            )
        elif test_type == TEST_STATEFULSET:
            result = k8s_ops.check_statefulset_ready(
                kp,
                ctx,
                inputs["resource_name"],
                inputs["namespace"],
            )
        elif test_type == TEST_DAEMONSET:
            result = k8s_ops.check_daemonset_ready(
                kp,
                ctx,
                inputs["resource_name"],
                inputs["namespace"],
            )
        elif test_type == TEST_CRD:
            result = k8s_ops.check_crd_exists(kp, ctx, inputs["crd_name"])
        elif test_type == TEST_DEPLOY_LABEL:
            result = k8s_ops.check_deployments_by_label(
                kp,
                ctx,
                inputs["namespace"],
                inputs["label_selector"],
            )
        elif test_type == TEST_CR_CONDITION:
            result = k8s_ops.check_custom_resource_condition(
                kp,
                ctx,
                inputs["cr_group"],
                inputs["cr_version"],
                inputs["cr_plural"],
                inputs["resource_name"],
                inputs.get("namespace") or None,
                condition_type=inputs.get("condition_type", "Ready"),
            )
        elif test_type == TEST_SECRET_EXISTS:
            result = k8s_ops.check_secret_exists(
                kp,
                ctx,
                inputs["resource_name"],
                inputs["namespace"],
                expected_keys=inputs.get("expected_keys"),
            )
        elif test_type == TEST_OPENBAO_SECRETS:
            result = k8s_ops.check_openbao_secrets(
                kp,
                ctx,
                inputs["namespace"],
                inputs["root_token"],
                inputs["expected_paths"],
                pod_name=inputs.get("pod_name", "openbao-0"),
                local_port=inputs.get("local_port", 18202),
            )
        else:
            msg = f"Unknown test type: {test_type}"
            raise ValueError(msg)

        test_name = inputs["test_name"]
        passed = result.get("passed", False)

        if not passed:
            msg = f"Integration test FAILED: {test_name} — {result}"
            raise RuntimeError(msg)

        pulumi.log.info(f"Integration test PASSED: {test_name}", resource=None)
        return {**inputs, "result": str(result), "passed": True}

    def create(self, inputs: dict[str, Any]) -> CreateResult:
        outs = self._run_check(inputs)
        return CreateResult(id_=f"test-{inputs['test_name']}", outs=outs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        # Always re-run on every `pulumi up` to validate live state
        return DiffResult(changes=True, replaces=[], stables=[], delete_before_replace=False)

    def update(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> UpdateResult:
        return UpdateResult(outs=self._run_check(news))

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass  # read-only check — nothing to clean up


class IntegrationTest(pulumi.dynamic.Resource):
    """Run an integration health check against a deployed service.

    Always re-runs on every ``pulumi up`` so the check reflects live cluster state.
    Fails the Pulumi operation if the check does not pass.
    """

    passed: pulumi.Output[bool]
    result: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        test_name: str,
        test_type: str,
        *,
        # For HTTPRoute status tests
        route_name: str = "",
        route_namespace: str = "",
        # For service HTTP tests
        service_name: str = "",
        service_port: int = 0,
        path: str = "/",
        expected_statuses: list[int] | None = None,
        timeout: int = 30,
        # For deployment/statefulset/daemonset tests
        namespace: str = "",
        resource_name: str = "",
        # For deploy_label tests
        label_selector: str = "",
        # For CRD tests
        crd_name: str = "",
        # For CR condition tests
        cr_group: str = "",
        cr_version: str = "",
        cr_plural: str = "",
        condition_type: str = "Ready",
        # For secret exists tests
        expected_keys: list[str] | None = None,
        # For OpenBao secret validation tests
        root_token: str = "",
        expected_paths: list[dict] | None = None,
        pod_name: str = "openbao-0",
        local_port: int = 18202,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _IntegrationTestProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "test_name": test_name,
                "test_type": test_type,
                "route_name": route_name,
                "route_namespace": route_namespace,
                "service_name": service_name,
                "service_port": service_port,
                "namespace": namespace,
                "path": path,
                "expected_statuses": expected_statuses or [200],
                "timeout": timeout,
                "resource_name": resource_name,
                "label_selector": label_selector,
                "crd_name": crd_name,
                "cr_group": cr_group,
                "cr_version": cr_version,
                "cr_plural": cr_plural,
                "condition_type": condition_type,
                "expected_keys": expected_keys,
                "root_token": root_token,
                "expected_paths": expected_paths or [],
                "pod_name": pod_name,
                "local_port": local_port,
                "passed": None,
                "result": None,
            },
            opts,
        )
