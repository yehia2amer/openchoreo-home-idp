# Learnings — gateway-mode-compliance

## Inherited from Plan A (talos-baremetal-deploy)
- Use `k8s.helm.v3.Release` (NOT v4.Chart) for Helm releases in Phase 1
- Use explicit namespace creation (NOT `create_namespace=True` on Helm)
- `k8s.yaml.v2.ConfigGroup` uses `files=` for remote URL lists, `yaml=` for inline YAML strings
- GPG signing fails — must use `git commit --no-gpg-sign`
- `.sisyphus/boulder.json` gets corrupted by subagents — always `git checkout -- .sisyphus/boulder.json` after subagent returns
- Ruff path Phase 1: `pulumi/talos-cluster-baremetal/.venv/bin/ruff`
- Python Phase 1: `pulumi/talos-cluster-baremetal/.venv/bin/python`
- Python Phase 2: `pulumi/.venv/bin/python` (run with workdir=`pulumi/`)
- Pulumi binary: `/opt/homebrew/bin/pulumi` (needs `PATH="/opt/homebrew/bin:$PATH"`)
- uv binary: `/opt/homebrew/bin/uv` (needed by pulumi for package resolution)
- PULUMI_CONFIG_PASSPHRASE Phase 1: `"openchoreo-talos-baremetal-dev"`
- talos_baremetal must use `gateway_mode="kgateway"` while keeping `cni_mode="cilium"`

## 2026-04-01
- Disabled Cilium Gateway API in Phase 1 by setting `gatewayAPI.enabled=false` only; left all other Cilium values unchanged.
- Added `retain_on_delete=True` to the six Gateway API CRD ConfigFile resources so existing clusters keep the CRDs while Phase 2 owns definitive installs.
- Removed the Cilium Helm release dependency on `gateway_api_crd_resources`; CRD ownership is now decoupled from the Cilium release.
- Phase 2 `pulumi/__main__.py` now documents that `cilium_enabled` means Cilium as the Gateway API controller, not Cilium-as-CNI.

## 2026-04-01 — workflow template URLs
- Added optional `workflow_template_urls` to `PlatformProfile` so platform-specific workflow filenames can override k3d defaults without changing shared behavior.
- Set Talos baremetal workflow templates to standard filenames: checkout-source.yaml, workflow-templates.yaml, publish-image.yaml, generate-workload.yaml.
- Added listenerName fields to gateway external http/https entries in pulumi/components/data_plane.py so kgateway listeners bind explicitly.

## 2026-04-01 TLS config update
- Added bare-metal TLS constants for self-signed bootstrap CA, OpenChoreo CA, and gateway cert names in `pulumi/config.py`.
- Enabled TLS for `talos-baremetal` via `openchoreo:tls_enabled: "true"` in `Pulumi.talos-baremetal.yaml`.

## 2026-04-01 — T8 TLS setup component
- Added `pulumi/components/tls_setup.py` as a `ComponentResource` that creates the cert-manager TLS chain in strict order: `selfsigned-bootstrap` ClusterIssuer → `openchoreo-ca` Certificate → `openchoreo-ca` ClusterIssuer → `cp-gateway-tls` + `dp-gateway-tls` Certificates.
- Ensured gateway certificate `dnsNames` derive from `cfg.domain_base` (`*.{domain_base}` and `{domain_base}`), with no hardcoded domains.
- Wired `pulumi/__main__.py` to conditionally create `TlsSetup` only when `cfg.tls_enabled` is true and made Control Plane depend on `tls.cp_cert` when present.
- Verification passed from `pulumi/`: `.venv/bin/ruff check components/tls_setup.py __main__.py` and `.venv/bin/python -c "from components import tls_setup"`.

## 2026-04-01 — T6 workflow template URL fix
- `config.py`: workflow_templates_urls now checks `platform.workflow_template_urls` first; falls back to k3d URLs when `None`. This keeps k3d backward-compatible while talos-baremetal gets standard filenames.
- `workflow_plane.py`: Added `standard_sed_templates` set for `generate-workload.yaml` — uses different sed patterns than k3d (replaces `https://host.k3d.internal:8080/oauth2/token` → thunder URL, `http://host.k3d.internal:8080` → api URL).
- `publish-image.yaml` (standard) doesn't match any sed set → plain `kubectl apply` — it uses ttl.sh directly, no patching needed.
- Only `config.py` and `workflow_plane.py` consume `workflow_templates_urls` — safe to modify without broader impact.
- The sed `|` delimiter works the same as `#` — both are non-slash delimiters avoiding escaping issues in URLs.

## 2026-04-01 — Data-plane namespace ordering fix
- Moved `NS_DATA_PLANE` namespace creation into `pulumi/components/prerequisites.py` beside `NS_CONTROL_PLANE`, both gated behind `cert_manager` readiness.
- Extended `PrerequisitesResult` with `data_plane_ns` so downstream components can declare explicit namespace dependencies instead of creating the namespace internally.
- Updated `pulumi/__main__.py` so TLS setup depends on both pre-created namespaces and Data Plane deployment depends on `prereqs.data_plane_ns` plus optional `tls.dp_cert`.
- Simplified `pulumi/components/data_plane.py` by removing internal namespace creation and making `copy_ca` depend on the externally provided `depends` chain.
