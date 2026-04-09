"""GitHub Actions integration tests.

Pure Python tests that verify the GitHub Actions external CI integration
is correctly wired in Helm values, schema, configmap, deployment template,
CSP, and Pulumi secret provisioning. No Pulumi SDK imports — these run
without a Pulumi engine.
"""

from __future__ import annotations
import json
import yaml
from pathlib import Path

# Path constants
HELM_DIR = (
    Path(__file__).resolve().parents[2] / "docs/reference-project-docs/openchoreo/install/helm/openchoreo-control-plane"
)
VALUES_FILE = HELM_DIR / "values.yaml"
SCHEMA_FILE = HELM_DIR / "values.schema.json"
CONFIGMAP_CI = HELM_DIR / "templates/backstage/configmap-ci.yaml"
DEPLOYMENT = HELM_DIR / "templates/backstage/deployment.yaml"
CSP_CONFIGMAP = HELM_DIR / "templates/backstage/configmap-csp.yaml"
PREREQUISITES = Path(__file__).resolve().parents[1] / "components/prerequisites.py"


def test_gha_values_schema():
    """values.schema.json includes githubActions with auth properties."""
    schema = json.loads(SCHEMA_FILE.read_text())
    gha = schema["properties"]["backstage"]["properties"]["externalCI"]["properties"]["githubActions"]
    auth = gha["properties"]["auth"]
    assert "type" in auth["properties"], "auth.type missing from schema"
    assert "app" in auth["properties"], "auth.app missing from schema"
    assert "token" in auth["properties"], "auth.token missing from schema"


def test_gha_values_defaults():
    """values.yaml githubActions defaults: disabled, auth.type=app."""
    values = yaml.safe_load(VALUES_FILE.read_text())
    gha = values["backstage"]["externalCI"]["githubActions"]
    assert gha["enabled"] is False, "githubActions should be disabled by default"
    assert gha["auth"]["type"] == "app", "default auth.type should be 'app'"
    assert "appId" in gha["auth"]["app"], "auth.app.appId missing"
    assert "token" in gha["auth"], "auth.token missing"


def test_gha_configmap_ci_rendering():
    """configmap-ci.yaml includes GitHub integration block with conditional."""
    content = CONFIGMAP_CI.read_text()
    assert "integrations" in content, "integrations block missing from configmap-ci"
    assert "GITHUB_TOKEN" in content, "GITHUB_TOKEN reference missing from configmap-ci"
    assert "githubActions.enabled" in content, "githubActions.enabled conditional missing"


def test_gha_deployment_env_vars():
    """deployment.yaml includes GitHub App env vars and token fallback."""
    content = DEPLOYMENT.read_text()
    assert "GITHUB_APP_ID" in content, "GITHUB_APP_ID env var missing"
    assert "GITHUB_APP_CLIENT_ID" in content, "GITHUB_APP_CLIENT_ID env var missing"
    assert "GITHUB_APP_CLIENT_SECRET" in content, "GITHUB_APP_CLIENT_SECRET env var missing"
    assert "GITHUB_APP_WEBHOOK_SECRET" in content, "GITHUB_APP_WEBHOOK_SECRET env var missing"
    assert "GITHUB_APP_PRIVATE_KEY" in content, "GITHUB_APP_PRIVATE_KEY env var missing"
    assert "GITHUB_TOKEN" in content, "GITHUB_TOKEN fallback env var missing"
    # Verify auth type conditional
    assert "auth.type" in content and '"app"' in content, "auth.type conditional missing"


def test_gha_csp_connect_src():
    """CSP configmap includes api.github.com when GHA enabled."""
    content = CSP_CONFIGMAP.read_text()
    assert "api.github.com" in content, "api.github.com missing from CSP"
    assert "githubActions.enabled" in content, "githubActions.enabled conditional missing from CSP"


def test_jenkins_unaffected_by_gha():
    """Jenkins integration is completely unchanged by GHA addition."""
    content = DEPLOYMENT.read_text()
    assert "JENKINS_BASE_URL" in content, "Jenkins JENKINS_BASE_URL missing"
    assert "JENKINS_USERNAME" in content, "Jenkins JENKINS_USERNAME missing"
    assert "JENKINS_API_KEY" in content, "Jenkins JENKINS_API_KEY missing"
    assert "jenkins-api-key" in content, "jenkins-api-key secret key missing"

    # Verify Jenkins in values.yaml
    values = yaml.safe_load(VALUES_FILE.read_text())
    jenkins = values["backstage"]["externalCI"]["jenkins"]
    assert jenkins["enabled"] is False, "Jenkins should remain disabled by default"
    assert jenkins["baseUrl"] == "https://jenkins.example.com", "Jenkins baseUrl changed"

    # Verify Jenkins in configmap-ci
    ci_content = CONFIGMAP_CI.read_text()
    assert "jenkins:" in ci_content, "Jenkins config block missing from configmap-ci"


def test_gha_secret_chain():
    """prerequisites.py provisions all GitHub secrets in push_secret and dev data."""
    content = PREREQUISITES.read_text()
    # Push secret keys
    assert '"github-token"' in content, "github-token missing from push_secret"
    assert '"github-app-client-secret"' in content, "github-app-client-secret missing"
    assert '"github-app-webhook-secret"' in content, "github-app-webhook-secret missing"
    assert '"github-app-private-key"' in content, "github-app-private-key missing"
    # Dev stack keys
    assert '"backstage-github-token"' in content, "backstage-github-token missing from dev secrets"
    assert '"backstage-github-app-client-secret"' in content, "backstage-github-app-client-secret missing"
    assert '"backstage-github-app-webhook-secret"' in content, "backstage-github-app-webhook-secret missing"
    assert '"backstage-github-app-private-key"' in content, "backstage-github-app-private-key missing"
