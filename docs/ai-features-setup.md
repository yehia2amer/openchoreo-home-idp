# OpenChoreo AI Features — Setup & Access Guide

## Overview

OpenChoreo has three AI-powered capabilities:

| Feature | Status | Endpoint | Purpose |
|---------|--------|----------|---------|
| **Control Plane MCP Server** | ✅ Enabled | `https://api.openchoreo.local:8443/mcp` | Manage projects, components, builds, deployments via AI |
| **Observer MCP Server** | ✅ Enabled | `https://observer.openchoreo.local:11085/mcp` | Query logs, traces, and metrics via AI |
| **RCA Agent** | 🔧 Enable via Pulumi | `https://rca-agent.openchoreo.local:11085` | AI-powered Root Cause Analysis with auto-remediation |

## 1. MCP Servers (Already Working)

Both MCP servers are accessible from your laptop via HTTPRoute through the Cilium L2 gateways.

### Authentication

Get a token:
```bash
./scripts/get-mcp-token.sh
```

Or manually:
```bash
curl -sk -X POST https://thunder.openchoreo.local:8443/oauth2/token \
  -u "service_mcp_client:service_mcp_client_secret" \
  -d "grant_type=client_credentials" \
  -d "scope=openid"
```

### MCP Toolsets (Control Plane)

| Toolset | Tools |
|---------|-------|
| `namespace` | list_namespaces, get_namespace |
| `project` | list_projects, get_project, create_project |
| `component` | list/get/create components, bindings, workloads, releases |
| `build` | trigger_build, list_builds, build_templates, workflow_planes |
| `deployment` | deployment_pipelines, observer_urls |
| `pe` | Platform engineering tools |

### MCP Toolsets (Observer)

Logs, traces, metrics queries — integrated with OpenSearch, OpenObserve, and Prometheus.

### Configure AI Assistants

#### Claude Code / pi
The `.mcp.json` at the project root is pre-configured. You need to set the token:

```bash
# Get a fresh token (valid 24h)
export OPENCHOREO_MCP_TOKEN=$(./scripts/get-mcp-token.sh)
```

#### Cursor
Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "openchoreo": {
      "url": "https://api.openchoreo.local:8443/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

#### VS Code (GitHub Copilot)
Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "openchoreo": {
      "type": "http",
      "url": "https://api.openchoreo.local:8443/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

## 2. RCA Agent (AI Root Cause Analysis)

### Enable RCA Agent

1. **Set your LLM API key** in OpenBao:
   ```bash
   export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig
   kubectl exec -n openbao openbao-0 -- \
     bao kv put secret/rca-llm-api-key value="YOUR_ANTHROPIC_OR_OPENAI_KEY"
   ```

2. **Deploy with Pulumi** (already configured in `Pulumi.talos-baremetal.yaml`):
   ```bash
   cd pulumi
   PULUMI_CONFIG_PASSPHRASE=openchoreo-talos-baremetal pulumi up --stack talos-baremetal
   ```

3. **Update `/etc/hosts`** — add `rca-agent.openchoreo.local` to the observability gateway line:
   ```bash
   # Change this line:
   192.168.0.12  alertmanager.openchoreo.local observer.openchoreo.local opensearch.openchoreo.local prometheus.openchoreo.local openobserve.openchoreo.local
   # To:
   192.168.0.12  alertmanager.openchoreo.local rca-agent.openchoreo.local observer.openchoreo.local opensearch.openchoreo.local prometheus.openchoreo.local openobserve.openchoreo.local
   ```

### RCA Agent Configuration

| Setting | Value |
|---------|-------|
| Model | `openai:bedrock.anthropic.claude-sonnet-4-5` via PwC GenAI proxy |
| Base URL | `https://genai-sharedservice-emea.pwc.com` |
| Auto-remediation | Enabled |
| Secret | `rca-agent-secret` (ExternalSecret from OpenBao) |
| OAuth client | `openchoreo-rca-agent` |

### RCA Agent API

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1alpha1/rca-agent/analyze` | Trigger an RCA analysis |
| `POST /api/v1alpha1/rca-agent/chat` | Chat follow-up on a report |
| `GET /api/v1alpha1/rca-reports/projects/{project}` | List reports by project |
| `GET /api/v1alpha1/rca-reports/alerts/{alert_fingerprint}` | Get report by alert |

### How RCA Works

1. Receives alert via REST API
2. Runs a **ReAct loop** — queries Observer MCP for logs/traces/metrics
3. Queries Control Plane MCP for project/component context
4. Produces structured RCA report with root causes, evidence, and recommendations
5. (Optional) Remediation agent reviews and applies fixes

## 3. Network Access Map

| Service | Gateway IP | HTTP | HTTPS |
|---------|-----------|------|-------|
| Control Plane MCP | 192.168.0.10 | :8080 | :8443 |
| Observer MCP | 192.168.0.12 | :11080 | :11085 |
| RCA Agent | 192.168.0.12 | :11080 | :11085 |
| Thunder (Auth) | 192.168.0.10 | :8080 | :8443 |

## Files Changed

- `pulumi/config.py` — Added `enable_rca`, `rca_llm_model`, `rca_llm_api_key` config
- `pulumi/values/observability_plane.py` — RCA agent Helm values with LLM config
- `pulumi/values/control_plane.py` — Explicit MCP toolset configuration
- `pulumi/components/observability_plane.py` — RCA ExternalSecret + dependencies
- `pulumi/values/openbao.py` — OpenBao bootstrap for `rca-llm-api-key`
- `pulumi/Pulumi.talos-baremetal.yaml` — Enabled `enable_rca: true`
- `.mcp.json` — MCP server configuration for AI assistants
- `scripts/get-mcp-token.sh` — Token helper script
