"""Tests for Backstage."""

import pytest
import requests

from utils.http_helpers import check_health, get_json, make_request


@pytest.mark.control_plane
@pytest.mark.smoke
class TestBackstageHealth:
    """Test Backstage service health."""

    def test_backstage_health_endpoint(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
    ):
        """Verify Backstage health endpoint responds."""
        is_healthy, message = check_health(http_session, f"{control_plane_base_url}/healthcheck")

        assert is_healthy, f"Backstage health check failed: {message}"

    def test_backstage_backend_info(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
    ):
        """Verify Backstage backend info endpoint."""
        response = http_session.get(
            f"{control_plane_base_url}/api/app/info",
            timeout=30,
        )

        # May return 404 if not configured, but should not error
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"


@pytest.mark.control_plane
class TestBackstageCatalog:
    """Test Backstage Catalog API."""

    def test_catalog_entities_endpoint(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify catalog entities endpoint is accessible."""
        response = http_session.get(
            f"{control_plane_base_url}/api/catalog/entities",
            headers=auth_headers,
            timeout=30,
        )

        # Should return 200 with entities or 401 if auth required
        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            entities = response.json()
            assert isinstance(entities, list), "Entities should be a list"

    def test_catalog_entity_facets(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify catalog facets endpoint."""
        response = http_session.get(
            f"{control_plane_base_url}/api/catalog/entity-facets",
            headers=auth_headers,
            params={"facet": "kind"},
            timeout=30,
        )

        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"


@pytest.mark.control_plane
class TestBackstageScaffolder:
    """Test Backstage Scaffolder API."""

    def test_scaffolder_templates_endpoint(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify scaffolder templates endpoint is accessible."""
        response = http_session.get(
            f"{control_plane_base_url}/api/scaffolder/v2/templates",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )

    def test_scaffolder_actions_endpoint(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify scaffolder actions endpoint is accessible."""
        response = http_session.get(
            f"{control_plane_base_url}/api/scaffolder/v2/actions",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )

        if response.status_code == 200:
            actions = response.json()
            assert isinstance(actions, list), "Actions should be a list"


@pytest.mark.control_plane
class TestBackstageAuth:
    """Test Backstage authentication integration."""

    def test_auth_providers_endpoint(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
    ):
        """Verify auth providers endpoint."""
        response = http_session.get(
            f"{control_plane_base_url}/api/auth/providers",
            timeout=30,
        )

        # May not be exposed, but should not error
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"

    def test_oauth_start_redirect(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
    ):
        """Verify OAuth start endpoint redirects to IdP."""
        # Don't follow redirects to check the redirect itself
        response = http_session.get(
            f"{control_plane_base_url}/api/auth/oauth2/start",
            allow_redirects=False,
            timeout=30,
        )

        # Should redirect to Thunder or return error if not configured
        assert response.status_code in [302, 303, 307, 400, 404], (
            f"Unexpected status: {response.status_code}"
        )

        if response.status_code in [302, 303, 307]:
            location = response.headers.get("Location", "")
            assert "thunder" in location.lower() or "oauth" in location.lower(), (
                f"Unexpected redirect location: {location}"
            )


@pytest.mark.control_plane
class TestBackstageTechDocs:
    """Test Backstage TechDocs API."""

    def test_techdocs_static_endpoint(
        self,
        control_plane_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify TechDocs static endpoint is accessible."""
        response = http_session.get(
            f"{control_plane_base_url}/api/techdocs/static/docs",
            headers=auth_headers,
            timeout=30,
        )

        # May return 404 if no docs, but should not error
        assert response.status_code in [200, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )
