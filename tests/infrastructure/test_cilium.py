"""Tests for Cilium CNI and Gateway API."""

import pytest
from kubernetes import client

from utils.k8s_helpers import check_resource_condition, get_custom_resource


@pytest.mark.infrastructure
@pytest.mark.smoke
class TestCiliumAgent:
    """Test Cilium agent health and status."""

    def test_cilium_daemonset_running(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Cilium DaemonSet is running on all nodes."""
        ds = k8s_apps_api.read_namespaced_daemon_set("cilium", namespaces["cilium"])

        assert ds.status is not None
        assert ds.status.desired_number_scheduled > 0, "No nodes scheduled for Cilium"
        assert ds.status.number_ready == ds.status.desired_number_scheduled, (
            f"Cilium agents not ready: {ds.status.number_ready}/{ds.status.desired_number_scheduled}"
        )

    def test_cilium_operator_running(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Cilium Operator deployment is ready."""
        deployment = k8s_apps_api.read_namespaced_deployment(
            "cilium-operator", namespaces["cilium"]
        )

        assert deployment.status is not None
        assert deployment.status.ready_replicas is not None
        assert deployment.status.ready_replicas > 0, "Cilium operator not ready"


@pytest.mark.infrastructure
class TestCiliumL2Announcements:
    """Test Cilium L2 announcement configuration."""

    def test_loadbalancer_ip_pool_exists(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify CiliumLoadBalancerIPPool is configured."""
        pool = get_custom_resource(
            k8s_custom_api,
            group="cilium.io",
            version="v2alpha1",
            plural="ciliumloadbalancerippools",
            name="default-pool",
        )

        assert pool is not None, "CiliumLoadBalancerIPPool 'default-pool' not found"

        # Check pool has CIDR blocks defined
        spec = pool.get("spec", {})
        blocks = spec.get("blocks", []) or spec.get("cidrs", [])
        assert len(blocks) > 0, "No IP blocks defined in pool"

    def test_l2_announcement_policy_exists(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify CiliumL2AnnouncementPolicy is configured."""
        policy = get_custom_resource(
            k8s_custom_api,
            group="cilium.io",
            version="v2alpha1",
            plural="ciliuml2announcementpolicies",
            name="default-l2-policy",
        )

        assert policy is not None, "CiliumL2AnnouncementPolicy 'default-l2-policy' not found"


@pytest.mark.infrastructure
class TestGatewayAPI:
    """Test Gateway API controller and resources."""

    def test_gateway_class_accepted(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify Cilium GatewayClass is accepted."""
        gateway_class = get_custom_resource(
            k8s_custom_api,
            group="gateway.networking.k8s.io",
            version="v1",
            plural="gatewayclasses",
            name="cilium",
        )

        assert gateway_class is not None, "GatewayClass 'cilium' not found"
        assert check_resource_condition(gateway_class, "Accepted"), (
            "GatewayClass 'cilium' not accepted"
        )

    def test_control_plane_gateway_programmed(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify control plane Gateway is programmed."""
        gateway = get_custom_resource(
            k8s_custom_api,
            group="gateway.networking.k8s.io",
            version="v1",
            plural="gateways",
            name="gateway-shared",
            namespace=namespaces["control_plane"],
        )

        assert gateway is not None, "Control plane Gateway not found"
        assert check_resource_condition(gateway, "Programmed"), (
            "Control plane Gateway not programmed"
        )

        # Check gateway has an address assigned
        status = gateway.get("status", {})
        addresses = status.get("addresses", [])
        assert len(addresses) > 0, "Gateway has no addresses assigned"

    def test_data_plane_gateway_programmed(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify data plane Gateway is programmed."""
        gateway = get_custom_resource(
            k8s_custom_api,
            group="gateway.networking.k8s.io",
            version="v1",
            plural="gateways",
            name="gateway-shared",
            namespace=namespaces["data_plane"],
        )

        assert gateway is not None, "Data plane Gateway not found"
        assert check_resource_condition(gateway, "Programmed"), "Data plane Gateway not programmed"


@pytest.mark.infrastructure
class TestHubble:
    """Test Hubble observability."""

    def test_hubble_relay_running(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Hubble Relay deployment is ready."""
        try:
            deployment = k8s_apps_api.read_namespaced_deployment(
                "hubble-relay", namespaces["cilium"]
            )

            assert deployment.status is not None
            assert deployment.status.ready_replicas is not None
            assert deployment.status.ready_replicas > 0, "Hubble Relay not ready"
        except client.ApiException as e:
            if e.status == 404:
                pytest.skip("Hubble Relay not deployed")
            raise

    def test_hubble_ui_running(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Hubble UI deployment is ready (if deployed)."""
        try:
            deployment = k8s_apps_api.read_namespaced_deployment("hubble-ui", namespaces["cilium"])

            assert deployment.status is not None
            assert deployment.status.ready_replicas is not None
            assert deployment.status.ready_replicas > 0, "Hubble UI not ready"
        except client.ApiException as e:
            if e.status == 404:
                pytest.skip("Hubble UI not deployed")
            raise
