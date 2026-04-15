#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# iam-setup.sh — Manual IAM prerequisite bindings for OpenChoreo GKE
# ──────────────────────────────────────────────────────────────────────────────
# Run this script ONCE as a project admin (requires setIamPolicy permissions)
# BEFORE running `pulumi up`.  It creates the 4 IAM bindings that Pulumi
# cannot create when the deployer lacks setIamPolicy.
#
# After running this, set `openchoreo:skip_iam_bindings: "true"` in
# Pulumi.<stack>.yaml (already the default for gcp stack).
#
# Usage:
#   chmod +x prereqs/iam-setup.sh
#   ./prereqs/iam-setup.sh
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration (update these to match your Pulumi config) ─────────────────
PROJECT_ID="${GCP_PROJECT_ID:-pg-ae-n-app-173978}"
REGION="${GCP_REGION:-europe-west1}"
ESO_GSA_NAME="${ESO_GSA_NAME:-openchoreo-eso}"
CAS_GSA_NAME="${CAS_GSA_NAME:-openchoreo-cas}"
CAS_POOL_NAME="${CAS_POOL_NAME:-openchoreo-ca-pool}"

# Derived values
ESO_GSA_EMAIL="${ESO_GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
CAS_GSA_EMAIL="${CAS_GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  OpenChoreo GKE — IAM Prerequisite Setup                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Project:   ${PROJECT_ID}"
echo "Region:    ${REGION}"
echo "ESO GSA:   ${ESO_GSA_EMAIL}"
echo "CAS GSA:   ${CAS_GSA_EMAIL}"
echo "CAS Pool:  ${CAS_POOL_NAME}"
echo ""

# ── 1. ESO service account → Secret Manager accessor (project-level) ────────
echo "→ [1/4] Granting ESO SA access to Secret Manager..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${ESO_GSA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None \
    --quiet

# ── 2. ESO Workload Identity binding ────────────────────────────────────────
echo "→ [2/4] Binding ESO K8s SA to GCP SA via Workload Identity..."
gcloud iam service-accounts add-iam-policy-binding "${ESO_GSA_EMAIL}" \
    --project="${PROJECT_ID}" \
    --member="serviceAccount:${PROJECT_ID}.svc.id.goog[external-secrets/external-secrets]" \
    --role="roles/iam.workloadIdentityUser" \
    --quiet

# ── 3. CAS Workload Identity binding ────────────────────────────────────────
echo "→ [3/4] Binding CAS K8s SA to GCP SA via Workload Identity..."
gcloud iam service-accounts add-iam-policy-binding "${CAS_GSA_EMAIL}" \
    --project="${PROJECT_ID}" \
    --member="serviceAccount:${PROJECT_ID}.svc.id.goog[cert-manager/google-cas-issuer]" \
    --role="roles/iam.workloadIdentityUser" \
    --quiet

# ── 4. CAS SA → Certificate Requester on CA Pool ────────────────────────────
echo "→ [4/4] Granting CAS SA certificate requester on CA pool..."
gcloud privateca pools add-iam-policy-binding "${CAS_POOL_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --member="serviceAccount:${CAS_GSA_EMAIL}" \
    --role="roles/privateca.certificateRequester" \
    --quiet

echo ""
echo "✅ All 4 IAM bindings created successfully."
echo "   You can now run: pulumi up -s gcp"
