"""Auto-annotate data plane namespaces for OTel auto-instrumentation.

Runs a kubectl command that finds all dp-* namespaces created by OpenChoreo
and annotates them with all supported language injection annotations.
This runs on every `pulumi up` to catch newly created namespaces.
"""

from __future__ import annotations

import pulumi
import pulumi_command as command

from components.otel_operator import LANG_ANNOTATIONS, NS_OBSERVABILITY_PLANE
from config import OpenChoreoConfig


def annotate_dp_namespaces(
    name: str,
    cfg: OpenChoreoConfig,
    depends: list[pulumi.Resource],
    opts: pulumi.ResourceOptions | None = None,
) -> command.local.Command:
    """Annotate all dp-* namespaces with OTel auto-instrumentation annotations.

    Uses the Instrumentation CR in the observability namespace.
    Each language annotation points to: openchoreo-observability-plane/auto-instrumentation
    """
    instr_ref = f"{NS_OBSERVABILITY_PLANE}/auto-instrumentation"

    # Build annotation flags for all languages
    annotation_flags = " ".join(
        f"{ann_key}={instr_ref}" for ann_key in LANG_ANNOTATIONS.values()
    )

    # Script that finds dp-* namespaces and annotates them
    script = f"""
export KUBECONFIG="{cfg.kubeconfig_path}"
CONTEXT_FLAG=""
if [ -n "{cfg.kubeconfig_context}" ]; then
  CONTEXT_FLAG="--context={cfg.kubeconfig_context}"
fi

# Find all dp-* namespaces (created by OpenChoreo for data plane workloads)
NAMESPACES=$(kubectl $CONTEXT_FLAG get ns -l openchoreo.dev/created-by=renderedrelease-controller \
  -o jsonpath='{{range .items[*]}}{{.metadata.name}}{{" "}}{{end}}' 2>/dev/null)

if [ -z "$NAMESPACES" ]; then
  echo "No data plane namespaces found yet. Skipping."
  exit 0
fi

COUNT=0
for NS in $NAMESPACES; do
  kubectl $CONTEXT_FLAG annotate namespace "$NS" \
    {annotation_flags} \
    --overwrite 2>/dev/null
  COUNT=$((COUNT + 1))
done

echo "Annotated $COUNT data plane namespace(s) for OTel auto-instrumentation."
"""

    return command.local.Command(
        name,
        create=script,
        # Re-run on every pulumi up by using a trigger that always changes
        triggers=[pulumi.Output.from_input("always-run")],
        opts=opts or pulumi.ResourceOptions(depends_on=depends),
    )
