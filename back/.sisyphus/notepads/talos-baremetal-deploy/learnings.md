## Notepad: Learnings

- Added bare-metal Cilium L2 settings at the end of `PlatformProfile` so dataclass default ordering stays valid.
- Used `tuple[str, ...]` defaults for CIDR and interface lists to keep the profile immutable.
- `Pulumi.dev.yaml` keeps existing keys intact; add new project-prefixed config entries under `config:` with two-space indentation.
- `certSans` must remain a YAML string containing JSON array syntax, not a native YAML list.
- Exposed bare-metal L2 pool/interface overrides on `talos_baremetal()` so callers can customize announcements without changing the profile defaults.
- In Pulumi Kubernetes Python, `k8s.apiextensions.CustomResource` accepts top-level `spec=...`; using `other_fields` triggers type-check errors, so Cilium L2 CRDs should pass `spec` directly and depend on the Cilium chart.
- Split Talos machine-config patch rendering into a pure-Python `patches.py` module with module-level runtime config set from `__main__.py`, keeping Pulumi resources and dependency chain untouched.
- For bare-metal Talos install image patching, use `factory.talos.dev/metal-installer/{schematic_id}:{talos_version}` and keep `machine.install.diskSelector.wwid` in storage patch instead of `machine.install.disk`.
- Aggregating optional patch outputs via `[p for p in [... ] if p]` mirrors Terraform `compact(concat(...))` behavior and safely filters disabled cloudflared/NVIDIA raw YAML patches.
- Pulumi dev config keys must be snake_case to match `cfg.get(...)`; include `install_disk_wwid` alongside the WWID install disk path for bare-metal Talos installs.
- Added pytest coverage for all 8 patch renderers in pulumi/talos-cluster-baremetal/patches.py.
- Fixed pyproject requires-python to >=3.12 so uv sync works on system Python 3.14.x.
- The test suite validates JSON patch structure with json.loads and checks raw YAML patch strings directly.
