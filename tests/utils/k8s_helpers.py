"""Kubernetes API helper functions."""

import time
from typing import Any

from kubernetes import client
from kubernetes.client.rest import ApiException


def wait_for_deployment(
    apps_api: client.AppsV1Api,
    namespace: str,
    name: str,
    timeout: int = 120,
    interval: int = 5,
) -> bool:
    """Wait for a deployment to be ready.

    Args:
        apps_api: Kubernetes Apps V1 API client
        namespace: Namespace of the deployment
        name: Name of the deployment
        timeout: Maximum time to wait in seconds
        interval: Polling interval in seconds

    Returns:
        True if deployment is ready, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            deployment = apps_api.read_namespaced_deployment(name, namespace)
            status = deployment.status
            if status.ready_replicas and status.ready_replicas == status.replicas:
                return True
        except ApiException as e:
            if e.status != 404:
                raise
        time.sleep(interval)
    return False


def get_custom_resource(
    custom_api: client.CustomObjectsApi,
    group: str,
    version: str,
    plural: str,
    name: str,
    namespace: str | None = None,
) -> dict[str, Any] | None:
    """Get a custom resource by name.

    Args:
        custom_api: Kubernetes Custom Objects API client
        group: API group (e.g., 'cert-manager.io')
        version: API version (e.g., 'v1')
        plural: Resource plural name (e.g., 'certificates')
        name: Resource name
        namespace: Namespace (None for cluster-scoped resources)

    Returns:
        Resource dict or None if not found
    """
    try:
        if namespace:
            return custom_api.get_namespaced_custom_object(group, version, namespace, plural, name)
        else:
            return custom_api.get_cluster_custom_object(group, version, plural, name)
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def check_resource_condition(
    resource: dict[str, Any],
    condition_type: str,
    expected_status: str = "True",
) -> bool:
    """Check if a resource has a specific condition.

    Args:
        resource: Resource dict from Kubernetes API
        condition_type: Type of condition to check (e.g., 'Ready')
        expected_status: Expected status value (default: 'True')

    Returns:
        True if condition matches, False otherwise
    """
    conditions = resource.get("status", {}).get("conditions", [])
    for condition in conditions:
        if condition.get("type") == condition_type:
            return condition.get("status") == expected_status
    return False


def list_pods_by_label(
    core_api: client.CoreV1Api,
    namespace: str,
    label_selector: str,
) -> list[client.V1Pod]:
    """List pods matching a label selector.

    Args:
        core_api: Kubernetes Core V1 API client
        namespace: Namespace to search
        label_selector: Label selector string (e.g., 'app=nginx')

    Returns:
        List of matching pods
    """
    pods = core_api.list_namespaced_pod(namespace, label_selector=label_selector)
    return pods.items


def get_pod_by_name_prefix(
    core_api: client.CoreV1Api,
    namespace: str,
    name_prefix: str,
) -> client.V1Pod | None:
    """Get first pod matching a name prefix.

    Args:
        core_api: Kubernetes Core V1 API client
        namespace: Namespace to search
        name_prefix: Pod name prefix

    Returns:
        First matching pod or None
    """
    pods = core_api.list_namespaced_pod(namespace)
    for pod in pods.items:
        if pod.metadata.name.startswith(name_prefix):
            return pod
    return None


def get_secret_data(
    core_api: client.CoreV1Api,
    namespace: str,
    name: str,
) -> dict[str, str] | None:
    """Get decoded secret data.

    Args:
        core_api: Kubernetes Core V1 API client
        namespace: Namespace of the secret
        name: Secret name

    Returns:
        Dict of decoded secret data or None if not found
    """
    import base64

    try:
        secret = core_api.read_namespaced_secret(name, namespace)
        if secret.data:
            return {
                key: base64.b64decode(value).decode("utf-8") for key, value in secret.data.items()
            }
        return {}
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def check_deployment_ready(
    apps_api: client.AppsV1Api,
    namespace: str,
    name: str,
) -> tuple[bool, str]:
    """Check if a deployment is ready.

    Args:
        apps_api: Kubernetes Apps V1 API client
        namespace: Namespace of the deployment
        name: Name of the deployment

    Returns:
        Tuple of (is_ready, message)
    """
    try:
        deployment = apps_api.read_namespaced_deployment(name, namespace)
        status = deployment.status

        if not status:
            return False, "No status available"

        ready = status.ready_replicas or 0
        desired = status.replicas or 0

        if ready == desired and desired > 0:
            return True, f"{ready}/{desired} replicas ready"
        else:
            return False, f"{ready}/{desired} replicas ready"

    except ApiException as e:
        if e.status == 404:
            return False, f"Deployment {name} not found"
        return False, f"API error: {e.reason}"


def get_service_endpoints(
    core_api: client.CoreV1Api,
    namespace: str,
    service_name: str,
) -> list[str]:
    """Get endpoint addresses for a service.

    Args:
        core_api: Kubernetes Core V1 API client
        namespace: Namespace of the service
        service_name: Service name

    Returns:
        List of endpoint addresses
    """
    try:
        endpoints = core_api.read_namespaced_endpoints(service_name, namespace)
        addresses = []
        if endpoints.subsets:
            for subset in endpoints.subsets:
                if subset.addresses:
                    for addr in subset.addresses:
                        addresses.append(addr.ip)
        return addresses
    except ApiException:
        return []
