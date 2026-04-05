"""Kubernetes port-forward context manager."""

import socket
import subprocess
import time
from typing import Any

from kubernetes import client
from kubernetes.client.rest import ApiException


class PortForward:
    """Context manager for Kubernetes port forwarding.

    Uses kubectl port-forward under the hood for reliability.

    Example:
        with PortForward(core_api, "default", "my-pod", 8080) as local_port:
            response = requests.get(f"http://localhost:{local_port}")
    """

    def __init__(
        self,
        core_api: client.CoreV1Api,
        namespace: str,
        pod_name: str,
        remote_port: int,
        local_port: int | None = None,
        kubeconfig: str | None = None,
        context: str | None = None,
    ):
        """Initialize port forward.

        Args:
            core_api: Kubernetes Core V1 API client (for pod lookup)
            namespace: Pod namespace
            pod_name: Pod name (can be a prefix, will find first match)
            remote_port: Remote port to forward
            local_port: Local port (None = auto-assign)
            kubeconfig: Path to kubeconfig file
            context: Kubernetes context name
        """
        self.core_api = core_api
        self.namespace = namespace
        self.pod_name = pod_name
        self.remote_port = remote_port
        self._local_port = local_port
        self.kubeconfig = kubeconfig
        self.context = context
        self._process: subprocess.Popen | None = None
        self._actual_local_port: int | None = None

    def _find_pod(self) -> str:
        """Find pod by name or prefix."""
        try:
            # Try exact match first
            self.core_api.read_namespaced_pod(self.pod_name, self.namespace)
            return self.pod_name
        except ApiException as e:
            if e.status != 404:
                raise

        # Try prefix match
        pods = self.core_api.list_namespaced_pod(self.namespace)
        for pod in pods.items:
            if pod.metadata.name.startswith(self.pod_name):
                return pod.metadata.name

        raise ValueError(f"Pod {self.pod_name} not found in namespace {self.namespace}")

    def _find_free_port(self) -> int:
        """Find a free local port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            return s.getsockname()[1]

    def _wait_for_port(self, port: int, timeout: int = 30) -> bool:
        """Wait for port to become available."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(("localhost", port))
                    return True
            except (socket.error, socket.timeout):
                time.sleep(0.5)
        return False

    def __enter__(self) -> int:
        """Start port forwarding and return local port."""
        # Find the actual pod name
        actual_pod = self._find_pod()

        # Determine local port
        if self._local_port is None:
            self._actual_local_port = self._find_free_port()
        else:
            self._actual_local_port = self._local_port

        # Build kubectl command
        cmd = ["kubectl", "port-forward"]

        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        if self.context:
            cmd.extend(["--context", self.context])

        cmd.extend(
            [
                "-n",
                self.namespace,
                f"pod/{actual_pod}",
                f"{self._actual_local_port}:{self.remote_port}",
            ]
        )

        # Start port-forward process
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for port to be ready
        if not self._wait_for_port(self._actual_local_port):
            self._cleanup()
            raise RuntimeError(f"Port forward to {actual_pod}:{self.remote_port} failed to start")

        return self._actual_local_port

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop port forwarding."""
        self._cleanup()

    def _cleanup(self) -> None:
        """Clean up port-forward process."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None


class ServicePortForward:
    """Port forward to a Kubernetes service (finds a backing pod).

    Example:
        with ServicePortForward(core_api, "default", "my-service", 80) as local_port:
            response = requests.get(f"http://localhost:{local_port}")
    """

    def __init__(
        self,
        core_api: client.CoreV1Api,
        namespace: str,
        service_name: str,
        service_port: int,
        local_port: int | None = None,
        kubeconfig: str | None = None,
        context: str | None = None,
    ):
        """Initialize service port forward.

        Args:
            core_api: Kubernetes Core V1 API client
            namespace: Service namespace
            service_name: Service name
            service_port: Service port to forward
            local_port: Local port (None = auto-assign)
            kubeconfig: Path to kubeconfig file
            context: Kubernetes context name
        """
        self.core_api = core_api
        self.namespace = namespace
        self.service_name = service_name
        self.service_port = service_port
        self._local_port = local_port
        self.kubeconfig = kubeconfig
        self.context = context
        self._port_forward: PortForward | None = None

    def _find_pod_for_service(self) -> tuple[str, int]:
        """Find a pod backing the service and the target port."""
        # Get service
        service = self.core_api.read_namespaced_service(self.service_name, self.namespace)

        # Get selector
        selector = service.spec.selector
        if not selector:
            raise ValueError(f"Service {self.service_name} has no selector")

        # Find target port
        target_port = self.service_port
        for port in service.spec.ports:
            if port.port == self.service_port:
                target_port = port.target_port or port.port
                break

        # Build label selector string
        label_selector = ",".join(f"{k}={v}" for k, v in selector.items())

        # Find pods
        pods = self.core_api.list_namespaced_pod(self.namespace, label_selector=label_selector)

        for pod in pods.items:
            if pod.status.phase == "Running":
                return pod.metadata.name, int(target_port)

        raise ValueError(f"No running pods found for service {self.service_name}")

    def __enter__(self) -> int:
        """Start port forwarding and return local port."""
        pod_name, target_port = self._find_pod_for_service()

        self._port_forward = PortForward(
            self.core_api,
            self.namespace,
            pod_name,
            target_port,
            self._local_port,
            self.kubeconfig,
            self.context,
        )

        return self._port_forward.__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop port forwarding."""
        if self._port_forward:
            self._port_forward.__exit__(exc_type, exc_val, exc_tb)
