# OpenChoreo Integration Test Plan

Comprehensive test plan for validating all services deployed via Pulumi/Helm in the Kubernetes cluster, accessible from the local network.

## Test Environment

- **Platform**: Talos bare-metal cluster
- **Domain**: `openchoreo.local`
- **TLS**: Enabled (self-signed CA)
- **Access Method**: Cilium L2 announcements + Gateway API (or port-forwarding fallback)

---

## Systems Under Test

### 1. Infrastructure Layer

| System | Namespace | Access Method | SDK/Library |
|--------|-----------|---------------|-------------|
| Cilium | `kube-system` | Gateway/NodePort | `cilium` Python SDK, `requests` |
| cert-manager | `cert-manager` | K8s API | `kubernetes` Python client |
| External Secrets Operator | `external-secrets` | K8s API | `kubernetes` Python client |
| OpenBao (Vault) | `openbao` | HTTP API | `hvac` Python SDK |
| Gateway API | `openchoreo-control-plane` | HTTP/HTTPS | `requests`, `kubernetes` |

### 2. Control Plane

| System | Namespace | Access Method | SDK/Library |
|--------|-----------|---------------|-------------|
| Thunder (IdP) | `thunder` | HTTPS Gateway | `requests`, `authlib` |
| Backstage | `openchoreo-control-plane` | HTTPS Gateway | `requests` |
| OpenChoreo API | `openchoreo-control-plane` | HTTPS Gateway | `requests` |

### 3. Data Plane

| System | Namespace | Access Method | SDK/Library |
|--------|-----------|---------------|-------------|
| Data Plane Gateway | `openchoreo-data-plane` | HTTP/HTTPS | `requests` |

### 4. Workflow Plane

| System | Namespace | Access Method | SDK/Library |
|--------|-----------|---------------|-------------|
| Argo Workflows | `openchoreo-workflow-plane` | HTTP API | `argo-workflows` Python SDK |
| Docker Registry | `openchoreo-workflow-plane` | HTTP API | `requests`, Docker Registry API v2 |

### 5. Observability Plane

| System | Namespace | Access Method | SDK/Library |
|--------|-----------|---------------|-------------|
| OpenSearch | `openchoreo-observability-plane` | HTTPS | `opensearch-py` SDK |
| OpenSearch Dashboards | `openchoreo-observability-plane` | HTTPS | `requests` |
| Prometheus | `openchoreo-observability-plane` | HTTP | `prometheus-api-client` |
| Observer | `openchoreo-observability-plane` | HTTPS Gateway | `requests` |

### 6. GitOps

| System | Namespace | Access Method | SDK/Library |
|--------|-----------|---------------|-------------|
| Flux CD | `flux-system` | K8s API | `kubernetes` Python client |

---

## Test Categories

### Category A: Connectivity & Health Checks
Basic reachability and health endpoint validation.

### Category B: Authentication & Authorization
OAuth2/OIDC flows, token validation, RBAC.

### Category C: Functional API Tests
Core business logic and API operations.

### Category D: Data Flow Tests
End-to-end data pipelines (logs, traces, metrics).

### Category E: Integration Tests
Cross-service communication and workflows.

---

## Detailed Test Specifications

### 1. Cilium CNI & Gateway

**Namespace**: `kube-system`

#### Test 1.1: Cilium Agent Health
```python
# Method: Cilium CLI or API
# Library: subprocess (cilium CLI) or requests
```
- **What**: Verify all Cilium agents are running and healthy
- **How**: Query Cilium status via `cilium status` or Hubble API
- **Expected**: All agents report `OK`, no degraded components

#### Test 1.2: Cilium L2 Announcements
```python
# Method: Check CiliumLoadBalancerIPPool and L2AnnouncementPolicy
# Library: kubernetes Python client
```
- **What**: Verify L2 IP pool is configured and announcing
- **How**: Check `CiliumLoadBalancerIPPool` and `CiliumL2AnnouncementPolicy` CRs
- **Expected**: Pool has available IPs, policy is active

#### Test 1.3: Gateway API Controller
```python
# Method: Check GatewayClass and Gateway resources
# Library: kubernetes Python client
```
- **What**: Verify Cilium Gateway API controller is functioning
- **How**: Check `GatewayClass` status, verify `Gateway` resources are programmed
- **Expected**: GatewayClass accepted, Gateways have assigned addresses

#### Test 1.4: Hubble Observability
```python
# Method: Hubble Relay API
# Library: requests (gRPC or REST)
```
- **What**: Verify Hubble is collecting network flows
- **How**: Query Hubble Relay for recent flows
- **Expected**: Flows are being recorded, no errors

---

### 2. cert-manager

**Namespace**: `cert-manager`

#### Test 2.1: Controller Health
```python
# Method: Deployment readiness + webhook test
# Library: kubernetes Python client
```
- **What**: Verify cert-manager controller is operational
- **How**: Check deployment status, verify webhook responds
- **Expected**: All replicas ready, webhook healthy

#### Test 2.2: ClusterIssuer Status
```python
# Method: Check ClusterIssuer conditions
# Library: kubernetes Python client
```
- **What**: Verify `openchoreo-ca` ClusterIssuer is ready
- **How**: Query ClusterIssuer status conditions
- **Expected**: `Ready=True` condition

#### Test 2.3: Certificate Issuance
```python
# Method: Check Certificate resources
# Library: kubernetes Python client
```
- **What**: Verify TLS certificates are issued for all planes
- **How**: Check `cp-gateway-tls`, `dp-gateway-tls`, `op-gateway-tls` certificates
- **Expected**: All certificates have `Ready=True`, secrets exist

---

### 3. External Secrets Operator

**Namespace**: `external-secrets`

#### Test 3.1: Operator Health
```python
# Method: Deployment readiness
# Library: kubernetes Python client
```
- **What**: Verify ESO controllers are running
- **How**: Check `external-secrets`, `external-secrets-webhook`, `external-secrets-cert-controller`
- **Expected**: All deployments ready

#### Test 3.2: ClusterSecretStore Status
```python
# Method: Check ClusterSecretStore conditions
# Library: kubernetes Python client
```
- **What**: Verify `default` ClusterSecretStore connects to OpenBao
- **How**: Query ClusterSecretStore status
- **Expected**: `Ready=True`, provider connection successful

#### Test 3.3: ExternalSecret Sync
```python
# Method: Check ExternalSecret resources
# Library: kubernetes Python client
```
- **What**: Verify secrets are syncing from OpenBao
- **How**: Check `backstage-secrets`, `opensearch-admin-credentials` ExternalSecrets
- **Expected**: `SecretSynced=True`, target secrets exist with expected keys

---

### 4. OpenBao (Vault)

**Namespace**: `openbao`

#### Test 4.1: Vault Health
```python
# Method: Vault health API
# Library: hvac (HashiCorp Vault Python client)
```
- **What**: Verify OpenBao is initialized, unsealed, and active
- **How**: `GET /v1/sys/health`
- **Expected**: `initialized=true`, `sealed=false`, `standby=false`

#### Test 4.2: Kubernetes Auth
```python
# Method: Vault auth API
# Library: hvac
```
- **What**: Verify Kubernetes auth method is configured
- **How**: List auth methods, check kubernetes mount
- **Expected**: `kubernetes/` auth method exists and enabled

#### Test 4.3: Secret Read/Write
```python
# Method: Vault KV API
# Library: hvac
```
- **What**: Verify secrets can be read from KV store
- **How**: Read `secret/data/backstage-backend-secret`
- **Expected**: Secret exists with expected structure

#### Test 4.4: Policy Validation
```python
# Method: Vault policy API
# Library: hvac
```
- **What**: Verify OpenChoreo policies are configured
- **How**: List policies, check `openchoreo-secret-writer-role`
- **Expected**: Policy exists with correct capabilities

---

### 5. Thunder (Identity Provider)

**Namespace**: `thunder`

#### Test 5.1: OIDC Discovery
```python
# Method: OIDC well-known endpoint
# Library: requests
```
- **What**: Verify OIDC discovery endpoint is accessible
- **How**: `GET https://thunder.openchoreo.local:8443/.well-known/openid-configuration`
- **Expected**: Valid OIDC configuration JSON with issuer, endpoints

#### Test 5.2: Token Endpoint
```python
# Method: OAuth2 client credentials flow
# Library: authlib or requests
```
- **What**: Verify token issuance works
- **How**: POST to `/oauth2/token` with client credentials
- **Expected**: Valid JWT access token returned

#### Test 5.3: JWKS Endpoint
```python
# Method: JWKS endpoint
# Library: requests, PyJWT
```
- **What**: Verify JWKS endpoint returns valid keys
- **How**: `GET /oauth2/jwks`
- **Expected**: Valid JWKS with RSA keys for token verification

#### Test 5.4: Token Validation
```python
# Method: Token introspection or JWT decode
# Library: PyJWT, cryptography
```
- **What**: Verify issued tokens are valid and contain expected claims
- **How**: Decode JWT, verify signature against JWKS
- **Expected**: Valid signature, correct issuer, expected claims present

---

### 6. Backstage

**Namespace**: `openchoreo-control-plane`

#### Test 6.1: Health Endpoint
```python
# Method: Backstage health API
# Library: requests
```
- **What**: Verify Backstage backend is healthy
- **How**: `GET https://openchoreo.local:8443/healthcheck`
- **Expected**: HTTP 200, healthy status

#### Test 6.2: Catalog API
```python
# Method: Backstage Catalog API
# Library: requests
```
- **What**: Verify catalog service is operational
- **How**: `GET /api/catalog/entities` (with auth)
- **Expected**: HTTP 200, valid entity list (may be empty)

#### Test 6.3: Auth Integration
```python
# Method: Backstage auth flow
# Library: requests
```
- **What**: Verify Thunder OAuth integration works
- **How**: Initiate auth flow, verify redirect to Thunder
- **Expected**: Proper OAuth redirect, session creation

#### Test 6.4: Software Templates
```python
# Method: Scaffolder API
# Library: requests
```
- **What**: Verify scaffolder service is available
- **How**: `GET /api/scaffolder/v2/templates`
- **Expected**: HTTP 200, template list

---

### 7. OpenChoreo API

**Namespace**: `openchoreo-control-plane`

#### Test 7.1: API Health
```python
# Method: Health endpoint
# Library: requests
```
- **What**: Verify OpenChoreo API is healthy
- **How**: `GET https://api.openchoreo.local:8443/health`
- **Expected**: HTTP 200

#### Test 7.2: Organization API
```python
# Method: REST API
# Library: requests
```
- **What**: Verify organization management works
- **How**: `GET /api/v1/organizations` (with auth token)
- **Expected**: HTTP 200, organization list

#### Test 7.3: Project API
```python
# Method: REST API
# Library: requests
```
- **What**: Verify project management works
- **How**: `GET /api/v1/projects` (with auth token)
- **Expected**: HTTP 200, project list

#### Test 7.4: Component API
```python
# Method: REST API
# Library: requests
```
- **What**: Verify component management works
- **How**: `GET /api/v1/components` (with auth token)
- **Expected**: HTTP 200, component list

---

### 8. Data Plane Gateway

**Namespace**: `openchoreo-data-plane`

#### Test 8.1: Gateway Health
```python
# Method: Gateway resource status
# Library: kubernetes Python client
```
- **What**: Verify Gateway is programmed and has address
- **How**: Check `gateway-default` Gateway status
- **Expected**: `Programmed=True`, address assigned

#### Test 8.2: HTTPRoute Status
```python
# Method: HTTPRoute resource status
# Library: kubernetes Python client
```
- **What**: Verify HTTPRoutes are accepted
- **How**: Check HTTPRoute conditions
- **Expected**: `Accepted=True`, `ResolvedRefs=True`

#### Test 8.3: HTTP Connectivity
```python
# Method: HTTP request through gateway
# Library: requests
```
- **What**: Verify HTTP traffic flows through gateway
- **How**: `GET http://openchoreo.local:19080/`
- **Expected**: Response from backend (may be 404 if no routes)

#### Test 8.4: HTTPS Connectivity
```python
# Method: HTTPS request through gateway
# Library: requests
```
- **What**: Verify HTTPS traffic with TLS termination
- **How**: `GET https://openchoreo.local:19443/` (with CA cert)
- **Expected**: Valid TLS handshake, response from backend

---

### 9. Argo Workflows

**Namespace**: `openchoreo-workflow-plane`

#### Test 9.1: Server Health
```python
# Method: Argo Workflows API
# Library: argo-workflows Python SDK or requests
```
- **What**: Verify Argo Workflows server is healthy
- **How**: `GET /api/v1/info` or health endpoint
- **Expected**: HTTP 200, version info

#### Test 9.2: List Workflows
```python
# Method: Argo Workflows API
# Library: argo-workflows SDK
```
- **What**: Verify workflow listing works
- **How**: `GET /api/v1/workflows/{namespace}`
- **Expected**: HTTP 200, workflow list (may be empty)

#### Test 9.3: ClusterWorkflowTemplates
```python
# Method: Argo Workflows API
# Library: argo-workflows SDK
```
- **What**: Verify ClusterWorkflowTemplates are installed
- **How**: `GET /api/v1/cluster-workflow-templates`
- **Expected**: Templates exist (checkout-source, publish-image, etc.)

#### Test 9.4: Submit Test Workflow
```python
# Method: Argo Workflows API
# Library: argo-workflows SDK
```
- **What**: Verify workflow submission and execution
- **How**: Submit a simple echo workflow, wait for completion
- **Expected**: Workflow completes successfully

---

### 10. Docker Registry

**Namespace**: `openchoreo-workflow-plane`

#### Test 10.1: Registry Health
```python
# Method: Docker Registry API v2
# Library: requests
```
- **What**: Verify registry is accessible
- **How**: `GET /v2/` (via port-forward or internal)
- **Expected**: HTTP 200, `{}`

#### Test 10.2: Catalog API
```python
# Method: Docker Registry API v2
# Library: requests
```
- **What**: Verify catalog listing works
- **How**: `GET /v2/_catalog`
- **Expected**: HTTP 200, repository list

#### Test 10.3: Push/Pull Test
```python
# Method: Docker Registry API v2
# Library: requests or docker SDK
```
- **What**: Verify image push and pull works
- **How**: Push a small test image, then pull manifest
- **Expected**: Push succeeds, manifest retrievable

---

### 11. OpenSearch

**Namespace**: `openchoreo-observability-plane`

#### Test 11.1: Cluster Health
```python
# Method: OpenSearch Cluster API
# Library: opensearch-py SDK
```
- **What**: Verify OpenSearch cluster is healthy
- **How**: `GET /_cluster/health`
- **Expected**: `status: green` or `yellow`, all nodes present

#### Test 11.2: Index Management
```python
# Method: OpenSearch Index API
# Library: opensearch-py SDK
```
- **What**: Verify indices are created
- **How**: `GET /_cat/indices`
- **Expected**: Log and trace indices exist

#### Test 11.3: Document Ingestion
```python
# Method: OpenSearch Document API
# Library: opensearch-py SDK
```
- **What**: Verify documents can be indexed
- **How**: Index a test document, then retrieve it
- **Expected**: Document indexed and retrievable

#### Test 11.4: Search Functionality
```python
# Method: OpenSearch Search API
# Library: opensearch-py SDK
```
- **What**: Verify search works
- **How**: Execute a simple match_all query
- **Expected**: Search returns results (if data exists)

---

### 12. OpenSearch Dashboards

**Namespace**: `openchoreo-observability-plane`

#### Test 12.1: Dashboard Health
```python
# Method: Dashboards API
# Library: requests
```
- **What**: Verify Dashboards is accessible
- **How**: `GET /api/status`
- **Expected**: HTTP 200, status JSON

#### Test 12.2: OpenSearch Connection
```python
# Method: Dashboards API
# Library: requests
```
- **What**: Verify Dashboards connects to OpenSearch
- **How**: Check status for OpenSearch connection
- **Expected**: Connection status healthy

---

### 13. Prometheus

**Namespace**: `openchoreo-observability-plane`

#### Test 13.1: Prometheus Health
```python
# Method: Prometheus API
# Library: prometheus-api-client or requests
```
- **What**: Verify Prometheus is healthy
- **How**: `GET /-/healthy`
- **Expected**: HTTP 200, "Prometheus is Healthy"

#### Test 13.2: Targets Status
```python
# Method: Prometheus API
# Library: prometheus-api-client
```
- **What**: Verify scrape targets are up
- **How**: `GET /api/v1/targets`
- **Expected**: Targets present, most in `up` state

#### Test 13.3: Query API
```python
# Method: Prometheus Query API
# Library: prometheus-api-client
```
- **What**: Verify PromQL queries work
- **How**: `GET /api/v1/query?query=up`
- **Expected**: HTTP 200, query results

#### Test 13.4: Metrics Ingestion
```python
# Method: Prometheus Query API
# Library: prometheus-api-client
```
- **What**: Verify metrics are being collected
- **How**: Query for Kubernetes metrics (e.g., `kube_pod_info`)
- **Expected**: Metrics present with recent timestamps

---

### 14. Observer

**Namespace**: `openchoreo-observability-plane`

#### Test 14.1: Observer Health
```python
# Method: Health endpoint
# Library: requests
```
- **What**: Verify Observer service is healthy
- **How**: `GET https://observer.openchoreo.local:11085/health`
- **Expected**: HTTP 200

#### Test 14.2: Logs API
```python
# Method: Observer Logs API
# Library: requests
```
- **What**: Verify log querying works
- **How**: Query logs for a known namespace
- **Expected**: HTTP 200, log entries (if available)

#### Test 14.3: Traces API
```python
# Method: Observer Traces API
# Library: requests
```
- **What**: Verify trace querying works
- **How**: Query traces for a time range
- **Expected**: HTTP 200, trace data (if available)

#### Test 14.4: Metrics API
```python
# Method: Observer Metrics API
# Library: requests
```
- **What**: Verify metrics querying works
- **How**: Query metrics for a known service
- **Expected**: HTTP 200, metric data

---

### 15. Flux CD

**Namespace**: `flux-system`

#### Test 15.1: Controller Health
```python
# Method: Deployment readiness
# Library: kubernetes Python client
```
- **What**: Verify Flux controllers are running
- **How**: Check `source-controller`, `kustomize-controller`, `helm-controller`
- **Expected**: All deployments ready

#### Test 15.2: GitRepository Status
```python
# Method: GitRepository resource status
# Library: kubernetes Python client
```
- **What**: Verify GitRepository is syncing
- **How**: Check `sample-gitops` GitRepository conditions
- **Expected**: `Ready=True`, last sync recent

#### Test 15.3: Kustomization Status
```python
# Method: Kustomization resource status
# Library: kubernetes Python client
```
- **What**: Verify Kustomizations are reconciling
- **How**: Check all Kustomization resources
- **Expected**: `Ready=True` for all, no errors

#### Test 15.4: Reconciliation Test
```python
# Method: Force reconciliation
# Library: kubernetes Python client
```
- **What**: Verify on-demand reconciliation works
- **How**: Annotate GitRepository to trigger sync
- **Expected**: Reconciliation completes successfully

---

## Test Implementation Structure

```
tests/
├── conftest.py                    # Pytest fixtures (k8s client, config, auth)
├── utils/
│   ├── __init__.py
│   ├── k8s_helpers.py            # Kubernetes API helpers
│   ├── http_helpers.py           # HTTP request helpers with TLS
│   ├── auth_helpers.py           # OAuth2 token acquisition
│   └── port_forward.py           # Port-forwarding context manager
├── infrastructure/
│   ├── test_cilium.py
│   ├── test_cert_manager.py
│   ├── test_external_secrets.py
│   └── test_openbao.py
├── control_plane/
│   ├── test_thunder.py
│   ├── test_backstage.py
│   └── test_openchoreo_api.py
├── data_plane/
│   └── test_gateway.py
├── workflow_plane/
│   ├── test_argo_workflows.py
│   └── test_docker_registry.py
├── observability_plane/
│   ├── test_opensearch.py
│   ├── test_opensearch_dashboards.py
│   ├── test_prometheus.py
│   └── test_observer.py
└── gitops/
    └── test_flux.py
```

---

## Python Dependencies

```toml
[project]
dependencies = [
    # Kubernetes
    "kubernetes>=29.0.0",
    
    # HTTP/REST
    "requests>=2.31.0",
    "httpx>=0.27.0",  # async support
    
    # Authentication
    "authlib>=1.3.0",
    "PyJWT>=2.8.0",
    "cryptography>=42.0.0",
    
    # Vault/OpenBao
    "hvac>=2.1.0",
    
    # OpenSearch
    "opensearch-py>=2.4.0",
    
    # Prometheus
    "prometheus-api-client>=0.5.4",
    
    # Argo Workflows
    "argo-workflows>=6.5.0",
    
    # Testing
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-timeout>=2.3.0",
    "pytest-html>=4.1.0",
]
```

---

## Access Methods

### Primary: Gateway API (Cilium L2)
Services exposed via Cilium Gateway with L2 announcements:
- Control Plane: `https://openchoreo.local:8443`
- Data Plane: `https://openchoreo.local:19443`
- Observability: `https://observer.openchoreo.local:11085`

### Fallback: Port Forwarding
For services not exposed via Gateway:
```python
# Example port-forward context manager
with port_forward("openbao", "openbao-0", 8200) as local_port:
    client = hvac.Client(url=f"http://localhost:{local_port}")
```

### Internal: Kubernetes API
For CRD status checks and resource validation:
```python
from kubernetes import client, config
config.load_kube_config(context="admin@openchoreo")
```

---

## Test Execution

### Run All Tests
```bash
pytest tests/ -v --html=report.html
```

### Run by Category
```bash
# Infrastructure only
pytest tests/infrastructure/ -v

# Control plane only
pytest tests/control_plane/ -v

# With markers
pytest -m "smoke" -v
pytest -m "integration" -v
```

### Environment Variables
```bash
export KUBECONFIG=~/.kube/config
export KUBE_CONTEXT=admin@openchoreo
export DOMAIN_BASE=openchoreo.local
export TLS_ENABLED=true
export CA_CERT_PATH=/path/to/ca.crt
export OPENBAO_TOKEN=root
export OPENSEARCH_USER=admin
export OPENSEARCH_PASS=ThisIsTheOpenSearchPassword1
```

---

## Success Criteria

| Category | Pass Threshold |
|----------|---------------|
| Infrastructure | 100% |
| Control Plane | 100% |
| Data Plane | 100% |
| Workflow Plane | 95% |
| Observability | 90% |
| GitOps | 100% |

---

## Notes

1. **TLS Verification**: Tests should use the self-signed CA certificate for HTTPS requests
2. **Authentication**: Most API tests require OAuth2 tokens from Thunder
3. **Timeouts**: Use generous timeouts (60-120s) for first-time operations
4. **Idempotency**: Tests should be idempotent and not leave state
5. **Parallelization**: Infrastructure tests can run in parallel; integration tests should be sequential
