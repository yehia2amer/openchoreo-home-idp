# Task 11: E2E test collection

## Scenarios

### 11.1 Test collection succeeds with 5 tests
- **Command**: `uv run pytest tests/ -v --co`
- **Result**: 5 tests collected in 0.39s
- Tests:
  - `test_e2e_smoke.py::test_control_plane_api_deployment_ready`
  - `test_e2e_smoke.py::test_thunder_httproute_accepted`
  - `test_e2e_smoke.py::test_backstage_service_http`
  - `test_e2e_smoke.py::test_gateway_httproute_crd_exists`
  - `test_e2e_smoke.py::test_backstage_secret_exists`
- **Result**: PASS

### 11.2 Markers present on all tests
- All 5 tests decorated with `@pytest.mark.e2e` and `@pytest.mark.timeout(120)`
- **Result**: PASS

### 11.3 Fixtures and pyproject config correct
- `tests/conftest.py`: `kubeconfig`, `pulumi_stack`, `kube_context` fixtures (session-scoped) + `pytest_configure` with marker registration
- `pyproject.toml`: `[dependency-groups] test = ["pytest>=8.0", "pytest-timeout>=2.0"]`, markers config, testpaths = ["tests"]
- **Result**: PASS

## Verdict: 3/3 PASS
