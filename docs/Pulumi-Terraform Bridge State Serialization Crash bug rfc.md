# RFC: Fix Timeouts Handling and Null Normalization in turnaroundCheck for pulumi-terraform-bridge

## Summary
The `pulumi-terraform-bridge` experiences a critical crash during the state serialization phase, specifically within the `turnaroundCheck` validation logic, when resources are configured with explicit `timeouts` in their data model, or when empty null-mapped structures exist after round-tripping. This RFC proposes four logical patches to conditionalize timeouts handling, implement robust null normalization prior to byte-for-byte state comparison, and enhance turnaround diagnostic logging. By applying these changes, the bridge will properly serialize state even when Terraform-derived timeouts overlap with explicit data model timeouts, and when standard JSON nullification alters the payload string during `PropertyValue` translation, thereby resolving a severe bug that causes endless configuration drift in downstream providers like `pulumiverse-talos`.

## Affected Versions
The issue has been explicitly observed and isolated in the following environments and dependency trees:
- **Primary Component:** `pulumi-terraform-bridge` v3.116.0. This is the version where the bug was observed and patched. Other 3.x versions using the same `turnaroundCheck` mechanism may also be affected but have not been tested.
- **Downstream Providers:** Observed in `pulumiverse-talos` v0.7.1 (wrapping upstream Terraform provider `siderolabs/talos`). Other providers built on this bridge version that use resources with explicit timeouts in their data model may exhibit the same behavior.
- **Pulumi Engine:** Tested and reproduced under Pulumi CLI version `v3.228.0`.

## Problem Statement
When a Pulumi resource powered by the `pulumi-terraform-bridge` completes an operation successfully (like the `ConfigurationApply` resource in the Talos provider), the bridge engine attempts to serialize and verify the raw state before successfully recording it to the Pulumi backend. The verification mechanism, known as `turnaroundCheck`, re-recovers the state from the internal delta representation and compares the recovered JSON payload against the original JSON representation. This comparison is currently enforced strictly byte-for-byte.

If this byte-for-byte comparison fails, the bridge throws a fatal error and panics, outputting the following error string to the user:
```text
recovered raw state does not byte-for-byte match the original raw state
```
Additionally, a secondary log failure typically surfaces during execution, providing slight (yet often misleading) context:
```text
failed recovering value for turnaround check: ...
```

The fundamental and severe consequence of this bug is that the failure happens *after* the resource has successfully provisioned on the remote target infrastructure (e.g., a Talos node is successfully configured). Because the turnaround check fails, the bridge refuses to write the updated configuration to the Pulumi state file. Consequently, the state is never recorded. 

Every subsequent execution of the `pulumi up` command falsely believes the resource must be re-created or re-applied because it does not exist in the state file. This leads to endless configuration drift loops, where `pulumi up` always shows pending changes that are completely artificial, significantly degrading the developer experience and rendering declarative configuration workflows untrustworthy.

## Root Cause Analysis
The failure fundamentally occurs because of a mismatch in how `turnaroundCheck` expects the raw state structure to look compared to what the recovery process generates. There are three key root causes identified in the `pkg/tfbridge/rawstate.go` module, all converging to cause the aforementioned crash.

### 1. Unconditional `timeouts` Stripping
In `inferRawStateDelta` (located around line 496 in `rawstate.go` v3.116.0), the bridge code unconditionally strips the `timeouts` key from the underlying value before passing it to `turnaroundCheck`.
```go
vWithoutTimeouts := v.Remove("timeouts")
err := delta.turnaroundCheck(ctx, newRawStateFromValue(schemaType, vWithoutTimeouts), pv)
```
Historically, `timeouts` are often injected by Terraform as metadata rather than strictly being part of the user's data model. Thus, the bridge defensively strips them out to avoid polluting the core resource properties. However, if `timeouts` are genuinely part of the resource's output data model (such as an explicit property requested and defined by the provider natively, not merely a Terraform-injected side-effect), stripping them unconditionally causes a massive structural mismatch. The Pulumi `PropertyValue` map (which powers the recovered state) retains the timeouts because they are legitimate properties of the resource. Conversely, the original raw state being compared against has had them artificially removed. When `turnaroundCheck` performs the comparison, the byte payload lengths and contents diverge wildly, immediately failing the byte-for-byte equality check.

### 2. Delta Generation for `timeouts`
During the resource property tree traversal performed in `deltaAt` (approximately lines 641 and 834), when the traversal engine encounters a `timeouts` step, it abruptly returns an empty struct (`RawStateDelta{}`) rather than an initialized object delta.
```go
if len(path) == 1 {
    if step, ok := path[0].(walk.GetAttrStep); ok {
        if step.Name == "timeouts" {
            return RawStateDelta{}, nil
        }
    }
}
```
This hardcoded break in the delta traversal logic breaks structural symmetry when rebuilding the object tree during state recovery. Because an empty delta struct is returned instead of an object map with property deltas, the recovered state serialization loses track of the nested structure of the timeout fields. It must return a valid, initialized object delta (`RawStateDelta{Obj: &objDelta{...}}`) to maintain parity and ensure that the object reconstruction logic can gracefully handle the key if it exists.

### 3. Strict Byte-for-Byte Comparison without Null Normalization
In `turnaroundCheck` (around line 536), the comparison of the two serialized JSON blobs is strictly byte-for-byte without any semantic structural awareness:
```go
if !bytes.Equal(rawStateRecoveredBytes, rawStateWithoutTimeoutsBytes) {
```
During the complex round-trip from the initial raw map to a Pulumi `PropertyValue` and back to the raw state representation, empty map properties can occasionally serialize with missing keys or explicit `null` values. This slight divergence means the JSON payload strings are functionally identical from an object schema perspective but differ in their raw byte layout. A strict byte comparison is simply too brittle for this operation. It triggers false positives when semantically the structures represent the exact same outcome, forcing a fatal bridge crash on perfectly valid infrastructure applications. 

*(Note: While debugging, a secondary log message is often emitted that notes `rawStateRecoverNatural cannot process Object values due to map vs object confusion`. This is actually a red herring. The actual delta recovery path handles objects via `d.Obj` in `recoverRepr`, naturally bypassing the raw map recovery error. The true failure lies entirely within the byte-for-byte comparison of the JSON.)*

## Reproduction Steps
This issue can be reproduced reliably using the `pulumiverse-talos` provider. The following steps dictate how an upstream maintainer or QA engineer can replicate the bridge failure.

1. Prepare a fresh local development environment with Go 1.26 or greater, and Pulumi CLI `v3.228.0`.
2. Deploy a fresh Talos cluster using `pulumiverse-talos` v0.7.1. Ensure the provider binaries are correctly loaded.
3. Define a basic Pulumi stack utilizing the `talos.ConfigurationApply` resource targeting a healthy control plane or worker node. Ensure the machine configuration is well-formed.
4. Run `pulumi up`.
5. Observe the CLI output. The node will accept and apply the configuration successfully (the target machine will update its state), but the Pulumi CLI will immediately error out at the end of the execution step with `recovered raw state does not byte-for-byte match the original raw state`.
6. To prove the impact of the bug, immediately run `pulumi up` again. 
7. Observe that the `ConfigurationApply` resource attempts to run again. Pulumi has no knowledge of the previously successful run because the bridge crashed before saving the resource back to the state file.

## Proposed Fix
The proposed fix encompasses four logical, localized changes to the `pkg/tfbridge/rawstate.go` file. The changes are designed to be backward compatible while significantly enhancing the resilience of the turnaround check against serialization noise.

### Patch A: Conditional Timeouts Handling
This patch addresses the unconditional stripping of the `timeouts` property. We must only strip the `timeouts` property if it is *not* present in the provider's actual output property map. If it is part of the recognized data model, we must keep it intact so that the original state and the recovered state remain perfectly symmetrical. Furthermore, we must ensure the delta traversal objects return an initialized `objDelta` map rather than an empty struct, protecting against nil pointer crashes during delta reconstruction.

**Location**: `inferRawStateDelta` and `deltaAt`

```diff
-	vWithoutTimeouts := v.Remove("timeouts")
-	err := delta.turnaroundCheck(ctx, newRawStateFromValue(schemaType, vWithoutTimeouts), pv)
+	var rawState rawstate.RawState
+	if _, hasTimeouts := outMap["timeouts"]; hasTimeouts {
+		// if the outputs include timeouts, then they are part of the data model,
+		// and we should not remove them so that raw state matches the outputs.
+		rawState = newRawStateFromValue(schemaType, v)
+	} else {
+		// otherwise, timeouts gets injected by terraform which we then remove from the raw state
+		rawState = newRawStateFromValue(schemaType, v.Remove("timeouts"))
+		if delta.Obj != nil {
+			delete(delta.Obj.PropertyDeltas, "timeouts")
+		}
+	}
+
+	err := delta.turnaroundCheck(ctx, rawState, pv)
```

```diff
-				return RawStateDelta{}, nil
+				return RawStateDelta{Obj: &objDelta{PropertyDeltas: map[resource.PropertyKey]RawStateDelta{}}}, nil
```

```diff
-					delta = RawStateDelta{}
+					delta = RawStateDelta{Obj: &objDelta{PropertyDeltas: map[resource.PropertyKey]RawStateDelta{}}}
```

### Patch B: Null Normalization
This patch introduces semantic parity to the byte comparison. It adds a recursive pass to strip arbitrary `null` references from both the original and the recovered JSON representations before performing the final byte equality check. This completely eliminates false-positive mismatches caused by empty map properties resolving to `null` instead of being omitted entirely during `PropertyValue` translations.

**Location**: `turnaroundCheck` and bottom of `rawstate.go`

```diff
+		// Null values in maps may be dropped during the PropertyValue round-trip.
+		// Normalize both sides by stripping null map entries before comparing.
+		normalizedOriginal := stripNullsFromJSON(rawStateWithoutTimeoutsBytes)
+		normalizedRecovered := stripNullsFromJSON(rawStateRecoveredBytes)
+
+		if !bytes.Equal(normalizedOriginal, normalizedRecovered) {
```

The recursive normalization helper functions appended to the file:
```go
func stripNullsFromJSON(data []byte) []byte {
	var v interface{}
	if err := json.Unmarshal(data, &v); err != nil {
		return data
	}
	stripped := stripNulls(v)
	out, err := json.Marshal(stripped)
	if err != nil {
		return data
	}
	return out
}

func stripNulls(v interface{}) interface{} {
	switch val := v.(type) {
	case map[string]interface{}:
		result := make(map[string]interface{})
		for k, child := range val {
			if child == nil {
				continue
			}
			result[k] = stripNulls(child)
		}
		return result
	case []interface{}:
		result := make([]interface{}, len(val))
		for i, child := range val {
			result[i] = stripNulls(child)
		}
		return result
	default:
		return v
	}
}
```

### Patch C: Enhanced Error Diagnostics
This patch significantly improves the debuggability of future bridge turnaround failures. It injects deeper logging context if the turnaround check ultimately fails, outputting the exact delta string and property values directly in the error stack trace. More importantly, it writes the mismatched JSON payloads directly to the host's `/tmp` directory. This allows engineers to utilize powerful offline text diffing tools to identify exactly where the serialization pipeline broke down, saving hours of manual string inspection.

**Location**: `turnaroundCheck`

```diff
-		return fmt.Errorf("failed recovering value for turnaround check: %w", err)
+		return fmt.Errorf("failed recovering value for turnaround check: %w\ndelta=%v\npv=%s",
+			err, d.Marshal().String(), pv.String())
```

```diff
+			_ = os.WriteFile("/tmp/rawstate-original.json", rawStateWithoutTimeoutsBytes, 0644)
+			_ = os.WriteFile("/tmp/rawstate-recovered.json", rawStateRecoveredBytes, 0644)
+			logger.Debug(fmt.Sprintf("recovered raw state does not match the original raw state even after null normalization\n"+
+				"original_len=%d recovered_len=%d",
+				len(rawStateWithoutTimeoutsBytes), len(rawStateRecoveredBytes),
+			))
```

### Patch D: Import Addition
This patch simply adds the required standard library dependency to support the diagnostic file writes introduced in Patch C.

**Location**: File imports

```diff
+	"os"
```

## Workaround (Current)
Until an upstream fix is formally accepted, merged, and released within a new version of the Pulumi Terraform Bridge framework, the current workaround requires providers to compile custom, ad-hoc binaries with a manually replaced bridge module.

The procedure to inject this workaround into your provider build is as follows:

1. Clone the upstream `pulumi-terraform-bridge` repository locally. Checkout the tag corresponding to your provider's current dependency constraint (e.g., `v3.116.0`).
2. Apply the four patches outlined in the "Proposed Fix" section of this document directly to `pkg/tfbridge/rawstate.go`.
3. In your target provider's source tree, modify the `go.mod` file (typically found within the `provider/` directory of the project), adding a Go workspace replace directive pointing to your customized bridge checkout. Use a generic path syntax appropriate for your machine:
   ```go
   replace github.com/pulumi/pulumi-terraform-bridge/v3 => /path/to/your/patched/bridge
   ```
4. Resolve dependencies and build the provider locally using the project's standard Makefile routines. For most Pulumi providers, this involves running:
   ```bash
   make provider
   ```
5. **(macOS Environments Only)** Since macOS imposes strict code signing requirements on executing third-party binaries, the resulting compiled binary must be explicitly ad-hoc signed before the OS execution policies permit it to run within the Pulumi engine. Execute the following command against the installed plugin binary:
   ```bash
   codesign --force --sign - --timestamp=none ~/.pulumi/plugins/resource-<provider>-<version>/pulumi-resource-<provider>
   ```

## Testing
The proposed fix was extensively tested and validated locally by performing a full module replacement of the bridge within a customized fork of `pulumiverse/pulumi-talos`. The validation followed a strict deployment lifecycle to ensure both functionality and idempotency were successfully restored.

**Verification methodology:**
1. Built the patched bridge containing the conditional timeouts logic and the recursive null normalization routines. Wired it into the provider fork via the `go.mod` replace directive.
2. Compiled the `pulumi-resource-talos` binary, ad-hoc signed it to bypass macOS security restrictions, and installed it into the Pulumi local plugins directory.
3. Executed a full Talos bare-metal cluster deployment command (`pulumi up`) against real infrastructure.
4. Monitored the target nodes and confirmed that the `ConfigurationApply` resource successfully transmitted the configuration payload to the target nodes, resulting in successful machine reboots and configuration acceptance.
5. Observed the CLI output and confirmed that the `turnaroundCheck` execution phase no longer crashed the provider. The command concluded with a pristine success message.
6. Exported and inspected the internal stack state file. Verified that the `ConfigurationApply` resource was correctly and fully recorded to the JSON state file, retaining all expected property values and timeout metadata.
7. Re-ran `pulumi up` on the identical stack without modifying any code. Verified that zero operational drift occurred. The provider properly read the state file, evaluated the inputs against the live cluster state, and reported that no changes were required, conclusively proving the fix resolves the endless drift loop.

## Impact Assessment
This bug was observed in the `pulumiverse-talos` provider but the root causes — unconditional timeouts stripping, null value dropping during round-trip, and incorrect delta initialization — exist in the shared bridge code. Other providers built on `pulumi-terraform-bridge` that use resources with explicit `timeouts` in their data model or complex nested state may encounter the same crash.

The recursive null normalization ensures that discrepancies in how map properties are marshaled during round-tripping no longer register as fatal mismatches. By conditionalizing the timeouts stripping logic, providers that define `timeouts` in their schema can serialize state without triggering the crash. This eliminates false positives when resources return structurally valid state that differs only in null representation or timeouts metadata.

## References
For deeper architectural context on the Pulumi Terraform Bridge and the specific provider where this issue was isolated, please consult the following repositories:

- `pulumi-terraform-bridge` Repository: https://github.com/pulumi/pulumi-terraform-bridge
- `pulumiverse-talos` Repository: https://github.com/pulumiverse/pulumi-talos
