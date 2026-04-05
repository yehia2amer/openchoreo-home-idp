# Pulumi IaC Project

Main Pulumi Python project for deploying OpenChoreo to Kubernetes.

## Architecture

```
pulumi/
├── __main__.py          # Entry point - orchestrates all planes
├── config.py            # Configuration loader and constants
├── components/          # ComponentResource classes (one per plane)
├── values/              # Helm values generators (1:1 with components)
├── helpers/             # Shared utilities
├── platforms/           # Platform adapters (strategy pattern)
├── scripts/             # Bootstrap and utility scripts
├── templates/           # YAML/config templates
├── tests/               # pytest test suite
├── policy/              # Pulumi CrossGuard policies
├── talos-cluster/       # Nested Pulumi: Talos VM cluster
└── talos-cluster-baremetal/  # Nested Pulumi: bare-metal Talos
```

## Module Responsibilities

### components/

Each file is a `ComponentResource` deploying one OpenChoreo plane:

| File | Purpose |
|------|---------|
| `control_plane.py` | Backstage, OpenChoreo API, controllers |
| `data_plane.py` | Gateway API, data plane services |
| `workflow_plane.py` | Argo Workflows, Docker registry |
| `observability_plane.py` | OpenSearch, Prometheus, dashboards |
| `prerequisites.py` | Namespaces, cert-manager, external-secrets, OpenBao, Thunder |
| `tls_setup.py` | Self-signed CA chain for bare-metal TLS |
| `cilium.py` | Cilium CNI and Gateway API controller |
| `flux_gitops.py` | Flux CD for GitOps deployments |
| `link_planes.py` | Links data/workflow/observability planes to control plane |
| `integration_tests.py` | Post-deployment validation |

### values/

Dynamic Helm values generators (called by corresponding component):

| File | Generates values for |
|------|---------------------|
| `control_plane.py` | openchoreo-control-plane chart |
| `data_plane.py` | openchoreo-data-plane chart |
| `workflow_plane.py` | openchoreo-workflow-plane chart |
| `observability_plane.py` | openchoreo-observability-plane chart |
| `openbao.py` | OpenBao Helm chart |
| `registry.py` | Docker registry chart |

### platforms/

Platform adapters using strategy pattern:

| File | Purpose |
|------|---------|
| `types.py` | `PlatformProfile` dataclass |
| `resolver.py` | Resolves platform from Pulumi config |
| `k3d.py` | k3d local cluster profile |
| `rancher_desktop.py` | Rancher Desktop profile |
| `talos.py` | Talos VM cluster profile |
| `talos_baremetal.py` | Bare-metal Talos profile |

### helpers/

Shared utilities:

| File | Purpose |
|------|---------|
| `k8s_ops.py` | Kubernetes operations (wait, apply, delete) |
| `wait.py` | Resource readiness polling |
| `dynamic_providers.py` | Pulumi dynamic providers for custom resources |
| `register_plane.py` | Registers planes with OpenChoreo API |
| `copy_ca.py` | Copies CA certificates between namespaces |

## Deployment Sequence

`__main__.py` deploys planes in this order:

1. **Cilium** (optional) - CNI + Gateway API controller
2. **Prerequisites** - Namespaces, cert-manager, ESO, OpenBao, Thunder
3. **TLS Setup** (optional) - Self-signed CA chain
4. **Control Plane** - Backstage, API, controllers
5. **Data Plane** - Gateway, data services
6. **Workflow Plane** - Argo Workflows, registry
7. **Observability Plane** (optional) - OpenSearch, Prometheus
8. **Link Planes** - Connect planes to control plane
9. **Flux GitOps** (optional) - GitOps deployment
10. **Integration Tests** - Validation

## Configuration

All config flows through `config.py`:

```python
from config import load_config
cfg = load_config()  # Returns OpenChoreoConfig dataclass
```

Key config sources:
- `Pulumi.<stack>.yaml` - Stack-specific settings
- Environment variables - Secrets
- `platforms/` - Platform-specific defaults

## Adding a New Platform

1. Create `platforms/<platform_name>.py`:
   ```python
   from .types import PlatformProfile

   def create_profile() -> PlatformProfile:
       return PlatformProfile(
           name="my-platform",
           cni_mode="cilium",
           gateway_mode="cilium",
           # ... other settings
       )
   ```

2. Register in `platforms/resolver.py`

3. Create `Pulumi.<platform>.yaml` stack config

## Adding a New Plane

1. Create `components/<plane>_plane.py` with `ComponentResource`
2. Create `values/<plane>_plane.py` for Helm values
3. Add to deployment sequence in `__main__.py`
4. Export outputs for URLs/credentials

## Testing

```bash
# Run all tests
uv run pytest

# Run E2E tests only
uv run pytest -m e2e

# Run with timeout
uv run pytest --timeout=120
```

Test fixtures in `tests/conftest.py` provide:
- `kubeconfig` - Path to kubeconfig file
- `kube_context` - Active Kubernetes context

## Nested Pulumi Projects

### talos-cluster/

Deploys Talos Linux VMs using libvirt/QEMU (macOS development).

```bash
cd talos-cluster
pulumi up -s dev
```

### talos-cluster-baremetal/

Deploys bare-metal Talos cluster with:
- Cilium CNI with L2 announcements
- Longhorn distributed storage
- Gateway API with Cilium

See `talos-cluster-baremetal/AGENTS.md` for details.

## Conventions

### Naming
- Components: `<Plane>Component` (e.g., `ControlPlane`)
- Values functions: `generate_<plane>_values(cfg)`
- Platform profiles: `<platform>_profile()`

### Dependencies
- Always pass `depends=[]` to ensure correct ordering
- Use `pulumi.ResourceOptions(depends_on=[...])` for Helm charts

### Secrets
- Never hardcode - use `cfg.get_secret()` or environment variables
- Mark outputs as secret: `pulumi.Output.secret(value)`
