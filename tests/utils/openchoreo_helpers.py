"""OpenChoreo CRD helper functions for E2E tests."""

from typing import Any

from kubernetes import client
from kubernetes.client.rest import ApiException


OPENCHOREO_GROUP = "core.openchoreo.dev"
OPENCHOREO_VERSION = "v1alpha1"


def get_openchoreo_resource(
    custom_api: client.CustomObjectsApi,
    plural: str,
    name: str,
    namespace: str = "default",
    group: str = OPENCHOREO_GROUP,
    version: str = OPENCHOREO_VERSION,
) -> dict[str, Any] | None:
    """Get a single OpenChoreo custom resource.

    Args:
        custom_api: Kubernetes Custom Objects API client
        plural: Resource plural name (e.g., 'components', 'releasebindings')
        name: Resource name
        namespace: Namespace (default: 'default')
        group: API group (default: core.openchoreo.dev)
        version: API version (default: v1alpha1)

    Returns:
        Resource dict or None if not found
    """
    try:
        return custom_api.get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=name,
        )
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def list_openchoreo_resources(
    custom_api: client.CustomObjectsApi,
    plural: str,
    namespace: str = "default",
    label_selector: str = "",
    group: str = OPENCHOREO_GROUP,
    version: str = OPENCHOREO_VERSION,
) -> list[dict[str, Any]]:
    """List OpenChoreo custom resources with optional label filter.

    Args:
        custom_api: Kubernetes Custom Objects API client
        plural: Resource plural name
        namespace: Namespace (default: 'default')
        label_selector: Label selector string (e.g., 'openchoreo.dev/component=frontend')
        group: API group
        version: API version

    Returns:
        List of resource dicts
    """
    kwargs: dict[str, Any] = {
        "group": group,
        "version": version,
        "namespace": namespace,
        "plural": plural,
    }
    if label_selector:
        kwargs["label_selector"] = label_selector

    result = custom_api.list_namespaced_custom_object(**kwargs)
    return result.get("items", [])


def get_resource_condition(
    resource: dict[str, Any],
    condition_type: str,
) -> dict[str, Any] | None:
    """Get a specific condition from a resource's status.

    Args:
        resource: Resource dict from Kubernetes API
        condition_type: Type of condition (e.g., 'Ready', 'ConnectionsResolved')

    Returns:
        Condition dict or None if not found
    """
    conditions = resource.get("status", {}).get("conditions", [])
    for condition in conditions:
        if condition.get("type") == condition_type:
            return condition
    return None


def find_data_plane_namespace(
    core_api: client.CoreV1Api,
    project: str = "doclet",
    environment: str = "development",
) -> str | None:
    """Find the data plane namespace for a given project and environment.

    OpenChoreo creates namespaces like: dp-default-{project}-{environment}-{hash}

    Args:
        core_api: Kubernetes Core V1 API client
        project: Project name
        environment: Environment name

    Returns:
        Namespace name or None if not found
    """
    prefix = f"dp-default-{project}-{environment}"
    namespaces = core_api.list_namespace()
    for ns in namespaces.items:
        if ns.metadata.name.startswith(prefix):
            return ns.metadata.name
    return None


def find_deployment_by_prefix(
    apps_api: client.AppsV1Api,
    namespace: str,
    name_prefix: str,
) -> Any | None:
    """Find a deployment by name prefix in a namespace.

    Args:
        apps_api: Kubernetes Apps V1 API client
        namespace: Namespace to search
        name_prefix: Deployment name prefix

    Returns:
        Deployment object or None
    """
    deployments = apps_api.list_namespaced_deployment(namespace)
    for d in deployments.items:
        if d.metadata.name.startswith(name_prefix):
            return d
    return None


def extract_env_vars(deployment: Any) -> dict[str, str]:
    """Extract environment variables from the first container in a deployment.

    Args:
        deployment: Kubernetes Deployment object

    Returns:
        Dict of env var name -> value
    """
    containers = deployment.spec.template.spec.containers
    if not containers:
        return {}
    env_list = containers[0].env or []
    return {e.name: (e.value or "") for e in env_list}
