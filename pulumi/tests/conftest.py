from __future__ import annotations

import importlib
import os

pytest = importlib.import_module("pytest")


@pytest.fixture(scope="session")
def kubeconfig() -> str:
    return os.path.expanduser(os.getenv("KUBECONFIG", "~/.kube/config"))


@pytest.fixture(scope="session")
def pulumi_stack() -> str:
    return os.getenv("PULUMI_STACK", "dev")


@pytest.fixture(scope="session")
def kube_context(pulumi_stack: str) -> str:
    return os.getenv("KUBE_CONTEXT", pulumi_stack)


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "e2e: end-to-end infrastructure tests")
    config.addinivalue_line("markers", "slow: long-running tests")
