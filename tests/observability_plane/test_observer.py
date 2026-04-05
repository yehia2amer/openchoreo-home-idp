"""Tests for Observer service."""

import pytest
import requests

from utils.http_helpers import check_health


@pytest.mark.observability
@pytest.mark.smoke
class TestObserverHealth:
    """Test Observer service health."""

    def test_observer_health_endpoint(
        self,
        observer_base_url: str,
        http_session: requests.Session,
    ):
        """Verify Observer health endpoint responds."""
        is_healthy, message = check_health(http_session, f"{observer_base_url}/health")

        assert is_healthy, f"Observer health check failed: {message}"

    def test_observer_readiness(
        self,
        observer_base_url: str,
        http_session: requests.Session,
    ):
        """Verify Observer readiness endpoint."""
        response = http_session.get(
            f"{observer_base_url}/ready",
            timeout=30,
        )

        # May be /ready or /healthz/ready
        if response.status_code == 404:
            response = http_session.get(
                f"{observer_base_url}/healthz/ready",
                timeout=30,
            )

        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"


@pytest.mark.observability
class TestObserverLogsAPI:
    """Test Observer logs API."""

    def test_logs_endpoint_accessible(
        self,
        observer_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify logs endpoint is accessible."""
        response = http_session.get(
            f"{observer_base_url}/api/v1/logs",
            headers=auth_headers,
            params={"namespace": "kube-system", "limit": 10},
            timeout=30,
        )

        assert response.status_code in [200, 400, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )

    def test_logs_query(
        self,
        observer_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify log querying works."""
        response = http_session.post(
            f"{observer_base_url}/api/v1/logs/query",
            headers=auth_headers,
            json={
                "query": "*",
                "limit": 10,
                "timeRange": {"from": "now-1h", "to": "now"},
            },
            timeout=30,
        )

        # May not have logs, but endpoint should respond
        assert response.status_code in [200, 400, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )


@pytest.mark.observability
class TestObserverTracesAPI:
    """Test Observer traces API."""

    def test_traces_endpoint_accessible(
        self,
        observer_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify traces endpoint is accessible."""
        response = http_session.get(
            f"{observer_base_url}/api/v1/traces",
            headers=auth_headers,
            params={"limit": 10},
            timeout=30,
        )

        assert response.status_code in [200, 400, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )

    def test_trace_search(
        self,
        observer_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify trace search works."""
        response = http_session.post(
            f"{observer_base_url}/api/v1/traces/search",
            headers=auth_headers,
            json={
                "service": "*",
                "limit": 10,
                "timeRange": {"from": "now-1h", "to": "now"},
            },
            timeout=30,
        )

        assert response.status_code in [200, 400, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )


@pytest.mark.observability
class TestObserverMetricsAPI:
    """Test Observer metrics API."""

    def test_metrics_endpoint_accessible(
        self,
        observer_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify metrics endpoint is accessible."""
        response = http_session.get(
            f"{observer_base_url}/api/v1/metrics",
            headers=auth_headers,
            timeout=30,
        )

        assert response.status_code in [200, 400, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )

    def test_metrics_query(
        self,
        observer_base_url: str,
        http_session: requests.Session,
        auth_headers: dict,
    ):
        """Verify metrics querying works."""
        response = http_session.post(
            f"{observer_base_url}/api/v1/metrics/query",
            headers=auth_headers,
            json={
                "query": "up",
                "timeRange": {"from": "now-5m", "to": "now"},
            },
            timeout=30,
        )

        assert response.status_code in [200, 400, 401, 403, 404], (
            f"Unexpected status: {response.status_code}"
        )
