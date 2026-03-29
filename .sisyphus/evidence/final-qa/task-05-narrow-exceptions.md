# Task 5: Narrow exception handling

## Scenarios

### 5.1 k8s_client.ApiException used for Kubernetes API errors
- **File**: `pulumi/helpers/k8s_ops.py`
- **Locations**: Lines 66-68, 98-100, 144-148, 179-183, 212-214, 230-232, 277-278, 424-425, 446-447, 468-469, 489-492, 523-524, 555-558, 579-582
- All catch `k8s_client.ApiException` instead of bare `except Exception`
- **Result**: PASS

### 5.2 Specific exceptions for non-K8s errors
- `k8s_ops.py:388`: `except (urllib.error.URLError, OSError)` — narrowed for HTTP errors
- `k8s_ops.py:618`: `except hvac.exceptions.VaultError` — narrowed for OpenBao errors
- `k8s_ops.py:716`: `except hvac.exceptions.VaultError` — narrowed for validation
- `dynamic_providers.py:268`: `except k8s_client.ApiException` — narrowed in delete
- **Result**: PASS

### 5.3 Acceptable remaining broad exceptions
- `k8s_ops.py:624`: Outer `except Exception` catch-all for port-forward block — acceptable as safety net for integration test helper
- `k8s_ops.py:669`: `except k8s_client.ApiException: pass` in polling loop — **INTENTIONAL per constraints** (not flagged)
- **Result**: ACCEPTABLE

## Verdict: 2/2 PASS (+ 2 acceptable exceptions noted)
