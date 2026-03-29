# Task 1: Security — Fail-fast on non-dev stacks

## Scenarios

### 1.1 `is_dev_stack` defined correctly
- **File**: `pulumi/config.py:213`
- **Evidence**: `is_dev_stack = stack in ("dev", "rancher-desktop", "local", "test")`
- **Result**: PASS

### 1.2 ValueError raised for missing opensearch_admin_password on non-dev stacks
- **File**: `pulumi/config.py:218`
- **Evidence**: `raise ValueError(...)` with message containing stack name and `pulumi config set --secret openchoreo:opensearch_admin_password`
- **Result**: PASS

### 1.3 ValueError raised for missing opensearch_seed_password on non-dev stacks
- **File**: `pulumi/config.py:229`
- **Evidence**: `raise ValueError(...)` with message containing stack name and `pulumi config set --secret openchoreo:opensearch_seed_password`
- **Result**: PASS

### 1.4 Dev stacks still get defaults
- **Evidence**: Lines 220-221 set `"root"` and lines 231-232 set `"ThisIsTheOpenSearchPassword1"` when `is_dev_stack` is True
- **Result**: PASS

## Verdict: 4/4 PASS
