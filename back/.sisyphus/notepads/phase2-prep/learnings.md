## Initial Setup
- Plan: phase2-prep
- Session: ses_2bef023c3ffe97xLB8JKcwC8Kh
- Started: 2026-03-31T20:14:52Z

## Pulumi VolumeSnapshotClass fix
- Use `k8s.yaml.v2.ConfigGroup` with inline `yaml=` for VolumeSnapshotClass so top-level fields stay at the document root.
- `k8s.apiextensions.CustomResource` with `spec=` nests `driver`, `deletionPolicy`, and `parameters` incorrectly under `spec`.
