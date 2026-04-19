"""Kubernetes Python client helpers for Pulumi dynamic providers.

These functions perform direct Kubernetes API calls, replacing kubectl shell commands.
They are intended to be called from within Pulumi dynamic provider create/update methods.
"""

from __future__ import annotations

import base64
import os
import time

import pulumi
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config


def _load_config(kubeconfig_path: str, context: str) -> None:
    """Load kube config once per call."""
    k8s_config.load_kube_config(config_file=kubeconfig_path, context=context)


def wait_for_pod_ready(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
    timeout: int = 240,
    poll_interval: int = 5,
) -> None:
    """Wait for a pod to reach Ready condition (replacement for kubectl wait pod)."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        pod = v1.read_namespaced_pod(name, namespace)
        if pod.status and pod.status.conditions:
            for cond in pod.status.conditions:
                if cond.type == "Ready" and cond.status == "True":
                    return
        time.sleep(poll_interval)

    msg = f"Timeout waiting for pod {namespace}/{name} to become Ready after {timeout}s"
    raise TimeoutError(msg)


def wait_for_secret_type(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
    expected_type: str = "kubernetes.io/tls",
    timeout: int = 240,
    poll_interval: int = 5,
) -> None:
    """Wait for a secret to exist with the expected type (replacement for kubectl wait secret)."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            secret = v1.read_namespaced_secret(name, namespace)
            if secret.type == expected_type:
                return
        except k8s_client.ApiException as e:
            if e.status != 404:
                raise
        time.sleep(poll_interval)

    msg = f"Timeout waiting for secret {namespace}/{name} with type={expected_type} after {timeout}s"
    raise TimeoutError(msg)


def wait_for_deployments_available(
    kubeconfig_path: str,
    context: str,
    names: list[str],
    namespace: str,
    timeout: int = 600,
    poll_interval: int = 10,
) -> None:
    """Wait for multiple deployments to reach Available condition."""
    _load_config(kubeconfig_path, context)
    apps = k8s_client.AppsV1Api()
    deadline = time.monotonic() + timeout

    remaining = set(names)
    while time.monotonic() < deadline and remaining:
        for dep_name in list(remaining):
            try:
                dep = apps.read_namespaced_deployment(dep_name, namespace)
                if dep.status and dep.status.conditions:
                    for cond in dep.status.conditions:
                        if cond.type == "Available" and cond.status == "True":
                            remaining.discard(dep_name)
                            break
            except k8s_client.ApiException as e:
                if e.status != 404:
                    raise
        if remaining:
            time.sleep(poll_interval)

    if remaining:
        msg = f"Timeout waiting for deployments {remaining} in {namespace} after {timeout}s"
        raise TimeoutError(msg)


def read_secret_data(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
    key: str,
) -> str:
    """Read and base64-decode a single key from a Kubernetes secret."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    secret = v1.read_namespaced_secret(name, namespace)
    raw = secret.data.get(key)
    if raw is None:
        msg = f"Key '{key}' not found in secret {namespace}/{name}"
        raise KeyError(msg)
    return base64.b64decode(raw).decode()


def ensure_configmap(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
    data: dict[str, str],
) -> None:
    """Create or update a ConfigMap (replacement for kubectl create configmap --dry-run | apply)."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()

    body = k8s_client.V1ConfigMap(
        metadata=k8s_client.V1ObjectMeta(name=name, namespace=namespace),
        data=data,
    )
    try:
        v1.create_namespaced_config_map(namespace, body)
    except k8s_client.ApiException as e:
        if e.status == 409:
            v1.patch_namespaced_config_map(name, namespace, body)
        else:
            raise


def patch_namespace_labels(
    kubeconfig_path: str,
    context: str,
    namespace: str,
    labels: dict[str, str],
) -> None:
    """Add/update labels on a namespace (replacement for kubectl label namespace)."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    body = k8s_client.V1Namespace(metadata=k8s_client.V1ObjectMeta(labels=labels))
    v1.patch_namespace(namespace, body)


def apply_cluster_custom_object(
    kubeconfig_path: str,
    context: str,
    group: str,
    version: str,
    plural: str,
    name: str,
    body: dict,
) -> None:
    """Create or patch a cluster-scoped custom object (replacement for kubectl apply -f -)."""
    _load_config(kubeconfig_path, context)
    custom = k8s_client.CustomObjectsApi()

    try:
        custom.create_cluster_custom_object(group, version, plural, body)
    except k8s_client.ApiException as e:
        if e.status == 409:
            custom.patch_cluster_custom_object(group, version, plural, name, body)
        else:
            raise


def patch_cluster_custom_object(
    kubeconfig_path: str,
    context: str,
    group: str,
    version: str,
    plural: str,
    name: str,
    patch: dict,
) -> None:
    """Merge-patch a cluster-scoped custom object (replacement for kubectl patch)."""
    _load_config(kubeconfig_path, context)
    custom = k8s_client.CustomObjectsApi()
    custom.patch_cluster_custom_object(group, version, plural, name, patch)


def delete_configmap(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
) -> None:
    """Delete a ConfigMap, ignoring 404."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    try:
        v1.delete_namespaced_config_map(name, namespace)
    except k8s_client.ApiException as e:
        if e.status != 404:
            raise


def delete_cluster_custom_object(
    kubeconfig_path: str,
    context: str,
    group: str,
    version: str,
    plural: str,
    name: str,
) -> None:
    """Delete a cluster-scoped custom object, ignoring 404."""
    _load_config(kubeconfig_path, context)
    custom = k8s_client.CustomObjectsApi()
    try:
        custom.delete_cluster_custom_object(group, version, plural, name)
    except k8s_client.ApiException as e:
        if e.status != 404:
            raise


def remove_namespace_labels(
    kubeconfig_path: str,
    context: str,
    namespace: str,
    label_keys: list[str],
) -> None:
    """Remove labels from a namespace using a strategic-merge patch."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    # Setting a label value to None in a strategic merge patch removes it
    patch_body = {"metadata": {"labels": {k: None for k in label_keys}}}
    v1.patch_namespace(namespace, patch_body)


# ──────────────────────────────────────────────────────────────
# Integration test helpers
# ──────────────────────────────────────────────────────────────


def check_httproute_accepted(
    kubeconfig_path: str,
    context: str,
    route_name: str,
    route_namespace: str,
) -> dict[str, object]:
    """Verify a Gateway API HTTPRoute has been accepted by its parent gateway.

    Checks that both ``Accepted`` and ``ResolvedRefs`` conditions are ``True``
    in the HTTPRoute's ``status.parents[*].conditions``.

    Returns a dict with ``passed``, ``conditions``, and optional ``error``.
    """
    _load_config(kubeconfig_path, context)
    custom = k8s_client.CustomObjectsApi()
    try:
        route = custom.get_namespaced_custom_object(
            "gateway.networking.k8s.io",
            "v1",
            route_namespace,
            "httproutes",
            route_name,
        )
    except k8s_client.ApiException as e:
        return {"passed": False, "error": f"HTTPRoute {route_namespace}/{route_name} not found: {e.status}"}

    parents = (route.get("status") or {}).get("parents") or []
    if not parents:
        return {"passed": False, "error": f"HTTPRoute {route_namespace}/{route_name} has no parent status"}

    # Collect condition results across all parents
    required = {"Accepted", "ResolvedRefs"}
    found: dict[str, str] = {}
    for parent in parents:
        for cond in parent.get("conditions", []):
            if cond["type"] in required:
                found[cond["type"]] = cond["status"]

    all_ok = all(found.get(r) == "True" for r in required)
    return {"passed": all_ok, "conditions": found, "route": f"{route_namespace}/{route_name}"}


def check_service_http(
    kubeconfig_path: str,
    context: str,
    service_name: str,
    namespace: str,
    service_port: int,
    path: str = "/",
    expected_statuses: list[int] | None = None,
    timeout: int = 30,
) -> dict[str, object]:
    """Port-forward to a Service and check an HTTP endpoint.

    Uses ``kubectl port-forward`` to reach the service from the host, sends an
    HTTP GET, and returns the result.  The port-forward is cleaned up after the
    request completes.

    Returns a dict with ``status_code``, ``body_snippet``, and ``passed``.
    """
    import os
    import shutil
    import socket
    import subprocess
    import urllib.request

    if expected_statuses is None:
        expected_statuses = [200]

    kubectl = shutil.which("kubectl")
    if not kubectl:
        return {"passed": False, "error": "kubectl not found on PATH"}

    kube_path = os.path.expanduser(kubeconfig_path)

    # Pick a free local port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        local_port = s.getsockname()[1]

    pf = subprocess.Popen(
        [
            kubectl,
            "port-forward",
            "--context",
            context,
            "--kubeconfig",
            kube_path,
            "-n",
            namespace,
            f"svc/{service_name}",
            f"{local_port}:{service_port}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for port-forward to become ready
        deadline = time.monotonic() + timeout
        ready = False
        while time.monotonic() < deadline:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", local_port)) == 0:
                    ready = True
                    break
            if pf.poll() is not None:
                err = (pf.stderr.read() or b"").decode()
                return {"passed": False, "error": f"port-forward exited early: {err}"}
            time.sleep(0.5)

        if not ready:
            return {"passed": False, "error": "port-forward did not become ready in time"}

        # Make HTTP request
        url = f"http://127.0.0.1:{local_port}{path}"
        last_err = None
        while time.monotonic() < deadline:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status = resp.status
                    body = resp.read(1024).decode("utf-8", errors="replace")
                    return {
                        "status_code": status,
                        "body_snippet": body[:200],
                        "passed": status in expected_statuses,
                    }
            except urllib.error.HTTPError as e:
                return {
                    "status_code": e.code,
                    "body_snippet": e.read(200).decode("utf-8", errors="replace"),
                    "passed": e.code in expected_statuses,
                }
            except (urllib.error.URLError, OSError) as e:
                pulumi.log.warn(f"HTTP request attempt failed: {e}")
                last_err = e
                time.sleep(1)

        return {"passed": False, "error": f"HTTP request failed: {last_err}"}
    finally:
        pf.terminate()
        try:
            pf.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pf.kill()
            pf.wait(timeout=2)


def check_deployment_ready(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
) -> dict[str, object]:
    """Check if a deployment is available. Returns dict with ready, replicas info."""
    _load_config(kubeconfig_path, context)
    apps = k8s_client.AppsV1Api()
    try:
        dep = apps.read_namespaced_deployment(name, namespace)
        available = False
        if dep.status and dep.status.conditions:
            for cond in dep.status.conditions:
                if cond.type == "Available" and cond.status == "True":
                    available = True
                    break
        ready = dep.status.ready_replicas or 0
        desired = dep.spec.replicas or 1
        return {
            "passed": available and ready >= desired,
            "ready_replicas": ready,
            "desired_replicas": desired,
            "available": available,
        }
    except k8s_client.ApiException as e:
        return {"passed": False, "error": f"API error {e.status}: {e.reason}"}


def check_statefulset_ready(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
) -> dict[str, object]:
    """Check if a StatefulSet has all replicas ready."""
    _load_config(kubeconfig_path, context)
    apps = k8s_client.AppsV1Api()
    try:
        ss = apps.read_namespaced_stateful_set(name, namespace)
        ready = ss.status.ready_replicas or 0
        desired = ss.spec.replicas or 1
        return {
            "passed": ready >= desired,
            "ready_replicas": ready,
            "desired_replicas": desired,
        }
    except k8s_client.ApiException as e:
        return {"passed": False, "error": f"API error {e.status}: {e.reason}"}


def check_daemonset_ready(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
) -> dict[str, object]:
    """Check if a DaemonSet has all desired pods ready."""
    _load_config(kubeconfig_path, context)
    apps = k8s_client.AppsV1Api()
    try:
        ds = apps.read_namespaced_daemon_set(name, namespace)
        desired = ds.status.desired_number_scheduled or 0
        ready = ds.status.number_ready or 0
        return {
            "passed": desired > 0 and ready >= desired,
            "ready_pods": ready,
            "desired_pods": desired,
        }
    except k8s_client.ApiException as e:
        return {"passed": False, "error": f"API error {e.status}: {e.reason}"}


def check_crd_exists(
    kubeconfig_path: str,
    context: str,
    crd_name: str,
) -> dict[str, object]:
    """Check if a CRD is established."""
    _load_config(kubeconfig_path, context)
    ext = k8s_client.ApiextensionsV1Api()
    try:
        crd = ext.read_custom_resource_definition(crd_name)
        established = False
        if crd.status and crd.status.conditions:
            for cond in crd.status.conditions:
                if cond.type == "Established" and cond.status == "True":
                    established = True
                    break
        return {"passed": established, "crd": crd_name}
    except k8s_client.ApiException as e:
        if e.status == 404:
            return {"passed": False, "crd": crd_name, "error": "not found"}
        return {"passed": False, "crd": crd_name, "error": f"API error {e.status}"}


def check_deployments_by_label(
    kubeconfig_path: str,
    context: str,
    namespace: str,
    label_selector: str,
) -> dict[str, object]:
    """Check all deployments matching a label selector are available."""
    _load_config(kubeconfig_path, context)
    apps = k8s_client.AppsV1Api()
    try:
        deps = apps.list_namespaced_deployment(namespace, label_selector=label_selector)
        if not deps.items:
            return {"passed": False, "error": f"No deployments matching '{label_selector}' in {namespace}"}
        all_available = True
        details = []
        for dep in deps.items:
            available = False
            if dep.status and dep.status.conditions:
                for cond in dep.status.conditions:
                    if cond.type == "Available" and cond.status == "True":
                        available = True
                        break
            ready = dep.status.ready_replicas or 0
            desired = dep.spec.replicas or 1
            details.append(f"{dep.metadata.name}: {ready}/{desired}")
            if not available or ready < desired:
                all_available = False
        return {"passed": all_available, "deployments": details}
    except k8s_client.ApiException as e:
        return {"passed": False, "error": f"API error {e.status}: {e.reason}"}


def check_custom_resource_condition(
    kubeconfig_path: str,
    context: str,
    group: str,
    version: str,
    plural: str,
    name: str,
    namespace: str | None,
    condition_type: str = "Ready",
) -> dict[str, object]:
    """Check if a CR reports the given condition as True (non-blocking)."""
    _load_config(kubeconfig_path, context)
    api = k8s_client.CustomObjectsApi()
    try:
        if namespace:
            obj = api.get_namespaced_custom_object(group, version, namespace, plural, name)
        else:
            obj = api.get_cluster_custom_object(group, version, plural, name)

        for cond in (obj.get("status") or {}).get("conditions", []):
            if cond.get("type") == condition_type and cond.get("status") == "True":
                return {"passed": True, "resource": f"{plural}/{name}", "condition": condition_type}
        return {
            "passed": False,
            "resource": f"{plural}/{name}",
            "condition": condition_type,
            "error": "condition not True",
        }
    except k8s_client.ApiException as e:
        if e.status == 404:
            return {"passed": False, "resource": f"{plural}/{name}", "error": "not found"}
        return {"passed": False, "resource": f"{plural}/{name}", "error": f"API error {e.status}"}


def check_secret_exists(
    kubeconfig_path: str,
    context: str,
    name: str,
    namespace: str,
    expected_keys: list[str] | None = None,
) -> dict[str, object]:
    """Check a Kubernetes Secret exists and optionally has expected data keys."""
    _load_config(kubeconfig_path, context)
    v1 = k8s_client.CoreV1Api()
    try:
        secret = v1.read_namespaced_secret(name, namespace)
        data_keys = list((secret.data or {}).keys())
        if expected_keys:
            missing = [k for k in expected_keys if k not in data_keys]
            if missing:
                return {"passed": False, "secret": f"{namespace}/{name}", "missing_keys": missing}
        return {"passed": True, "secret": f"{namespace}/{name}", "keys": data_keys}
    except k8s_client.ApiException as e:
        if e.status == 404:
            return {"passed": False, "secret": f"{namespace}/{name}", "error": "not found"}
        return {"passed": False, "secret": f"{namespace}/{name}", "error": f"API error {e.status}"}


def check_openbao_secrets(
    kubeconfig_path: str,
    context: str,
    namespace: str,
    root_token: str,
    expected_paths: list[dict],
    pod_name: str = "openbao-0",
    local_port: int = 18202,
) -> dict[str, object]:
    """Check that expected secrets exist in OpenBao (non-blocking, returns result dict)."""
    import subprocess
    import time as _time

    import hvac

    port = int(local_port)
    kube_path = os.path.expanduser(kubeconfig_path)
    pf = subprocess.Popen(
        [
            "kubectl",
            "port-forward",
            "--kubeconfig",
            kube_path,
            "--context",
            context,
            f"pod/{pod_name}",
            f"{port}:8200",
            "-n",
            namespace,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _time.sleep(3)
        client = hvac.Client(url=f"http://127.0.0.1:{port}", token=root_token)
        errors = []
        for entry in expected_paths:
            path = entry["path"]
            try:
                resp = client.secrets.kv.v2.read_secret_version(path=path, mount_point="secret")
                data = resp.get("data", {}).get("data", {})
                for field in entry.get("fields", []):
                    if field not in data or not data[field]:
                        errors.append(f"secret/{path}: field '{field}' missing or empty")
            except hvac.exceptions.VaultError:
                pulumi.log.warn(f"OpenBao secret '{path}' does not exist or is inaccessible")
                errors.append(f"secret/{path}: does not exist")
        if errors:
            return {"passed": False, "errors": errors}
        return {"passed": True, "validated_paths": [e["path"] for e in expected_paths]}
    except Exception as e:
        pulumi.log.warn(f"OpenBao secret check failed: {e}")
        return {"passed": False, "errors": [str(e)]}
    finally:
        import contextlib

        with contextlib.suppress(ProcessLookupError):
            pf.terminate()
        try:
            pf.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pf.kill()
            pf.wait()


def wait_for_custom_resource_condition(
    kubeconfig_path: str,
    context: str,
    group: str,
    version: str,
    plural: str,
    name: str,
    namespace: str | None,
    condition_type: str = "Ready",
    timeout: int = 300,
) -> None:
    """Poll a custom resource until it reports the given condition as True.

    Works for both namespaced and cluster-scoped resources.
    Raises RuntimeError on timeout.
    """
    _load_config(kubeconfig_path, context)
    api = k8s_client.CustomObjectsApi()
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            if namespace:
                obj = api.get_namespaced_custom_object(group, version, namespace, plural, name)
            else:
                obj = api.get_cluster_custom_object(group, version, plural, name)

            for cond in (obj.get("status") or {}).get("conditions", []):
                if cond.get("type") == condition_type and cond.get("status") == "True":
                    return
        except k8s_client.ApiException:
            pass
        time.sleep(5)

    scope = f"{namespace}/{name}" if namespace else name
    raise RuntimeError(f"Timeout waiting for {plural}/{scope} condition {condition_type}=True after {timeout}s")


def validate_openbao_secrets(
    kubeconfig_path: str,
    context: str,
    namespace: str,
    root_token: str,
    expected_paths: list[dict],
    pod_name: str = "openbao-0",
    local_port: int = 18201,
) -> None:
    """Validate that expected secrets exist in OpenBao with the right fields.

    Each entry in expected_paths should be:
      {"path": "git-token", "fields": ["git-token"]}

    Raises RuntimeError if any secret or field is missing.
    """
    import subprocess
    import time as _time

    import hvac

    port = int(local_port)
    kube_path = os.path.expanduser(kubeconfig_path)
    pf = subprocess.Popen(
        [
            "kubectl",
            "port-forward",
            "--kubeconfig",
            kube_path,
            "--context",
            context,
            f"pod/{pod_name}",
            f"{port}:8200",
            "-n",
            namespace,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _time.sleep(3)
        client = hvac.Client(url=f"http://127.0.0.1:{port}", token=root_token)
        errors = []
        for entry in expected_paths:
            path = entry["path"]
            try:
                resp = client.secrets.kv.v2.read_secret_version(path=path, mount_point="secret")
                data = resp.get("data", {}).get("data", {})
                for field in entry.get("fields", []):
                    if field not in data or not data[field]:
                        errors.append(f"secret/{path}: field '{field}' missing or empty")
            except hvac.exceptions.VaultError:
                pulumi.log.warn(f"OpenBao secret '{path}' does not exist or is inaccessible")
                errors.append(f"secret/{path}: does not exist")
        if errors:
            raise RuntimeError("OpenBao validation failed:\n  " + "\n  ".join(errors))
    finally:
        import contextlib

        with contextlib.suppress(ProcessLookupError):
            pf.terminate()
        try:
            pf.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pf.kill()
            pf.wait()
