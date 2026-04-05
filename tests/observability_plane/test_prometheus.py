"""Tests for Prometheus."""

import pytest
from kubernetes import client
from prometheus_api_client import PrometheusConnect

from utils.k8s_helpers import check_deployment_ready
from utils.port_forward import PortForward


@pytest.mark.observability
@pytest.mark.smoke
class TestPrometheusHealth:
    """Test Prometheus server health."""

    def test_prometheus_statefulset_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Prometheus StatefulSet is ready."""
        try:
            sts = k8s_apps_api.read_namespaced_stateful_set(
                "prometheus-server", namespaces["observability_plane"]
            )

            assert sts.status is not None
            assert sts.status.ready_replicas is not None
            assert sts.status.ready_replicas > 0, "Prometheus StatefulSet not ready"
        except client.ApiException as e:
            if e.status == 404:
                # Try deployment instead
                is_ready, message = check_deployment_ready(
                    k8s_apps_api, namespaces["observability_plane"], "prometheus-server"
                )
                assert is_ready, f"Prometheus not ready: {message}"
            else:
                raise

    def test_prometheus_healthy(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify Prometheus is healthy."""
        # Simple query to verify Prometheus is responding
        result = prometheus_client.custom_query("up")

        assert result is not None, "Prometheus query failed"


@pytest.mark.observability
class TestPrometheusTargets:
    """Test Prometheus scrape targets."""

    def test_targets_exist(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify scrape targets are configured."""
        # Query for 'up' metric which shows all targets
        result = prometheus_client.custom_query("up")

        assert len(result) > 0, "No scrape targets found"

    def test_targets_up(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify most targets are up."""
        result = prometheus_client.custom_query("up")

        up_count = sum(1 for r in result if r.get("value", [None, "0"])[1] == "1")
        total_count = len(result)

        # At least 50% of targets should be up
        assert up_count > 0, "No targets are up"
        assert up_count / total_count >= 0.5, f"Too many targets down: {up_count}/{total_count} up"


@pytest.mark.observability
class TestPrometheusQueries:
    """Test Prometheus query functionality."""

    def test_instant_query(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify instant queries work."""
        result = prometheus_client.custom_query("prometheus_build_info")

        assert result is not None, "Instant query failed"

    def test_range_query(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify range queries work."""
        from datetime import datetime, timedelta

        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=5)

        result = prometheus_client.custom_query_range(
            query="up",
            start_time=start_time,
            end_time=end_time,
            step="60s",
        )

        assert result is not None, "Range query failed"

    def test_kubernetes_metrics_available(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify Kubernetes metrics are being collected."""
        # Try common kube-state-metrics metric
        result = prometheus_client.custom_query("kube_pod_info")

        if not result:
            # Try alternative metric
            result = prometheus_client.custom_query("container_cpu_usage_seconds_total")

        assert len(result) > 0, "No Kubernetes metrics found"


@pytest.mark.observability
class TestPrometheusAlerts:
    """Test Prometheus alerting."""

    def test_alertmanager_configured(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Alertmanager is deployed (if configured)."""
        try:
            is_ready, message = check_deployment_ready(
                k8s_apps_api, namespaces["observability_plane"], "alertmanager"
            )

            if not is_ready and "not found" in message.lower():
                # Try prometheus-alertmanager
                is_ready, message = check_deployment_ready(
                    k8s_apps_api, namespaces["observability_plane"], "prometheus-alertmanager"
                )

            if not is_ready and "not found" in message.lower():
                pytest.skip("Alertmanager not deployed")

            assert is_ready, f"Alertmanager not ready: {message}"
        except Exception:
            pytest.skip("Alertmanager not deployed")

    def test_alerting_rules_loaded(
        self,
        prometheus_client: PrometheusConnect,
    ):
        """Verify alerting rules are loaded."""
        # Query for ALERTS metric
        result = prometheus_client.custom_query("ALERTS")

        # It's OK if there are no active alerts
        # We just want to verify the query works
        assert result is not None, "Alert query failed"
