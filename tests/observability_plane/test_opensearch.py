"""Tests for OpenSearch."""

import pytest
from kubernetes import client
from opensearchpy import OpenSearch

from utils.k8s_helpers import get_pod_by_name_prefix
from utils.port_forward import PortForward


@pytest.mark.observability
@pytest.mark.smoke
class TestOpenSearchHealth:
    """Test OpenSearch cluster health."""

    def test_opensearch_statefulset_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify OpenSearch StatefulSet is ready."""
        sts = k8s_apps_api.read_namespaced_stateful_set(
            "opensearch-cluster-master", namespaces["observability_plane"]
        )

        assert sts.status is not None
        assert sts.status.ready_replicas is not None
        assert sts.status.ready_replicas > 0, "OpenSearch StatefulSet not ready"

    def test_opensearch_cluster_health(
        self,
        opensearch_client: OpenSearch,
    ):
        """Verify OpenSearch cluster health is green or yellow."""
        health = opensearch_client.cluster.health()

        assert health["status"] in ["green", "yellow"], (
            f"OpenSearch cluster unhealthy: {health['status']}"
        )
        assert health["number_of_nodes"] > 0, "No OpenSearch nodes"

    def test_opensearch_nodes_available(
        self,
        opensearch_client: OpenSearch,
    ):
        """Verify OpenSearch nodes are available."""
        nodes = opensearch_client.nodes.info()

        assert "_nodes" in nodes
        assert nodes["_nodes"]["total"] > 0, "No OpenSearch nodes available"
        assert nodes["_nodes"]["successful"] > 0, "No successful node responses"


@pytest.mark.observability
class TestOpenSearchIndices:
    """Test OpenSearch index management."""

    def test_list_indices(
        self,
        opensearch_client: OpenSearch,
    ):
        """Verify indices can be listed."""
        indices = opensearch_client.cat.indices(format="json")

        assert isinstance(indices, list), "Invalid indices response"

    def test_log_indices_exist(
        self,
        opensearch_client: OpenSearch,
    ):
        """Verify log indices exist (if logs are being collected)."""
        indices = opensearch_client.cat.indices(format="json")

        # Look for common log index patterns
        log_patterns = ["logs-", "fluentbit-", "logstash-", "filebeat-"]

        log_indices = [
            idx for idx in indices if any(idx.get("index", "").startswith(p) for p in log_patterns)
        ]

        if not log_indices:
            pytest.skip("No log indices found (logs may not be collected yet)")


@pytest.mark.observability
class TestOpenSearchOperations:
    """Test OpenSearch document operations."""

    def test_index_and_search_document(
        self,
        opensearch_client: OpenSearch,
    ):
        """Verify document indexing and search works."""
        test_index = "integration-test-index"
        test_doc = {
            "message": "Integration test document",
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "info",
        }

        try:
            # Index document
            index_response = opensearch_client.index(
                index=test_index,
                body=test_doc,
                refresh=True,
            )

            assert index_response["result"] in ["created", "updated"], (
                f"Index failed: {index_response}"
            )

            # Search for document
            search_response = opensearch_client.search(
                index=test_index,
                body={"query": {"match_all": {}}},
            )

            assert search_response["hits"]["total"]["value"] > 0, (
                "No documents found after indexing"
            )

        finally:
            # Cleanup
            try:
                opensearch_client.indices.delete(index=test_index)
            except Exception:
                pass

    def test_bulk_operations(
        self,
        opensearch_client: OpenSearch,
    ):
        """Verify bulk operations work."""
        test_index = "integration-test-bulk"

        try:
            # Bulk index
            actions = []
            for i in range(5):
                actions.append({"index": {"_index": test_index}})
                actions.append({"message": f"Bulk test {i}", "seq": i})

            bulk_response = opensearch_client.bulk(body=actions, refresh=True)

            assert not bulk_response.get("errors", True), (
                f"Bulk operation had errors: {bulk_response}"
            )

        finally:
            # Cleanup
            try:
                opensearch_client.indices.delete(index=test_index)
            except Exception:
                pass
