# GitHub Actions Integration for OpenChoreo

> **Scope**: Enabling GitHub Actions build visibility in OpenChoreo's Backstage portal and delivering workloads via external CI.
>
> **Audience**: Platform engineers and developers using GitHub Actions with OpenChoreo.
>
> **Related**: See [External CI Integration](../reference-project-docs/openchoreo-docs/docs/platform-engineer-guide/workflows/external-ci.mdx) for the full External CI workflow guide (authentication, Workload API, Jenkins example).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Setup Steps](#3-setup-steps)
4. [Using External CI with GitHub Actions](#4-using-external-ci-with-github-actions)
5. [Sample Workflow](#5-sample-workflow)
6. [Troubleshooting](#6-troubleshooting)
7. [Limitations](#7-limitations)
8. [What's Next](#8-whats-next)

---

## 1. Overview

This guide explains how to enable GitHub Actions build visibility in OpenChoreo's Backstage portal using the bundled `@backstage-community/plugin-github-actions` plugin.

This integration provides:

- Build history and status in the Backstage CI/CD tab
- Direct links to GitHub Actions workflow runs and logs
- Automatic build status updates

> **Note**: This integration provides *visibility* into GitHub Actions builds within Backstage. It does not orchestrate or trigger GitHub Actions workflows — those run in GitHub as usual.

---

## 2. Prerequisites

Before you begin, ensure you have:

- **OpenChoreo installed and running** — the Backstage portal must be accessible
- **GitHub credentials** — one of the following depending on your chosen auth method:
  - **GitHub App** (recommended for `auth.type: app`): `appId`, `clientId`, `clientSecret`, `webhookSecret`, and `privateKey` (PEM format)
  - **Personal Access Token** (for `auth.type: token`): a PAT with `repo` and `actions:read` scopes
- **Helm chart access** — ability to supply value overrides to the `openchoreo-control-plane` chart
- **Network connectivity** — the Backstage pod must be able to reach `api.github.com` (port 443)

---

## 3. Setup Steps

### Step 1: Enable GitHub Actions in Helm Values

Add the following to your `custom-values.yaml` (or equivalent Helm override file):

```yaml
backstage:
  externalCI:
    githubActions:
      enabled: true
      host: github.com
      apiBaseUrl: "https://api.github.com"
      auth:
        type: app   # "app" (recommended) or "token"
        app:
          appId: "<your-github-app-id>"
          clientId: "<your-github-app-client-id>"
          clientSecret: ""   # Provisioned via OpenBao
          webhookSecret: ""  # Provisioned via OpenBao
          privateKey: ""     # Provisioned via OpenBao (PEM format)
        token: ""  # Only used when auth.type is "token", provisioned via OpenBao
```

**Auth type selection:**

| Auth Type | Best For | Benefits |
|-----------|----------|----------|
| `app` (recommended) | Production environments | Higher API rate limits, fine-grained repository permissions, no personal token expiry |
| `token` | Quick setup, development | Simpler configuration, single PAT with `repo` + `actions:read` scopes |

> **Important**: Set `auth.type` to match the credentials you configure. Using `app` with only a PAT configured (or vice versa) will result in authentication failures.

### Step 2: Configure Secrets in OpenBao

The GitHub Actions integration uses four secret keys, provisioned through the PushSecret → ExternalSecret chain:

| Secret Key | Purpose | Used When |
|------------|---------|-----------|
| `github-token` | Personal Access Token | `auth.type: token` |
| `github-app-client-secret` | GitHub App OAuth client secret | `auth.type: app` |
| `github-app-webhook-secret` | GitHub App webhook secret | `auth.type: app` |
| `github-app-private-key` | GitHub App private key (PEM format) | `auth.type: app` |

These are stored under `kv/data/backstage-secrets` in OpenBao and synced to the `backstage-secrets` Kubernetes Secret via ExternalSecret.

> **Important**: Placeholder values are provisioned by default. You **must** replace them with real credentials before setting `githubActions.enabled: true`. The Backstage pod will fail to authenticate with GitHub if placeholder values remain.

### Step 3: Add Component Annotation

For each Backstage component that should display GitHub Actions builds, add the `github.com/project-slug` annotation to its `catalog-info.yaml`:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  annotations:
    github.com/project-slug: "your-org/your-repo"
spec:
  type: service
  lifecycle: production
  owner: team-platform
```

The `github.com/project-slug` annotation tells the Backstage GitHub Actions plugin which repository to fetch workflow runs from. The value must match the `owner/repo` format exactly as it appears on GitHub.

### Step 4: Upgrade and Verify

Apply the Helm values and upgrade the control plane:

```bash
helm upgrade openchoreo-control-plane ./openchoreo-control-plane \
  -f custom-values.yaml \
  -n openchoreo-system
```

After the upgrade completes:

1. Wait for the Backstage pod to restart and become ready
2. Navigate to a component that has the `github.com/project-slug` annotation
3. A **"GitHub Actions"** tab should appear on the component page
4. The tab displays workflow run history, status, and links to GitHub

---

## 4. Using External CI with GitHub Actions

Beyond build visibility, you can use GitHub Actions as an external CI system to deliver workloads to OpenChoreo. There are two approaches:

### Approach A: API-Based (Direct)

1. GitHub Actions workflow builds and pushes a container image
2. The workflow obtains an OAuth2 token from Thunder IDP via `client_credentials` grant
3. The workflow POSTs Workload JSON directly to the OpenChoreo API

**Best for**: Simple deployments, quick iteration, teams that prefer imperative delivery.

### Approach B: GitOps with `occ` CLI

1. GitHub Actions workflow builds and pushes a container image
2. The workflow uses the `occ` CLI to generate Workload, ComponentRelease, and ReleaseBinding YAML manifests
3. The workflow commits the manifests to the GitOps repository
4. FluxCD detects the change and delivers it to the cluster

**Best for**: Teams already using GitOps workflows, audit trail requirements, environments where changes must go through Git.

---

## 5. Sample Workflow

A reference GitHub Actions workflow is provided in this repository at:

```
.github/workflows/external-ci-openchoreo.yml
```

This sample demonstrates the end-to-end flow: building a container image, authenticating with OpenChoreo, and delivering a workload. Use it as a starting point and adapt it to your project's needs.

---

## 6. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "GitHub Actions" tab not visible | Missing annotation | Add `github.com/project-slug: "org/repo"` to component metadata |
| CSP errors in browser console | GitHub Actions not enabled | Set `backstage.externalCI.githubActions.enabled: true` and redeploy |
| 401 from GitHub API | Token/App permissions | Check PAT scopes (`repo`, `actions:read`) or GitHub App permissions |
| Empty build list | Wrong repo slug | Ensure annotation matches the exact `owner/repo` where workflows run |
| Pod env vars not set | Auth type mismatch | Verify `auth.type` matches your credential setup (`app` vs `token`) |
| Backstage pod crash loop | Invalid PEM key | Ensure `github-app-private-key` in OpenBao is a valid PEM-encoded private key |

---

## 7. Limitations

- **Single GitHub organization** — multi-org support is not available
- **github.com only** — GitHub Enterprise Server is not supported
- **No build log streaming** — Backstage links to the GitHub UI for full logs
- **Read-only** — the GitHub Actions plugin can view builds but cannot trigger workflows from Backstage
- **Mutually exclusive CI annotations** — Jenkins and GitHub Actions annotations cannot be used on the same component entity; use one CI annotation per component

---

## 8. What's Next

- For the full External CI workflow guide (authentication, Workload API, Jenkins example), see the [External CI Integration](../reference-project-docs/openchoreo-docs/docs/platform-engineer-guide/workflows/external-ci.mdx) guide
- OpenChoreo issue [#3138](https://github.com/openchoreo/openchoreo/issues/3138) tracks the CI Module proposal for native multi-CI support at the controller level
- Community discussions: [#568](https://github.com/openchoreo/openchoreo/discussions/568), [#1759](https://github.com/openchoreo/openchoreo/discussions/1759), [#2979](https://github.com/openchoreo/openchoreo/discussions/2979)
