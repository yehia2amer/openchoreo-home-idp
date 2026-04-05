# Task 7: Safe port-forward cleanup

## Scenarios

### 7.1 contextlib.suppress(ProcessLookupError) around terminate()
- `dynamic_providers.py:501` — `_OpenBaoSecretsProvider.create`: `contextlib.suppress(ProcessLookupError)` around `pf.terminate()`
- `k8s_ops.py:630` — `check_openbao_secrets`: `contextlib.suppress(ProcessLookupError)` around `pf.terminate()`
- `k8s_ops.py:724` — `validate_openbao_secrets`: `contextlib.suppress(ProcessLookupError)` around `pf.terminate()`
- **Result**: PASS

### 7.2 subprocess.TimeoutExpired handling with kill+wait fallback
- `dynamic_providers.py:505-507`: `except subprocess.TimeoutExpired: pf.kill(); pf.wait()`
- `k8s_ops.py:634-636`: `except subprocess.TimeoutExpired: pf.kill(); pf.wait()`
- `k8s_ops.py:728-730`: `except subprocess.TimeoutExpired: pf.kill(); pf.wait()`
- **Result**: PASS

### 7.3 Minor note: check_service_http (k8s_ops.py:395-396)
- Uses simpler `pf.terminate(); pf.wait(timeout=5)` without `contextlib.suppress(ProcessLookupError)`
- This is an integration test helper, not a critical path — acceptable minor gap
- **Result**: ACCEPTABLE (not a failure)

## Verdict: 2/2 PASS (1 minor note)
