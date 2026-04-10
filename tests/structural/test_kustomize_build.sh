#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <gitops-repo-path>"
  exit 2
fi

GITOPS_REPO="${1%/}"
INFRA_DIR="${GITOPS_REPO}/infrastructure"
PLATFORMS_DIR="${INFRA_DIR}/platforms"
COMPONENTS_DIR="${INFRA_DIR}/components"

if [[ ! -d "${PLATFORMS_DIR}" ]]; then
  echo "FAIL: platforms directory not found: ${PLATFORMS_DIR}"
  exit 1
fi

if [[ ! -d "${COMPONENTS_DIR}" ]]; then
  echo "FAIL: components directory not found: ${COMPONENTS_DIR}"
  exit 1
fi

PASS_COUNT=0
FAIL_COUNT=0
RESOURCE_REPORT=()

pass() {
  echo "PASS: $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
  echo "FAIL: $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

section() {
  echo
  echo "== $1 =="
}

resource_count() {
  local file="$1"
  awk '
    /^[[:space:]]*kind:[[:space:]]*/ {
      if ($0 !~ /^[[:space:]]*kind:[[:space:]]*Kustomization[[:space:]]*$/ &&
          $0 !~ /^[[:space:]]*kind:[[:space:]]*Component[[:space:]]*$/) {
        count++
      }
    }
    END { print count + 0 }
  ' "${file}"
}

resource_keys() {
  local file="$1"
  awk '
    function trim(value) {
      sub(/^[[:space:]]+/, "", value)
      sub(/[[:space:]]+$/, "", value)
      return value
    }
    function flush() {
      if (kind != "" && name != "") {
        print kind "|" name "|" namespace
      }
      kind = ""
      name = ""
      namespace = ""
      in_metadata = 0
    }
    /^---[[:space:]]*$/ { flush(); next }
    /^[^[:space:]]/ {
      if ($0 ~ /^kind:[[:space:]]*/) {
        kind = trim(substr($0, index($0, ":") + 1))
      }
      if ($0 ~ /^metadata:[[:space:]]*$/) {
        in_metadata = 1
        next
      }
      in_metadata = 0
      next
    }
    in_metadata && /^[[:space:]]{2}name:[[:space:]]*/ {
      name = trim(substr($0, index($0, ":") + 1))
      next
    }
    in_metadata && /^[[:space:]]{2}namespace:[[:space:]]*/ {
      namespace = trim(substr($0, index($0, ":") + 1))
      next
    }
    END { flush() }
  ' "${file}"
}

discover_dirs() {
  local parent="$1"
  local -n result_ref="$2"

  mapfile -t result_ref < <(
    for dir in "${parent}"/*; do
      [[ -d "${dir}" ]] || continue
      printf '%s\n' "${dir}"
    done | sort
  )
}

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

PLATFORMS=()
COMPONENTS=()
discover_dirs "${PLATFORMS_DIR}" PLATFORMS
discover_dirs "${COMPONENTS_DIR}" COMPONENTS

if [[ ${#PLATFORMS[@]} -eq 0 ]]; then
  echo "FAIL: no platform overlays found under ${PLATFORMS_DIR}"
  exit 1
fi

if [[ ${#COMPONENTS[@]} -eq 0 ]]; then
  echo "FAIL: no components found under ${COMPONENTS_DIR}"
  exit 1
fi

section "Platform overlay builds"
for platform_dir in "${PLATFORMS[@]}"; do
  platform_name="$(basename "${platform_dir}")"
  output_file="${TMP_DIR}/${platform_name}.yaml"

  if kustomize build "${platform_dir}" >"${output_file}" 2>"${TMP_DIR}/${platform_name}.err"; then
    pass "platform ${platform_name} builds"
  else
    fail "platform ${platform_name} builds"
    cat "${TMP_DIR}/${platform_name}.err"
    continue
  fi

  count="$(resource_count "${output_file}")"
  RESOURCE_REPORT+=("${platform_name}:${count}")
  pass "platform ${platform_name} resource count = ${count}"

  baseline_file="/tmp/baseline-${platform_name}.yaml"
  if [[ -f "${baseline_file}" ]]; then
    if diff -u "${baseline_file}" "${output_file}" >"${TMP_DIR}/${platform_name}.baseline.diff"; then
      pass "platform ${platform_name} matches baseline ${baseline_file}"
    else
      fail "platform ${platform_name} differs from baseline ${baseline_file}"
      cat "${TMP_DIR}/${platform_name}.baseline.diff"
    fi
  else
    echo "INFO: baseline not found for ${platform_name}: ${baseline_file}"
  fi

  duplicates="$(resource_keys "${output_file}" | sort | uniq -d || true)"
  if [[ -z "${duplicates}" ]]; then
    pass "platform ${platform_name} has no duplicate kind+name+namespace resources"
  else
    fail "platform ${platform_name} has duplicate kind+name+namespace resources"
    printf '%s\n' "${duplicates}"
  fi
done

section "Component builds"
for component_dir in "${COMPONENTS[@]}"; do
  component_name="$(basename "${component_dir}")"
  kustomization_file=""

  if [[ -f "${component_dir}/kustomization.yaml" ]]; then
    kustomization_file="${component_dir}/kustomization.yaml"
  elif [[ -f "${component_dir}/kustomization.yml" ]]; then
    kustomization_file="${component_dir}/kustomization.yml"
  fi

  if [[ -z "${kustomization_file}" ]]; then
    echo "INFO: skipping component ${component_name}; no kustomization file"
    continue
  fi

  if kustomize build "${component_dir}" >"${TMP_DIR}/component-${component_name}.yaml" 2>"${TMP_DIR}/component-${component_name}.err"; then
    pass "component ${component_name} builds independently"
  else
    fail "component ${component_name} builds independently"
    cat "${TMP_DIR}/component-${component_name}.err"
  fi
done

section "Summary"
for report in "${RESOURCE_REPORT[@]}"; do
  platform_name="${report%%:*}"
  count="${report#*:}"
  echo "INFO: platform ${platform_name} produced ${count} resources"
done

echo "INFO: pass count = ${PASS_COUNT}"
echo "INFO: fail count = ${FAIL_COUNT}"

if [[ ${FAIL_COUNT} -eq 0 ]]; then
  echo "PASS: all structural kustomize checks passed"
  exit 0
fi

echo "FAIL: structural kustomize checks failed"
exit 1
