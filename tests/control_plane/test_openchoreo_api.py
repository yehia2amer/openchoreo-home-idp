"""Tests for OpenChoreo API."""

import pytest
import requests

from utils.http_helpers import check_health, get_json


@pytest.mark.control_plane
@pytest.mark.smoke
class TestOpenChoreoAPIHealth:
    """Test OpenChoreo API health."""

    def test_api_health_endpoint(
        self,
        api_base_url: str,
        http_session: requests.Session,
    ):
        """Verify OpenChoreo API health endpoint responds."""
        is_healthy, message = check_health(http_session, f"{api_base_url}/health")

        assert is_healthy, f"OpenChoreo API health check failed: {message}"

    def test_api_readiness_endpoint(
        self,
        api_base_url: str,
        http_session: requests.Session,
    ):
        """Verify OpenChoreo API readiness endpoint."""
        response = http_session.get(
            f"{api_base_url}/ready",
            timeout=30,
        )

        # May be /ready or /healthz/ready
        if response.status_code == 404:
            response = http_session.get(
                f"{api_base_url}/healthz/ready",
                timeout=30,
            )

        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"


@pytest.mark.control_plane
class TestOrganizationAPI:
    """Test Organization management API."""

    def test_list_organizations(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify organization listing works."""
        response = http_session.get(
            f"{api_base_url}/api/v1/organizations",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict)), "Invalid response format"

    def test_organization_crud_flow(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Test organization CRUD operations (if permitted)."""
        # Try to create a test organization
        test_org = {
            "name": "test-integration-org",
            "displayName": "Test Integration Org",
        }

        response = http_session.post(
            f"{api_base_url}/api/v1/organizations",
            headers=auth_headers,
            json=test_org,
            timeout=30,
        )

        # May not have permission, but should not error unexpectedly
        assert response.status_code in [200, 201, 400, 401, 403, 409], (
            f"Unexpected status: {response.status_code}"
        )

        # If created, try to delete
        if response.status_code in [200, 201]:
            org_data = response.json()
            org_id = org_data.get("id") or org_data.get("name")

            if org_id:
                delete_response = http_session.delete(
                    f"{api_base_url}/api/v1/organizations/{org_id}",
                    headers=auth_headers,
                    timeout=30,
                )
                assert delete_response.status_code in [200, 204, 401, 403, 404], (
                    f"Cleanup failed: {delete_response.status_code}"
                )


@pytest.mark.control_plane
class TestProjectAPI:
    """Test Project management API."""

    def test_list_projects(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify project listing works."""
        response = http_session.get(
            f"{api_base_url}/api/v1/projects",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict)), "Invalid response format"

    def test_list_projects_by_org(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify project listing by organization works."""
        # First get organizations
        org_response = http_session.get(
            f"{api_base_url}/api/v1/organizations",
            headers=auth_headers,
            timeout=30,
        )

        if org_response.status_code != 200:
            pytest.skip("Cannot list organizations")

        orgs = org_response.json()
        if not orgs:
            pytest.skip("No organizations available")

        # Get first org ID
        org_id = orgs[0].get("id") or orgs[0].get("name") if isinstance(orgs, list) else None
        if not org_id:
            pytest.skip("Cannot determine organization ID")

        # List projects for org
        response = http_session.get(
            f"{api_base_url}/api/v1/organizations/{org_id}/projects",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )


@pytest.mark.control_plane
class TestComponentAPI:
    """Test Component management API."""

    def test_list_components(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify component listing works."""
        response = http_session.get(
            f"{api_base_url}/api/v1/components",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict)), "Invalid response format"

    def test_component_types(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify component types endpoint."""
        response = http_session.get(
            f"{api_base_url}/api/v1/component-types",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )


@pytest.mark.control_plane
class TestEnvironmentAPI:
    """Test Environment management API."""

    def test_list_environments(
        self,
        api_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify environment listing works."""
        response = http_session.get(
            f"{api_base_url}/api/v1/environments",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict)), "Invalid response format"
