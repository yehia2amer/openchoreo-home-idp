# OpenChoreo Home IDP

Pulumi Python IaC project for deploying OpenChoreo (Internal Developer Platform) to Kubernetes clusters.

## Project Overview

| Aspect | Value |
|--------|-------|
| **Type** | Infrastructure as Code (Pulumi Python) |
| **Runtime** | Python 3.12+ with uv package manager |
| **Framework** | Pulumi with pulumi-kubernetes provider |
| **Purpose** | Deploy OpenChoreo control, data, workflow, and observability planes |

## Directory Structure

```
openchoreo-home-idp/
├── pulumi/                      # Main Pulumi IaC project (see pulumi/AGENTS.md)
│   ├── components/              # ComponentResource classes per plane
│   ├── values/                  # Dynamic Helm values generators
│   ├── helpers/                 # Shared utilities
│   ├── platforms/               # Platform adapters (k3d, talos, rancher)
│   ├── scripts/                 # Bootstrap CLI scripts
│   ├── talos-cluster/           # Nested Pulumi: Talos VM cluster
│   └── talos-cluster-baremetal/ # Nested Pulumi: bare-metal Talos (see AGENTS.md)
├── docs/                        # Reference docs from upstream openchoreo
└── talos_get_all_details.py     # Standalone Talos diagnostic utility
```

## Entry Points

| File | Purpose |
|------|---------|
| `pulumi/__main__.py` | Main orchestration - deploys all planes sequentially |
| `pulumi/scripts/bootstrap.py` | CLI dispatcher for platform-specific bootstrap |
| `pulumi/talos-cluster/__main__.py` | Talos VM cluster (libvirt/QEMU) |
| `pulumi/talos-cluster-baremetal/__main__.py` | Bare-metal Talos with Cilium, Longhorn |
| `talos_get_all_details.py` | Dumps Talos cluster resources to files |

## Quick Commands

```bash
# Navigate to main Pulumi project
cd pulumi

# Deploy to dev stack (k3d)
pulumi up -s dev

# Deploy to Talos bare-metal
pulumi up -s talos-baremetal

# Bootstrap a platform
python scripts/bootstrap.py --platform talos
```

## Stack Configuration

Stacks define platform-specific settings in `Pulumi.<stack>.yaml`:

| Stack | Platform | Description |
|-------|----------|-------------|
| `dev` | k3d | Local k3d development cluster |
| `rancher-desktop` | Rancher Desktop | Local Rancher Desktop cluster |
| `talos` | Talos VM | Talos on libvirt/QEMU VMs |
| `talos-baremetal` | Talos Bare-metal | Physical Talos nodes |

## Key Configuration Options

```yaml
# Pulumi.<stack>.yaml
config:
  openchoreo:kubeconfig_context: "talos-admin@talos"
  openchoreo:domain_base: "openchoreo.localhost"
  openchoreo:tls_enabled: true
  openchoreo:enable_observability: true
  openchoreo:enable_flux: false
  openchoreo:platform: "talos"  # k3d | rancher-desktop | talos | talos-baremetal
```

## Conventions

### Python Style
- **Line length**: 120 chars
- **Python version**: >=3.12
- **Linter**: Ruff with rules: E, W, F, I, UP, B, SIM, RUF
- **Type checker**: ty with `python-version = "3.12"`
- **Package manager**: uv (NOT pip)

### Code Organization
- One `ComponentResource` per plane in `components/`
- Corresponding Helm values generator in `values/`
- Platform-specific logic in `platforms/` (strategy pattern via `resolver.py`)

### Testing
- Framework: pytest >=8.0 with pytest-timeout
- Markers: `@pytest.mark.e2e`, `@pytest.mark.slow`
- Location: `pulumi/tests/`, `pulumi/talos-cluster-baremetal/tests/`

## Anti-Patterns and Warnings

### NEVER
- Hardcode secrets in code - always use Pulumi config or environment variables

### DO NOT EDIT (Auto-Generated)
- Files in `docs/reference-project-docs/openchoreo/` are upstream reference code

### Known Issues
- `talos_get_all_details.py` should be moved to `pulumi/scripts/`
- Some TODO items in reference docs for incomplete implementations

## Outputs After Deployment

```bash
# View all outputs
pulumi stack output

# View secrets
pulumi stack output --show-secrets

# Key URLs exported
backstage_url       # Backstage UI
api_url             # OpenChoreo API
thunder_url         # Thunder OAuth
observer_url        # Observability dashboard
data_plane_gateway_http   # Data plane HTTP gateway
data_plane_gateway_https  # Data plane HTTPS gateway
```

## Namespaces

| Namespace | Purpose |
|-----------|---------|
| `openchoreo-control-plane` | Control plane services (Backstage, API, controllers) |
| `openchoreo-data-plane` | Data plane gateway and services |
| `openchoreo-workflow-plane` | Argo Workflows and build pipelines |
| `openchoreo-observability-plane` | OpenSearch, Prometheus, dashboards |
| `openbao` | Secrets management (OpenBao vault) |
| `cert-manager` | TLS certificate management |
| `external-secrets` | External secrets operator |
| `thunder` | OAuth/OIDC authentication |

## Related Documentation

- [OpenChoreo Official Docs](https://github.com/openchoreo/openchoreo)
- Reference implementation in `docs/reference-project-docs/openchoreo/`
