"""OpenChoreo infrastructure policy enforcement.

CrossGuard PolicyPack that provides policy-as-code enforcement for the OpenChoreo
project.  Invoked via ``pulumi preview --policy-pack ./policy`` or
``pulumi up --policy-pack ./policy``.

Policies
--------
1. require-secrets-on-prod   — block insecure default credentials on non-dev stacks
2. block-dev-seeds-on-prod   — block dev seed secret commands on non-dev stacks
3. enforce-resource-labels   — warn when K8s Namespaces lack openchoreo.dev labels
4. enforce-helm-timeouts     — require custom timeouts on Helm Chart and Helm Release resources
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
    StackValidationArgs,
    StackValidationPolicy,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Stack names that are considered development environments.
_DEV_STACKS = ("dev", "rancher-desktop", "local", "test")

#: Insecure default credentials that must never appear in non-dev stacks.
#: Mirrors the fail-fast logic in ``config.py:212-227``.
_INSECURE_DEFAULTS: dict[str, str] = {
    "openbao_root_token": "root",
    "opensearch_password": "ThisIsTheOpenSearchPassword1",
}

#: Dev-only seed command patterns (OpenBao ``bao kv put`` seed operations).
_DEV_SEED_PATTERNS: list[str] = [
    "bao kv put secret/",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_stack_name(urn: str) -> str:
    """Extract the stack name from a Pulumi URN.

    URN format: ``urn:pulumi:{stack}::{project}::{type}::{name}``
    """
    parts = urn.split("::")
    if len(parts) >= 1:
        prefix = parts[0]  # "urn:pulumi:{stack}"
        segments = prefix.split(":")
        if len(segments) >= 3:
            return segments[2]
    return ""


def _is_dev_stack_from_resources(resources: list[Any]) -> bool:
    """Determine whether the stack is a dev stack from its resource URNs."""
    for resource in resources:
        stack_name = _extract_stack_name(resource.urn)
        if stack_name:
            return stack_name in _DEV_STACKS
    return False  # If we cannot determine the stack, fail closed — enforce policies.


def _serialize_props(props: Mapping[str, Any]) -> str:
    """Serialize resource properties to a JSON string for pattern scanning."""
    try:
        return json.dumps(dict(props), default=str)
    except (TypeError, ValueError):
        return str(props)


# ---------------------------------------------------------------------------
# Policy 1: require-secrets-on-prod
# ---------------------------------------------------------------------------


def _require_secrets_on_prod_validator(
    args: StackValidationArgs,
    report_violation: ReportViolation,
) -> None:
    """Ensure non-dev stacks do not contain insecure default credentials.

    Scans all resource properties for the known insecure defaults used during
    local development.  This mirrors the runtime fail-fast in ``config.py``
    but enforces it declaratively at the policy layer.
    """
    if _is_dev_stack_from_resources(args.resources):
        return

    for resource in args.resources:
        serialized = _serialize_props(resource.props)
        for key, insecure_value in _INSECURE_DEFAULTS.items():
            if f'"{insecure_value}"' in serialized:
                report_violation(
                    f"Insecure default credentials detected in non-dev stack: "
                    f"{key} contains the dev-only default value. "
                    f"Set an explicit secret via `pulumi config set --secret`.",
                    resource.urn,
                )


require_secrets_on_prod = StackValidationPolicy(
    name="require-secrets-on-prod",
    description=(
        "Non-dev stacks must not use insecure default credentials "
        "(e.g. openbao_root_token='root', opensearch_password='ThisIsTheOpenSearchPassword1')."
    ),
    enforcement_level=EnforcementLevel.MANDATORY,
    validate=_require_secrets_on_prod_validator,
)


# ---------------------------------------------------------------------------
# Policy 2: block-dev-seeds-on-prod
# ---------------------------------------------------------------------------


def _block_dev_seeds_on_prod_validator(
    args: StackValidationArgs,
    report_violation: ReportViolation,
) -> None:
    """Ensure dev-only seed secrets (``bao kv put`` commands) do not leak into
    non-dev stacks.

    The OpenBao post-start script injects seed secrets via ``bao kv put``
    commands.  These must only be present in development environments.
    """
    if _is_dev_stack_from_resources(args.resources):
        return

    for resource in args.resources:
        serialized = _serialize_props(resource.props)
        for pattern in _DEV_SEED_PATTERNS:
            if pattern in serialized:
                report_violation(
                    f"Dev seed secrets found in non-dev stack resources: "
                    f"detected '{pattern}' in resource {resource.name}. "
                    f"Remove dev-only seed data from production configurations.",
                    resource.urn,
                )


block_dev_seeds_on_prod = StackValidationPolicy(
    name="block-dev-seeds-on-prod",
    description=(
        "Non-dev stacks must not contain dev-only seed secret commands "
        "(e.g. 'bao kv put secret/choreo-system-password')."
    ),
    enforcement_level=EnforcementLevel.MANDATORY,
    validate=_block_dev_seeds_on_prod_validator,
)


# ---------------------------------------------------------------------------
# Policy 3: enforce-resource-labels
# ---------------------------------------------------------------------------


def _enforce_resource_labels_validator(
    args: ResourceValidationArgs,
    report_violation: ReportViolation,
) -> None:
    """Warn when Kubernetes Namespace resources lack ``openchoreo.dev`` labels.

    This is advisory because existing namespaces do not yet carry labels — it
    serves as a best-practice nudge for new resources.
    """
    if args.resource_type != "kubernetes:core/v1:Namespace":
        return

    metadata = args.props.get("metadata", {})
    if not isinstance(metadata, dict):
        report_violation("Namespace resource should have openchoreo.dev labels in metadata.")
        return

    labels = metadata.get("labels", {})
    if not isinstance(labels, dict):
        report_violation("Namespace resource should have openchoreo.dev labels.")
        return

    has_openchoreo_label = any(key.startswith("openchoreo.dev") for key in labels)
    if not has_openchoreo_label:
        report_violation(
            f"Namespace '{args.name}' should have at least one label with "
            f"the 'openchoreo.dev' prefix (e.g. 'openchoreo.dev/component')."
        )


enforce_resource_labels = ResourceValidationPolicy(
    name="enforce-resource-labels",
    description=(
        "Kubernetes Namespace resources should carry openchoreo.dev labels for consistent resource identification."
    ),
    enforcement_level=EnforcementLevel.ADVISORY,
    validate=_enforce_resource_labels_validator,
)


# ---------------------------------------------------------------------------
# Policy 4: enforce-helm-timeouts
# ---------------------------------------------------------------------------


def _enforce_helm_timeouts_validator(
    args: ResourceValidationArgs,
    report_violation: ReportViolation,
) -> None:
    """Ensure all Helm Chart and Helm Release resources specify custom timeouts.

    Custom timeouts prevent indefinite hangs during ``pulumi up`` when a Helm
    release takes longer than expected.  The policy checks that at least one of
    the ``custom_timeouts`` values (create, update, delete) is non-zero,
    indicating the resource author deliberately configured timeout behaviour.

    The ``custom_timeouts`` are accessible via ``args.opts.custom_timeouts``
    which exposes ``create_seconds``, ``update_seconds``, and
    ``delete_seconds``.
    """
    if args.resource_type not in ("kubernetes:helm.sh/v4:Chart", "kubernetes:helm.sh/v3:Release"):
        return

    timeouts = args.opts.custom_timeouts
    if timeouts is None:
        report_violation(
            f"Helm resource '{args.name}' must specify custom_timeouts "
            f"(create, update, or delete) to prevent indefinite hangs. "
            f"Use pulumi.ResourceOptions(custom_timeouts=...) when defining the Helm resource."
        )
        return

    has_custom_timeout = timeouts.create_seconds > 0 or timeouts.update_seconds > 0 or timeouts.delete_seconds > 0

    if not has_custom_timeout:
        report_violation(
            f"Helm resource '{args.name}' must specify custom_timeouts "
            f"(create, update, or delete) to prevent indefinite hangs. "
            f"Use pulumi.ResourceOptions(custom_timeouts=...) when defining the Helm resource."
        )


enforce_helm_timeouts = ResourceValidationPolicy(
    name="enforce-helm-timeouts",
    description=(
        "All Helm Chart and Helm Release resources must specify custom_timeouts to prevent indefinite deployment hangs."
    ),
    enforcement_level=EnforcementLevel.MANDATORY,
    validate=_enforce_helm_timeouts_validator,
)


# ---------------------------------------------------------------------------
# PolicyPack
# ---------------------------------------------------------------------------

PolicyPack(
    "openchoreo-policy",
    policies=[
        require_secrets_on_prod,
        block_dev_seeds_on_prod,
        enforce_resource_labels,
        enforce_helm_timeouts,
    ],
)
