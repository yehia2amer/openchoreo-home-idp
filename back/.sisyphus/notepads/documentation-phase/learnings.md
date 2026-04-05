# Learnings — Documentation Phase

(none yet)

- rawstate.go bridge patch set is four logical changes: conditional timeouts handling, null normalization, better turnaround diagnostics, and os import for debug writes.
- The wired bridge replacement is `replace github.com/pulumi/pulumi-terraform-bridge/v3 => /tmp/bridge-v3.116.0-patched` in `/tmp/pulumi-talos-fork/provider/go.mod`.
- Task 2 evidence extraction confirmed the Talos waiters now handle TLS-1.3/mTLS, /readyz 401s, and float ports explicitly.
- macOS Talos plugin binaries require ad-hoc signing after replacement: `codesign --force --sign - --timestamp=none <binary>`.
- The Pulumi Talos plugin binary in `~/.pulumi/plugins/resource-talos-v0.7.1/` is a Mach-O arm64 executable with `Signature=adhoc`.
- Bridge replacement is wired through `/tmp/pulumi-talos-fork/provider/go.mod` using the patched bridge path.

- Synthesized the Pulumi Talos bare-metal migration technical challenges into a comprehensive Lessons Learned document.
- Abstracted transport layer vs application layer TLS validation rules into educational documentation based on Talos's use of gRPC.
- Established a documentation pattern of separating Symptom, Root Cause, Fix, and Known Issue Status for each discovered bug to maintain clarity.

## Bridge Bug RFC Documentation
- Created a comprehensive RFC document detailing the `turnaroundCheck` bug in `pulumi-terraform-bridge`.
- The document explores three primary root causes: unconditional timeouts stripping, incorrect delta initialization for timeouts, and strict byte-for-byte JSON comparisons that are brittle to null normalization differences.
- Diffs were extracted and incorporated into the RFC cleanly, making it ready for an upstream pull request discussion.
- Ad-hoc signing of binaries on macOS (`codesign --force --sign - --timestamp=none`) is a necessary step when injecting custom-compiled local provider plugins.
