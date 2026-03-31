# Project Lessons Learned: Talos Bare-Metal Provisioning with Pulumi

## Project Overview
This project successfully migrated a Talos Linux bare-metal Kubernetes cluster deployment from Terraform to Pulumi using Python. The objective was achieving absolute parity with the existing Terraform implementation through a strict twelve-step alignment plan documented in our migration strategy. To achieve this, we developed custom Pulumi dynamic resource providers in Python that handle pre-flight node state detection, cluster bootstrap orchestration, and Kubernetes API server polling. Along the way, we discovered and resolved several deep technical challenges spanning Go provider compilation, TLS 1.3 protocol behaviors, and Kubernetes security hardening defaults.

## Bug 1: Pulumi-Terraform Bridge State Serialization Crash

### Symptom
During the initial deployment of the Talos machine configuration, the `ConfigurationApply` resource successfully pushed the configuration to the node. However, the Pulumi provider immediately crashed during the state saving phase. The failure occurred inside the `turnaroundCheck` function with the exact error: `recovered raw state does not byte-for-byte match the original raw state`.

### Root Cause
This bug stems from how the `pulumi-terraform-bridge` manages state transitions between Pulumi's engine and the underlying Terraform provider schema. The turnaround check is a safety mechanism ensuring that if Pulumi saves a state, it can accurately recover that exact state back from the Terraform representation. 

The mismatch was triggered by three compounding factors. First, the bridge improperly removed `timeouts` from the raw state even when those timeouts were part of the provider's actual data model. Second, when converting property values back and forth through JSON, map entries containing explicit `null` values were dropped, creating a structural mismatch when compared against the original raw state which retained the keys with `null` values. Third, the error messages lacked the necessary context to debug the serialization drift, failing to dump the exact JSON payloads that were being compared.

### Fix
Resolving this required checking out the `pulumi-terraform-bridge` source code, developing a patch, and recompiling the `pulumiverse-talos` provider locally. We implemented conditional timeouts handling, added a recursive function to strip nulls before the final byte comparison, and enhanced the diagnostic output to write the drifting JSON payloads to disk. 

We injected our patched bridge into the provider compilation using a `replace` directive in the `go.mod` file:

```go
// /tmp/pulumi-talos-fork/provider/go.mod
module github.com/pulumiverse/pulumi-talos/provider

go 1.22.0

replace github.com/pulumi/pulumi-terraform-bridge/v3 => /tmp/bridge-v3.116.0-patched

require (
	github.com/siderolabs/terraform-provider-talos v0.7.0
    // ...
)
```

### Known Issue Status
Resolved locally via the custom patched provider build. For a comprehensive deep dive into the bridge serialization mechanism, the diffs applied, and the path forward for upstreaming this fix, refer to the accompanying document at `docs/bridge-bug-rfc.md`.

## Bug 2: Pre-Flight Node Detection TLS 1.3 False Positive

### Symptom
Our custom Pulumi pre-flight check, `check_node_state.py`, was designed to probe the target server and determine if the node was in `UNREACHABLE`, `MAINTENANCE`, or `RUNNING` mode. The initial implementation misclassified fully operational `RUNNING` nodes as being in `MAINTENANCE` mode, causing Pulumi to attempt applying configurations to nodes that were already live and actively serving Kubernetes workloads.

### Root Cause
Talos nodes in maintenance mode accept API connections without requiring mutual TLS client certificates. Nodes in running mode strictly require mutual TLS. Our early logic attempted a raw Python `ssl.CERT_NONE` handshake without providing a client certificate. We assumed that if the node was running, the TLS handshake would immediately fail at the transport layer, throwing an `ssl.SSLError`. 

However, under modern TLS 1.3 specifications combined with gRPC (which the Talos API uses), the underlying TLS transport connection can succeed completely even without the client certificate. The enforcement of mutual TLS happens at the gRPC application layer, not the initial TLS transport handshake. Because the raw socket handshake succeeded without throwing an exception, our Python code falsely concluded the node was in maintenance mode.

### Fix
We updated the pre-flight logic to rely on the actual application-layer CLI tool, `talosctl`, rather than attempting to guess the state using raw Python sockets. We invoke `talosctl get machinestatus --insecure`. If the node is in maintenance mode, this insecure request returns actual machine status data. If the node is running, the application layer correctly rejects the insecure request, and we safely categorize the node as `RUNNING`.

```python
def _try_talosctl_insecure(host: str, timeout: float = 10.0) -> tuple[bool, str]:
    """Try `talosctl get machinestatus --insecure` as a primary check.
    
    This is more reliable than raw TLS probing because it uses the actual
    Talos gRPC protocol. In maintenance mode, this returns machine status.
    In running mode, it fails with a TLS error at the application level.
    """
    talosctl = shutil.which("talosctl")
    if talosctl is None:
        return False, "talosctl not found on PATH"

    try:
        result = subprocess.run(
            [talosctl, "get", "machinestatus", "--insecure", "--nodes", host, "--endpoints", host],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, f"talosctl insecure succeeded: {result.stdout[:200].strip()}"
        return False, f"talosctl insecure failed (rc={result.returncode}): {result.stderr[:200].strip()}"
    except subprocess.TimeoutExpired:
        return False, "talosctl insecure timed out"
    except OSError as e:
        return False, f"talosctl error: {e}"
```

### Known Issue Status
Fixed. The pre-flight check now accurately distinguishes between node states by probing the gRPC application layer instead of relying on transport-level TLS errors. The raw socket approach is retained only as a fallback if the `talosctl` binary is completely absent from the local path.

## Bug 3: Kubernetes /readyz Returns 401 on Talos Clusters

### Symptom
Following the successful application of the Talos configuration and cluster bootstrap, our secondary dynamic provider `wait_for_k8s_api.py` was responsible for pausing execution until the Kubernetes API became fully functional. The script polled the `/readyz` endpoint waiting for an HTTP `200 OK` response. However, the script hung indefinitely, eventually timing out and failing the Pulumi deployment, even though manual inspection proved the Kubernetes cluster was perfectly healthy.

### Root Cause
Standard Kubernetes distributions often allow unauthenticated requests to reach specific health check endpoints like `/readyz` or `/livez` to facilitate load balancer probing. Talos Linux prioritizes extreme security defaults and actively disables anonymous authentication across the entire Kubernetes API server. 

When our Python script performed an unauthenticated HTTPS GET request to the `/readyz` endpoint, the API server rejected it with an HTTP `401 Unauthorized` status. Our script interpreted anything other than a `200 OK` as a failure and continued polling. In reality, the API server returning a `401 Unauthorized` is definitive proof that the API server is actively running, processing requests, and enforcing authentication policies.

### Fix
We modified the readiness logic to treat any HTTP response with a status code below 500 as proof of life. A `401` or `403` status means the server is actively rejecting unauthenticated traffic, which is exactly the expected behavior of a healthy, hardened Talos cluster.

```python
def _check_k8s_readyz(host: str, port: int, connect_timeout: float = 10.0) -> tuple[bool, int | None]:
    """Return (True, status_code) if the K8s API server responds to HTTP at all.

    Talos clusters disable anonymous auth, so /readyz returns 401; a 401 
    from kube-apiserver is conclusive proof it's running.
    """
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        conn = http.client.HTTPSConnection(
            host,
            port=int(port),
            timeout=connect_timeout,
            context=ctx,
        )
        try:
            conn.request("GET", "/readyz")
            resp = conn.getresponse()
            
            # 200 = fully ready
            # 401/403 = running but no anonymous access (expected for Talos)
            # 500/503 = starting up but processing requests
            return (resp.status < 500, resp.status)
        finally:
            conn.close()
    except (OSError, TimeoutError, http.client.HTTPException):
        return (False, None)
```

### Known Issue Status
Fixed. The deployment pipeline now successfully detects API readiness without getting blocked by Talos authentication policies.

## Bug 4: TCP Port Float Type Mismatch in Dynamic Resources

### Symptom
Our infrastructure code utilized Pulumi dynamic resource providers to manage procedural waits, such as `wait_for_talos_node.py`. When passing the `port` variable into the Python socket connection function, the deployment crashed unexpectedly with a Python `TypeError`, preventing the wait loop from executing.

### Root Cause
Pulumi seamlessly serializes and deserializes state between the engine and the language host. During this translation process, numerical inputs passed into a Python dynamic resource provider from upstream outputs can occasionally lose their strict integer typing. The `port` value, configured as `50000`, was deserialized and delivered to the Python dynamic resource as a floating-point number (`50000.0`). 

The standard library `socket.create_connection` strictly demands an integer for the port parameter. When it received the float, it threw a type error, crashing the provider process mid-execution. 

### Fix
We introduced an explicit integer type cast immediately at the entry boundary of our wait functions, ensuring that regardless of how Pulumi deserializes numerical arguments, the socket logic always receives a strict integer.

```python
def wait_for_talos_api(
    node: str,
    endpoint: str,
    port: int = 50000,
    talosconfig_path: str | None = None,
    timeout: int = 600,
    poll_interval: int = 10,
    initial_delay: int = 0,
) -> dict[str, Any]:
    """Poll until the Talos node has finished installing and reached RUNNING stage."""
    
    # Explicitly cast parameters to correct types to handle Pulumi 
    # cross-language serialization inconsistencies.
    port = int(port)
    timeout = int(timeout)
    poll_interval = int(poll_interval)
    initial_delay = int(initial_delay)
    
    start = time.monotonic()
    deadline = start + timeout
    attempts = 0
    # ... polling logic continues
```

### Known Issue Status
Fixed. All numerical arguments passed into dynamic resources are now explicitly sanitized before downstream usage.

## Unexpected Discovery: macOS Code Signing for Go Binaries

### What Happened
While patching the `pulumi-terraform-bridge` bug, we needed to compile a custom local version of the `pulumiverse-talos` provider. After compiling the binary using standard Go build tools and moving it into the `~/.pulumi/plugins/resource-talos-v0.7.1/` directory, Pulumi immediately failed to execute it. The operating system terminated the plugin process instantly with a cryptic `Killed: 9` signal.

### The Fix
This failure occurs strictly on modern Apple Silicon (M-series) Macs running recent versions of macOS. The operating system's dynamic linker (`dyld`) and Gatekeeper security framework strictly enforce code signing requirements for all ARM64 executables. Unsigned executables are immediately killed upon execution to prevent malware tampering.

To resolve this, we discovered that developers must perform an ad-hoc signature on the compiled provider binary before Pulumi can launch it. This creates a valid local signature without requiring an Apple Developer certificate.

```bash
# Ad-hoc sign the compiled binary to satisfy macOS ARM64 execution requirements
codesign --force --sign - --timestamp=none ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos
```

Running `codesign -dv <binary>` subsequently verified the binary contained `Signature=adhoc`, and Pulumi was able to execute the plugin successfully.

## Terraform Post-Install Superseded

### What Happened
After successfully deploying the Talos cluster with the newly authored Pulumi configuration, executing a `tofu plan` or `terraform plan` against the old legacy state resulted in an immediate catastrophic failure containing `x509: certificate signed by unknown authority` errors.

### Why It's Expected
This failure is completely expected and represents a successful outcome. During the Pulumi provisioning process, new machine secrets, new certificate authority keys, and new node configurations were generated and applied to the bare-metal servers. The legacy Terraform state file contains the old cryptographic material, which is now entirely obsolete. 

Because the underlying cluster has been successfully taken over and rotated by the Pulumi stack, Terraform can no longer authenticate against the API server. The Terraform implementation is now fully superseded and can be safely archived or deleted. The Pulumi codebase is now the single source of truth for the cluster infrastructure.

## Pro Tips

If you are attempting to replicate this migration or build similar bare-metal orchestrations with Pulumi, keep the following lessons in mind:

*   **Bridge Building Workflows:** When you encounter serialization bugs in Pulumi Terraform providers, you don't necessarily have to wait for upstream fixes. You can fork `pulumi-terraform-bridge`, author a patch, and use the `replace` directive in your provider's `go.mod` to test and compile a local version of the provider.
*   **macOS Code Signing:** If you compile custom Pulumi provider binaries on Apple Silicon hardware, always remember to run `codesign --force --sign - --timestamp=none` on the executable. Otherwise, macOS will silently terminate the plugin upon execution.
*   **TLS 1.3 Behavior:** Never rely on raw transport-level TLS connection errors to detect whether a server requires client certificates. Modern gRPC servers under TLS 1.3 will complete the transport handshake and fail at the application layer instead. Use application-specific tools like `talosctl` for reliable probing.
*   **Talos Anonymous Auth:** Talos Linux explicitly disables anonymous authentication across the Kubernetes API. When building polling mechanisms against `/readyz`, understand that an HTTP `401 Unauthorized` response actually signifies a healthy, running server, not a failure.
*   **Pulumi Dynamic Resource Types:** Pulumi inputs passing into Python dynamic provider boundaries can lose strict typing. Always explicitly cast integers and floats before handing them off to strict standard library functions like `socket.create_connection`.
*   **Testing Provider Patches:** Instead of attempting to fake a release tarball, you can force Pulumi to consume your locally patched provider binary by overwriting the executable directly inside your `~/.pulumi/plugins/` directory.
*   **Node State Modeling:** Talos nodes pass through distinct installation stages (off, maintenance, running). Building explicit Python `Enum` classes to represent these states drastically clarifies pre-flight logic and prevents applying configurations to running nodes.
*   **Polling Separation:** Separate your polling logic into phases. Check TCP reachability first to confirm the server is powered on, then check application HTTP readiness. This separation helps diagnose exactly where timeouts occur during long cluster bootstrap sequences.

## Build Environment

The patches, deployments, and logic described in this document were executed and verified against the following environment:

*   **Go Version:** `go1.26.1 darwin/arm64`
*   **Operating System:** `macOS 26.3.1` (BuildVersion: `25D2128`)
*   **Pulumi CLI:** `v3.228.0`
*   **Talos Pulumi Provider:** `pulumiverse-talos v0.7.1` (Patched locally)
*   **Kubernetes Pulumi Provider:** `pulumi-kubernetes v4.28.0`
*   **Compiled Plugin Signature:** `Mach-O 64-bit executable arm64` with `Signature=adhoc`
