#!/bin/bash
#
# Exercises DEPLOYMENT.sh against an isolated temp copy of
# S3_Bucket_processing/info/s3_folder_mask_aws-key.info, using fake,
# non-secret input only. Never touches the real AWS_KEY/.env-EMSERVICEUSER file.
#
# Run from the repo root:
#   bash tests/test_DEPLOYMENT.sh

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0

run_case() {
    local name="$1"
    if "$2"; then
        echo "PASS: ${name}"
    else
        echo "FAIL: ${name}"
        failures=$((failures + 1))
    fi
}

case_fresh_create() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "${tmpdir}/AWS_KEY" "${tmpdir}/S3_Bucket_processing/info"
    cp "${repo_root}/S3_Bucket_processing/info/s3_folder_mask_aws-key.info" "${tmpdir}/S3_Bucket_processing/info/s3_folder_mask_aws-key.info"
    cp "${repo_root}/DEPLOYMENT.sh" "${tmpdir}/DEPLOYMENT.sh"

    printf 'FAKEID123\nFAKESECRET456\n' | DEPLOYMENT_SKIP_S3_CHECK=1 bash "${tmpdir}/DEPLOYMENT.sh" > /dev/null

    local ok=1
    if [[ -f "${tmpdir}/AWS_KEY/.env-EMSERVICEUSER" ]]; then
        grep -q '^export AWS_KEY_1=FAKEID123$' "${tmpdir}/AWS_KEY/.env-EMSERVICEUSER" || ok=0
        grep -q '^export AWS_KEY_VALUES_1=FAKESECRET456$' "${tmpdir}/AWS_KEY/.env-EMSERVICEUSER" || ok=0
    else
        ok=0
    fi

    rm -rf "${tmpdir}"
    [[ "${ok}" == "1" ]]
}

case_declines_overwrite() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "${tmpdir}/AWS_KEY" "${tmpdir}/S3_Bucket_processing/info"
    cp "${repo_root}/S3_Bucket_processing/info/s3_folder_mask_aws-key.info" "${tmpdir}/S3_Bucket_processing/info/s3_folder_mask_aws-key.info"
    cp "${repo_root}/DEPLOYMENT.sh" "${tmpdir}/DEPLOYMENT.sh"
    echo "export EXISTING=1" > "${tmpdir}/AWS_KEY/.env-EMSERVICEUSER"

    printf 'n\n' | DEPLOYMENT_SKIP_S3_CHECK=1 bash "${tmpdir}/DEPLOYMENT.sh" > /dev/null

    local ok=1
    grep -q '^export EXISTING=1$' "${tmpdir}/AWS_KEY/.env-EMSERVICEUSER" || ok=0

    rm -rf "${tmpdir}"
    [[ "${ok}" == "1" ]]
}

run_case "fresh_create_writes_env_file" case_fresh_create
run_case "declines_overwrite_leaves_existing_env_file" case_declines_overwrite

if [[ "${failures}" -gt 0 ]]; then
    exit 1
fi
echo "ALL TESTS PASSED"
