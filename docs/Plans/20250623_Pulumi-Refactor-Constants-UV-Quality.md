# Pulumi Refactor: Centralized Constants, UV, Code Quality — Completed

**Date:** 2025-06-23
**Status:** COMPLETED
**Preview:** 369 resources, 7 outputs, 0 errors

---

## Objectives

1. **Centralize magic strings** — Move all hardcoded URLs, namespaces, secret names, timeouts, and sleep durations into `config.py`
2. **Replace requirements.txt with pyproject.toml + uv** — Modern Python packaging and dependency management
3. **Add Ruff and ty** — Lint, format, and type-check the codebase

---

## Changes Made

### 1. Magic String Centralization (`config.py`)

Added 60+ module-level constants organized by category:

| Category | Constants |
|---|---|
| Helm OCI registries | `OPENCHOREO_CHART_REPO`, `CERT_MANAGER_CHART_REPO`, `EXTERNAL_SECRETS_CHART_REPO`, `KGATEWAY_CHART_REPO`, `OPENBAO_CHART_REPO`, `THUNDER_CHART_REPO` |
| Helm HTTP repos | `DOCKER_REGISTRY_HELM_REPO` |
| Namespaces | `NS_CONTROL_PLANE`, `NS_DATA_PLANE`, `NS_WORKFLOW_PLANE`, `NS_OBSERVABILITY_PLANE`, `NS_OPENBAO`, `NS_CERT_MANAGER`, `NS_EXTERNAL_SECRETS`, `NS_THUNDER`, `NS_FLUX_SYSTEM` |
| Secrets | `SECRET_GATEWAY_CA`, `SECRET_AGENT_TLS`, `SECRET_BACKSTAGE`, `SECRET_OPENSEARCH_ADMIN`, `SECRET_OBSERVER_OPENSEARCH`, `SECRET_OBSERVER` |
| K8s resources | `SA_ESO_OPENBAO`, `CLUSTER_SECRET_STORE_NAME` |
| URLs | `THUNDER_INTERNAL_BASE`, `FLUX_INSTALL_URL` |
| API versions | `OPENCHOREO_API_VERSION` |
| Timeouts (seconds) | `TIMEOUT_DEFAULT=600`, `TIMEOUT_OPENSEARCH=900`, `TIMEOUT_OBS_PLANE=1500`, `TIMEOUT_WAIT=300`, `TIMEOUT_TLS_WAIT=120` |
| Sleep durations | `SLEEP_AFTER_GATEWAY_API=5`, `SLEEP_AFTER_OPENBAO=10`, `SLEEP_AFTER_THUNDER=10`, `SLEEP_AFTER_ESO_SYNC=10` |

Added derived URL fields to `OpenChoreoConfig` dataclass:
- `gateway_api_crds_url`, `coredns_rewrite_url`, `thunder_values_url`, `workflow_templates_urls`

Added chart URL properties:
- `thunder_chart`, `cp_chart`, `dp_chart`, `wp_chart`, `obs_chart`, `logs_chart`, `traces_chart`, `metrics_chart`

### 2. Files Updated (14 files)

| File | Changes |
|---|---|
| `config.py` | Added constants, derived URLs, chart properties |
| `components/prerequisites.py` | Replaced 15+ magic strings with constants |
| `components/control_plane.py` | Replaced 10+ magic strings with constants |
| `components/data_plane.py` | Replaced 8+ magic strings with constants |
| `components/workflow_plane.py` | Replaced 8+ magic strings, template URLs from config |
| `components/link_planes.py` | Rewritten (was `test = 1`) |
| `components/observability_plane.py` | Replaced 20+ magic strings, added `_external_secret_yaml()` helper |
| `components/flux_gitops.py` | Replaced 6+ magic strings, added `_kustomization_yaml()` helper |
| `helpers/copy_ca.py` | Uses `NS_CONTROL_PLANE`, `SECRET_GATEWAY_CA` |
| `helpers/register_plane.py` | Uses `SECRET_AGENT_TLS`, `OPENCHOREO_API_VERSION`, `TIMEOUT_TLS_WAIT` |
| `values/observability_plane.py` | Uses `THUNDER_INTERNAL_BASE`, `SECRET_OPENSEARCH_ADMIN`, `SECRET_OBSERVER` |
| `values/control_plane.py` | Uses `SECRET_BACKSTAGE` |
| `__main__.py` | Added `from __future__ import annotations`, sorted imports |
| All `.py` files | Added `from __future__ import annotations` |

### 3. pyproject.toml + UV

- Created `pyproject.toml` with `[project]`, `[dependency-groups]`, `[tool.ruff]`, `[tool.ty]`
- Updated `Pulumi.yaml`: `toolchain: uv` (replaces `virtualenv: venv`)
- Deleted `requirements.txt`
- Ran `uv lock` + `uv sync --group dev` — 33 packages installed
- Python 3.12.12 via CPython

### 4. Ruff (v0.15.7)

Config:
- `target-version = "py312"`, `line-length = 120`
- Rules: E, W, F, I, UP, B, SIM, RUF

Results:
- 7 issues auto-fixed (unused imports, import sorting)
- 2 unused variable assignments fixed manually (`kgateway`, `metrics_prometheus`)
- **All checks passed**
- 5 files reformatted

### 5. ty (v0.0.24)

Config:
- `python-version = "3.12"`
- `call-non-callable = "warn"` (pulumi-kubernetes SDK false positive)

Results:
- 1 warning: `call-non-callable` on `k8s.core.v1.ServiceAccount()` — false positive from pulumi-kubernetes dual module/class export pattern
- 0 errors

---

## Validation

```
$ pulumi preview --stack dev
Resources:
    + 369 to create
Outputs:
    api_url                  : "http://api.openchoreo.localhost:8080"
    argo_workflows_url       : "http://localhost:10081"
    backstage_url            : "http://openchoreo.localhost:8080"
    data_plane_gateway       : "http://openchoreo.localhost:19080"
    observer_url             : "http://observer.openchoreo.localhost:11080"
    opensearch_dashboards_url: "http://localhost:11081"
    thunder_url              : "http://thunder.openchoreo.localhost:8080"
```

---

## Commands

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check

# Preview
PULUMI_CONFIG_PASSPHRASE="openchoreo" pulumi preview --stack dev

# Deploy
PULUMI_CONFIG_PASSPHRASE="openchoreo" pulumi up --stack dev
```
