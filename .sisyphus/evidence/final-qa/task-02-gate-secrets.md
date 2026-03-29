# Task 2: Security — Gate dev seed secrets in OpenBao values

## Scenarios

### 2.1 `is_dev_stack` parameter accepted
- **File**: `pulumi/values/openbao.py:12`
- **Evidence**: `def get_values(is_dev_stack: bool = False, ...) -> dict[str, Any]:`
- **Result**: PASS

### 2.2 `is_dev_stack` passed from call site
- **File**: `pulumi/components/prerequisites.py:205`
- **Evidence**: `is_dev_stack=pulumi.get_stack() in ("dev", "rancher-desktop", "local", "test")`
- **Note**: Call site is in `prerequisites.py`, not `control_plane.py` as plan suggested — functionally correct
- **Result**: PASS

### 2.3 Hardcoded dev credentials gated behind `if is_dev_stack:`
- **File**: `pulumi/values/openbao.py:67-85`
- **Evidence**: Dev-only block includes root token, unseal keys, and bootstrap credentials ONLY inside `if is_dev_stack:` block. Non-dev path (lines 37-66) only has policy setup and Kubernetes auth config.
- **Result**: PASS

## Verdict: 3/3 PASS
