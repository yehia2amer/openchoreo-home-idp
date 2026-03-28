# Pulumi Refactor Plan — Magic Strings, pyproject.toml, Code Quality

**Date:** 2026-03-23 14:00  
**Scope:** Refactor the Pulumi Python project for config centralization, modern Python packaging, and code quality tooling  

---

## 1. Problem Statement

### 1.1 Magic Strings Everywhere
Hardcoded URLs, namespace names, chart references, Helm registries, API versions, and kubectl commands are scattered across 10+ component files instead of being centralized in `config.py`.

**Examples found in audit:**

| Category | Magic String | File(s) |
|----------|-------------|---------|
| OCI Registry | `oci://ghcr.io/openchoreo/helm-charts/...` | prerequisites, control_plane, data_plane, workflow_plane, observability_plane |
| OCI Registry | `oci://quay.io/jetstack/charts/cert-manager` | prerequisites |
| OCI Registry | `oci://ghcr.io/external-secrets/charts/...` | prerequisites |
| OCI Registry | `oci://cr.kgateway.dev/kgateway-dev/charts/...` | prerequisites |
| OCI Registry | `oci://ghcr.io/openbao/charts/openbao` | prerequisites |
| OCI Registry | `oci://ghcr.io/asgardeo/helm-charts/thunder` | control_plane |
| HTTP Registry | `https://twuni.github.io/docker-registry.helm` | workflow_plane |
| URL | `https://github.com/kubernetes-sigs/gateway-api/releases/...` | prerequisites |
| URL | `https://github.com/fluxcd/flux2/releases/latest/download/install.yaml` | flux_gitops |
| URL | `http://thunder-service.thunder.svc.cluster.local:8090/...` | values/observability_plane |
| Namespace | `openchoreo-control-plane`, `openchoreo-data-plane`, etc. | 9 files |
| Namespace | `openbao`, `cert-manager`, `external-secrets`, `thunder`, `flux-system` | multiple |
| Chart Name | `cert-manager`, `external-secrets`, `kgateway`, `openbao`, etc. | prerequisites |
| K8s Resource | `cluster-gateway-ca`, `cluster-agent-tls`, `backstage-secrets` | helpers, components |
| K8s Resource | `opensearch-admin-credentials`, `observer-secret`, etc. | observability_plane |
| Timeout | `600s`, `900s`, `1500s`, `120s`, `300s` | all components |
| Sleep | `5`, `10`, `30` seconds | prerequisites, control_plane |

### 1.2 No pyproject.toml / UV
- Using legacy `requirements.txt` instead of `pyproject.toml`
- No `uv` lockfile for reproducible installs
- No dev dependency section for tooling

### 1.3 No Code Quality Tooling
- No linter (Ruff)
- No type checker (ty)
- No CI-ready quality gate

---

## 2. Solution Design

### 2.1 Centralize Magic Strings in `config.py`

Add to `OpenChoreoConfig` dataclass:

```python
# Helm chart OCI registries
OPENCHOREO_CHART_REPO = "oci://ghcr.io/openchoreo/helm-charts"
CERT_MANAGER_CHART_REPO = "oci://quay.io/jetstack/charts"
EXTERNAL_SECRETS_CHART_REPO = "oci://ghcr.io/external-secrets/charts"
KGATEWAY_CHART_REPO = "oci://cr.kgateway.dev/kgateway-dev/charts"
OPENBAO_CHART_REPO = "oci://ghcr.io/openbao/charts"
THUNDER_CHART_REPO = "oci://ghcr.io/asgardeo/helm-charts"
DOCKER_REGISTRY_REPO = "https://twuni.github.io/docker-registry.helm"

# Namespace names
NS_CONTROL_PLANE = "openchoreo-control-plane"
NS_DATA_PLANE = "openchoreo-data-plane"
NS_WORKFLOW_PLANE = "openchoreo-workflow-plane"
NS_OBSERVABILITY_PLANE = "openchoreo-observability-plane"
NS_OPENBAO = "openbao"
NS_CERT_MANAGER = "cert-manager"
NS_EXTERNAL_SECRETS = "external-secrets"
NS_THUNDER = "thunder"
NS_FLUX_SYSTEM = "flux-system"

# Well-known K8s resource names
SECRET_GATEWAY_CA = "cluster-gateway-ca"
SECRET_AGENT_TLS = "cluster-agent-tls"
SECRET_BACKSTAGE = "backstage-secrets"
SECRET_OPENSEARCH_ADMIN = "opensearch-admin-credentials"
SECRET_OBSERVER_OPENSEARCH = "observer-opensearch-credentials"
SECRET_OBSERVER = "observer-secret"
SA_ESO_OPENBAO = "external-secrets-openbao"
CLUSTER_SECRET_STORE_NAME = "default"

# Timeouts (seconds)
TIMEOUT_DEFAULT = 600
TIMEOUT_OPENSEARCH = 900
TIMEOUT_OBS_PLANE = 1500
TIMEOUT_WAIT = 300

# Derived URLs (add as properties or calculated in load_config)
gateway_api_crds_url: str        # from gateway_api_version
flux_install_url: str             # static
thunder_internal_base_url: str    # in-cluster thunder service URL
coredns_rewrite_url: str          # from raw_base
```

### 2.2 Replace requirements.txt with pyproject.toml + uv

```toml
[project]
name = "openchoreo-k3d"
version = "1.0.0"
description = "OpenChoreo v1.0 on k3d — Pulumi Python"
requires-python = ">=3.12"
dependencies = [
    "pulumi>=3.0.0,<4.0.0",
    "pulumi-kubernetes>=4.0.0,<5.0.0",
    "pulumi-command>=1.0.0,<2.0.0",
    "pyyaml>=6.0",
]

[dependency-groups]
dev = [
    "ruff>=0.11",
    "ty>=0.0.1a7",
]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "RUF"]

[tool.ty]
python-version = "3.12"
```

- Delete `requirements.txt`
- Update `Pulumi.yaml` to use `uv` toolchain (`toolchain: uv`)
- Generate `uv.lock` via `uv lock`
- Update bootstrap script for `uv sync` instead of `pip install`

### 2.3 Add Ruff and ty Quality Checks

- `uv run ruff check .` — lint all files
- `uv run ruff format --check .` — format check
- `uv run ty check` — type check
- Fix all issues found

---

## 3. Implementation Steps

| # | Task | Files Changed |
|---|------|---------------|
| 1 | Add constants + derived URLs to `config.py` | config.py |
| 2 | Refactor all `components/*.py` to use config constants | 7 component files |
| 3 | Refactor `helpers/*.py` to accept constants from caller | 3 helper files |
| 4 | Refactor `values/*.py` to use constants where applicable | 2 value files |
| 5 | Create `pyproject.toml`, delete `requirements.txt` | pyproject.toml, requirements.txt |
| 6 | Update `Pulumi.yaml` for uv | Pulumi.yaml |
| 7 | Restore `Pulumi.dev.yaml` with full non-secret config | Pulumi.dev.yaml |
| 8 | Run `uv lock` + recreate venv | uv.lock, venv/ |
| 9 | Run `ruff check --fix .` + `ruff format .` | all .py files |
| 10 | Run `ty check` and fix type issues | affected .py files |
| 11 | Run `pulumi preview` to validate | — |

---

## 4. File Tree After Refactor

```
pulumi/
├── Pulumi.yaml
├── Pulumi.dev.yaml
├── pyproject.toml              # NEW (replaces requirements.txt)
├── uv.lock                     # NEW (generated)
├── __main__.py
├── config.py                   # MODIFIED (constants + derived URLs)
├── components/
│   ├── __init__.py
│   ├── prerequisites.py        # MODIFIED (use config constants)
│   ├── control_plane.py        # MODIFIED
│   ├── data_plane.py           # MODIFIED
│   ├── workflow_plane.py       # MODIFIED
│   ├── observability_plane.py  # MODIFIED
│   ├── flux_gitops.py          # MODIFIED
│   └── link_planes.py          # MODIFIED
├── values/
│   ├── __init__.py
│   ├── openbao.py
│   ├── control_plane.py
│   ├── data_plane.py
│   ├── workflow_plane.py
│   ├── registry.py
│   └── observability_plane.py  # MODIFIED (thunder internal URL)
├── helpers/
│   ├── __init__.py
│   ├── copy_ca.py              # MODIFIED (accept source ns + secret name)
│   ├── register_plane.py       # MODIFIED (accept secret name as param)
│   └── wait.py
└── scripts/
    └── bootstrap_k3d.py        # MODIFIED (uv sync)
```
