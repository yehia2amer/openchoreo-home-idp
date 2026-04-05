# Bug Details Evidence — Task 2

## Bug 1: Pulumi-Terraform Bridge State Serialization Crash
### Symptom
`ConfigurationApply` succeeds, then the provider crashes in `turnaroundCheck` with: `recovered raw state does not byte-for-byte match the original raw state`.

### Root Cause
Bridge rawstate comparison was too strict across Terraform/Pulumi round-tripping. Timeouts handling, null-map normalization, and diagnostics all contributed to a false mismatch.

### Fix Applied
- Reference: `.sisyphus/evidence/task-1-bridge-patches.md`
- Wired replacement: `/tmp/pulumi-talos-fork/provider/go.mod` uses `replace github.com/pulumi/pulumi-terraform-bridge/v3 => /tmp/bridge-v3.116.0-patched`
- Four logical changes:
  - conditional timeouts handling
  - null normalization before comparison
  - better turnaround diagnostics
  - `os` import for debug file writes

### Error Messages
- `recovered raw state does not byte-for-byte match the original raw state`
- `failed recovering value for turnaround check: ...`

### Known Issue Status
Resolved in patched bridge build; evidence recorded in Task 1 file.

## Bug 2: Pre-Flight Node Detection TLS 1.3 False Positive
### Symptom
`check_node_state.py` can misclassify a running node as maintenance if it relies only on a bare TLS handshake.

### Root Cause
`ssl.CERT_NONE` handshakes can succeed on RUNNING Talos nodes because mTLS is enforced at the gRPC application layer, not at TLS transport.

### Fix Applied (with code snippet)
```py
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
...
result = subprocess.run(
    [talosctl, "get", "machinestatus", "--insecure", "--nodes", host, "--endpoints", host],
...
)
```
`talosctl get machinestatus --insecure` is now the primary maintenance-mode check; the raw TLS probe is only a fallback.

### Known Issue Status
Fixed by preferring `talosctl` insecure detection and treating cert-required failures as RUNNING.

## Bug 3: Kubernetes /readyz Returns 401 on Talos Clusters
### Symptom
`wait_for_k8s_api.py` could wait forever for `/readyz` to return 200 even though the API server was already up.

### Root Cause
Talos clusters disable anonymous auth, so `/readyz` commonly returns 401/403 while the API server is healthy.

### Fix Applied (with code snippet)
```py
resp = conn.getresponse()
return (resp.status < 500, resp.status)
```
Any HTTP status below 500 counts as ready.

### Known Issue Status
Fixed; 401/403 are now treated as proof the API server is running.

## Bug 4: TCP Port Float Type Mismatch
### Symptom
`wait_for_talos_node.py` could receive a floating-point port value from Pulumi dynamic inputs.

### Root Cause
The provider passed port values through dynamic resource inputs without normalizing the type before socket use.

### Fix Applied (with code snippet)
```py
port = int(port)
```
The helper now casts the port before TCP and TLS checks.

### Known Issue Status
Fixed; port values are normalized to integers before use.

## macOS Code Signing Discovery
### What Happened
The patched plugin binary exists at `~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` and is an arm64 Mach-O executable.

### The Fix
Run:
```bash
codesign --force --sign - --timestamp=none <binary>
```
Verification showed `Signature=adhoc`.

## Terraform Post-Install Superseded
### What Happened
`tofu plan` fails with x509 after the cluster was redeployed through Pulumi with new machine secrets.

### Why It's Expected
Terraform post-install is fully superseded by the Pulumi path; the failure is expected and not a blocker.

## Build Environment
### Versions (from actual command output)
- `go version`: `go1.26.1 darwin/arm64`
- `sw_vers`: `macOS 26.3.1` (`BuildVersion: 25D2128`)
- `pulumi version`: `v3.228.0`
- plugin dir: patched `pulumi-resource-talos` binary present
- `file`: `Mach-O 64-bit executable arm64`
- `codesign -dv`: `Signature=adhoc`
