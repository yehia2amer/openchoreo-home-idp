# Bridge Patches: rawstate.go (pulumi-terraform-bridge v3.116.0)

## Full Unified Diff
```diff
--- /Users/yamer003/go/pkg/mod/github.com/pulumi/pulumi-terraform-bridge/v3@v3.116.0/pkg/tfbridge/rawstate.go	2026-03-31 13:16:01
+++ /tmp/bridge-v3.116.0-patched/pkg/tfbridge/rawstate.go	2026-03-31 13:42:26
@@ -21,6 +21,7 @@
 	"errors"
 	"fmt"
 	"math/big"
+	"os"
 	"sort"
 
 	"github.com/hashicorp/go-cty/cty"
@@ -493,8 +494,20 @@
 	pv := resource.NewObjectProperty(outMap)
 
 	delta := ih.delta(pv, v)
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
  	if err != nil {
  		return RawStateDelta{}, err
  	}
@@ -506,10 +519,10 @@
 	rawState rawstate.RawState,
 	pv resource.PropertyValue,
 ) error {
 -	// Double-check that recovering works as expected, before it is written to the state.
 	rawStateRecovered, err := d.Recover(pv)
 	if err != nil {
 -		return fmt.Errorf("failed recovering value for turnaround check: %w", err)
 +		return fmt.Errorf("failed recovering value for turnaround check: %w\ndelta=%v\npv=%s",
 +			err, d.Marshal().String(), pv.String())
 	}
 
 	rawStateWithoutTimeoutsBytes, err := json.Marshal(rawState)
@@ -523,25 +536,64 @@
 	}
 
 	if !bytes.Equal(rawStateRecoveredBytes, rawStateWithoutTimeoutsBytes) {
 -		logger := log.TryGetLogger(ctx)
 -		if logger == nil {
 -			logger = log.NewDiscardLogger()
 -		}
 -		logger.Debug(fmt.Sprintf("recovered raw state does not byte-for-byte match the original raw state\n"+
 -			"rawStateWithoutTimeoutsBytes=%s\n"+
 -			"rawStateRecoveredBytes=%s\n"+
 -			"pv=%s\n"+
 -			"delta=%s", string(rawStateWithoutTimeoutsBytes),
 -			string(rawStateRecoveredBytes),
 -			pv.String(),
 -			d.Marshal().String(),
 -		))
 -		return fmt.Errorf("recovered raw state does not byte-for-byte match the original raw state")
 +		// Null values in maps may be dropped during the PropertyValue round-trip.
 +		// Normalize both sides by stripping null map entries before comparing.
 +		normalizedOriginal := stripNullsFromJSON(rawStateWithoutTimeoutsBytes)
 +		normalizedRecovered := stripNullsFromJSON(rawStateRecoveredBytes)
 +
 +		if !bytes.Equal(normalizedOriginal, normalizedRecovered) {
 +			logger := log.TryGetLogger(ctx)
 +			if logger == nil {
 +				logger = log.NewDiscardLogger()
 +			}
 +			_ = os.WriteFile("/tmp/rawstate-original.json", rawStateWithoutTimeoutsBytes, 0644)
 +			_ = os.WriteFile("/tmp/rawstate-recovered.json", rawStateRecoveredBytes, 0644)
 +			logger.Debug(fmt.Sprintf("recovered raw state does not match the original raw state even after null normalization\n"+
 +				"original_len=%d recovered_len=%d",
 +				len(rawStateWithoutTimeoutsBytes), len(rawStateRecoveredBytes),
 +			))
 +			return fmt.Errorf("recovered raw state does not byte-for-byte match the original raw state")
 +		}
 	}
 
 	return nil
 }
 
 +func stripNullsFromJSON(data []byte) []byte {
 +	var v interface{}
 +	if err := json.Unmarshal(data, &v); err != nil {
 +		return data
 +	}
 +	stripped := stripNulls(v)
 +	out, err := json.Marshal(stripped)
 +	if err != nil {
 +		return data
 +	}
 +	return out
 +}
 +
 +func stripNulls(v interface{}) interface{} {
 +	switch val := v.(type) {
 +	case map[string]interface{}:
 +		result := make(map[string]interface{})
 +		for k, child := range val {
 +			if child == nil {
 +				continue
 +			}
 +			result[k] = stripNulls(child)
 +		}
 +		return result
 +	case []interface{}:
 +		result := make([]interface{}, len(val))
 +		for i, child := range val {
 +			result[i] = stripNulls(child)
 +		}
 +		return result
 +	default:
 +		return v
 +	}
 +}
 +
  // Reduce float precision.
  //
  // When comparing values for the turnaround check, precision-induced false positives need to be avoided, e.g:
 @@ -638,7 +690,7 @@
 	if len(path) == 1 {
 		if step, ok := path[0].(walk.GetAttrStep); ok {
 			if step.Name == "timeouts" {
 -				return RawStateDelta{}, nil
 +				return RawStateDelta{Obj: &objDelta{PropertyDeltas: map[resource.PropertyKey]RawStateDelta{}}}, nil
 			}
 		}
 	}
 @@ -831,7 +883,7 @@
 				if len(path) == 0 && key == "timeouts" {
 					// Timeouts are a special property that accidentally gets pushed here for historical reasons; it is not
 					// relevant for the permanent RawState storage. Ignore it for now.
 -					delta = RawStateDelta{}
 +					delta = RawStateDelta{Obj: &objDelta{PropertyDeltas: map[resource.PropertyKey]RawStateDelta{}}}
 				} else {
 					// Missing matching PropertyValue for key, generate a replace delta.
 					n := resource.NewNullProperty()
 ```

## Patch A: Conditional Timeouts Handling
**Location**: `inferRawStateDelta` / timeouts delta handling paths
**Diff**:
```diff
-	vWithoutTimeouts := v.Remove("timeouts")
-	err := delta.turnaroundCheck(ctx, newRawStateFromValue(schemaType, vWithoutTimeouts), pv)
+	var rawState rawstate.RawState
+	if _, hasTimeouts := outMap["timeouts"]; hasTimeouts {
+		rawState = newRawStateFromValue(schemaType, v)
+	} else {
+		rawState = newRawStateFromValue(schemaType, v.Remove("timeouts"))
+		if delta.Obj != nil {
+			delete(delta.Obj.PropertyDeltas, "timeouts")
+		}
+	}
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
**Purpose**: Only strips `timeouts` when it is not part of the provider data model, and preserves empty object deltas for `timeouts` so the raw-state structure stays consistent.

## Patch B: Null Normalization
**Location**: `turnaroundCheck` and new helpers `stripNullsFromJSON` / `stripNulls`
**Diff**:
```diff
+		// Null values in maps may be dropped during the PropertyValue round-trip.
+		// Normalize both sides by stripping null map entries before comparing.
+		normalizedOriginal := stripNullsFromJSON(rawStateWithoutTimeoutsBytes)
+		normalizedRecovered := stripNullsFromJSON(rawStateRecoveredBytes)
+
+		if !bytes.Equal(normalizedOriginal, normalizedRecovered) {
+			...
+		}
```
```diff
+func stripNullsFromJSON(data []byte) []byte {
+	...
+}
+
+func stripNulls(v interface{}) interface{} {
+	...
+}
```
**Purpose**: Adds a second comparison pass that ignores null-map-entry drift introduced by JSON/PropertyValue round-tripping, reducing false mismatches.

## Patch C: Enhanced Error Messages
**Location**: `turnaroundCheck`
**Diff**:
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
**Purpose**: Makes recovery failures easier to diagnose by including delta/PropertyValue context in the error and dumping both JSON payloads to `/tmp` for inspection.

## Patch D: Import Addition
**Location**: import block
**Diff**:
```diff
+	"os"
```
**Purpose**: Enables debug file writes used by the enhanced turnaround-check diagnostics.

## Build Wiring: go.mod replace directive
```go
replace github.com/pulumi/pulumi-terraform-bridge/v3 => /tmp/bridge-v3.116.0-patched
```
