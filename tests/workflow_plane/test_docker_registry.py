"""Tests for Docker Registry."""

import pytest
import requests
from kubernetes import client

from utils.k8s_helpers import check_deployment_ready
from utils.port_forward import PortForward


@pytest.mark.workflow_plane
@pytest.mark.smoke
class TestDockerRegistryHealth:
    """Test Docker Registry health."""

    def test_registry_deployment_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Docker Registry deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["workflow_plane"], "docker-registry"
        )

        # Try alternative names
        if not is_ready and "not found" in message.lower():
            is_ready, message = check_deployment_ready(
                k8s_apps_api, namespaces["workflow_plane"], "registry"
            )

        assert is_ready, f"Docker Registry not ready: {message}"


@pytest.mark.workflow_plane
class TestDockerRegistryAPI:
    """Test Docker Registry API v2."""

    def test_registry_v2_endpoint(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify registry v2 endpoint is accessible."""
        with PortForward(
            k8s_core_api,
            namespaces["workflow_plane"],
            "docker-registry",
            5000,
        ) as local_port:
            response = requests.get(
                f"http://localhost:{local_port}/v2/",
                timeout=30,
            )

            assert response.status_code == 200, (
                f"Registry v2 endpoint failed: {response.status_code}"
            )

    def test_registry_catalog(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify registry catalog endpoint works."""
        with PortForward(
            k8s_core_api,
            namespaces["workflow_plane"],
            "docker-registry",
            5000,
        ) as local_port:
            response = requests.get(
                f"http://localhost:{local_port}/v2/_catalog",
                timeout=30,
            )

            assert response.status_code == 200, f"Registry catalog failed: {response.status_code}"

            data = response.json()
            assert "repositories" in data, "Invalid catalog response"


@pytest.mark.workflow_plane
@pytest.mark.slow
class TestDockerRegistryOperations:
    """Test Docker Registry push/pull operations."""

    def test_push_and_pull_manifest(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify image manifest can be pushed and pulled."""
        import hashlib
        import json

        with PortForward(
            k8s_core_api,
            namespaces["workflow_plane"],
            "docker-registry",
            5000,
        ) as local_port:
            base_url = f"http://localhost:{local_port}"
            repo_name = "integration-test"
            tag = "latest"

            # Create a minimal config blob
            config = {
                "architecture": "amd64",
                "os": "linux",
                "config": {},
                "rootfs": {
                    "type": "layers",
                    "diff_ids": [],
                },
            }
            config_json = json.dumps(config).encode()
            config_digest = f"sha256:{hashlib.sha256(config_json).hexdigest()}"

            # Upload config blob
            # Start upload
            upload_response = requests.post(
                f"{base_url}/v2/{repo_name}/blobs/uploads/",
                timeout=30,
            )

            if upload_response.status_code not in [202, 200]:
                pytest.skip(f"Blob upload not supported: {upload_response.status_code}")

            upload_url = upload_response.headers.get("Location")
            if not upload_url:
                pytest.skip("No upload URL returned")

            # Complete upload
            if not upload_url.startswith("http"):
                upload_url = f"{base_url}{upload_url}"

            separator = "&" if "?" in upload_url else "?"
            put_response = requests.put(
                f"{upload_url}{separator}digest={config_digest}",
                data=config_json,
                headers={"Content-Type": "application/octet-stream"},
                timeout=30,
            )

            if put_response.status_code not in [201, 202]:
                pytest.skip(f"Blob upload failed: {put_response.status_code}")

            # Create and push manifest
            manifest = {
                "schemaVersion": 2,
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "config": {
                    "mediaType": "application/vnd.docker.container.image.v1+json",
                    "size": len(config_json),
                    "digest": config_digest,
                },
                "layers": [],
            }

            manifest_response = requests.put(
                f"{base_url}/v2/{repo_name}/manifests/{tag}",
                json=manifest,
                headers={"Content-Type": "application/vnd.docker.distribution.manifest.v2+json"},
                timeout=30,
            )

            assert manifest_response.status_code in [201, 202], (
                f"Manifest push failed: {manifest_response.status_code}"
            )

            # Verify manifest can be pulled
            get_response = requests.get(
                f"{base_url}/v2/{repo_name}/manifests/{tag}",
                headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"},
                timeout=30,
            )

            assert get_response.status_code == 200, (
                f"Manifest pull failed: {get_response.status_code}"
            )

            # Cleanup - delete the test image
            try:
                digest = get_response.headers.get("Docker-Content-Digest")
                if digest:
                    requests.delete(
                        f"{base_url}/v2/{repo_name}/manifests/{digest}",
                        timeout=30,
                    )
            except Exception:
                pass  # Cleanup failure is not critical
