#!/bin/bash
#
# Run this once after cloning/deploying this repo to production, before any
# S3_Bucket_processing-<NAME>.sh wrapper is run.
#
# S3_Bucket_processing/info/s3_folder_mask_aws-key.info only stores
# environment-variable NAMES (e.g. $AWS_KEY_1 / $AWS_KEY_VALUES_1), never the
# real AWS credentials, so it's safe in git. The real values must be exported
# from AWS_KEY/.env-EMSERVICEUSER, which is gitignored and does not exist after a
# fresh clone. This script creates it by asking the deployer for the real AWS
# access key id / secret access key for each bucket|folder|file_mask
# combination listed in s3_folder_mask_aws-key.info, then verifies boto3 can
# actually reach each bucket/folder with those credentials.
#
# Python deps are managed with uv (pyproject.toml/uv.lock) - `uv sync` creates
# ${venv_dir}/ and installs the pinned deps into it.
#
# DEPLOYMENT_SKIP_S3_CHECK=1 skips the uv sync step, the live S3
# verification, and the sas01_sasdata_PROD_S3_Bucket_processing symlink
# check/creation (credential collection still runs) - used by
# tests/test_DEPLOYMENT.sh so it never makes real network/AWS calls or
# needs an interactive prompt for a machine-specific symlink.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
key_file="${script_dir}/S3_Bucket_processing/info/s3_folder_mask_aws-key.info"
env_file="${script_dir}/AWS_KEY/.env-EMSERVICEUSER"
venv_dir="${script_dir}/.venv"
venv_python="${venv_dir}/bin/python"
skip_s3_check="${DEPLOYMENT_SKIP_S3_CHECK:-0}"

if [[ ! -f "${key_file}" ]]; then
    echo "ERROR: ${key_file} not found. Nothing to deploy against."
    exit 1
fi

# --------------------------------------------------------------------------------
# -- .venv + deps: uv sync creates ${venv_dir} (if missing) and installs the
# -- exact versions pinned in pyproject.toml/uv.lock.
# --------------------------------------------------------------------------------
if [[ "${skip_s3_check}" -eq 1 ]]; then
    echo "-"
    echo "DEPLOYMENT_SKIP_S3_CHECK=1: skipping .venv/boto3 setup and S3 verification."
else
    echo "-"
    echo "Running uv sync..."
    (cd "${script_dir}" && uv sync)
fi

# --------------------------------------------------------------------------------
# -- Real SAS executable detection: a real SAS license is too expensive to have
# -- in a dev environment, so COMMON/z_config.py's sas_bin defaults to
# -- FAKE-SAS-BIN.sh. If a real `sas` binary IS available on this machine (e.g.
# -- this is actually being deployed to the real SAS server), point sas_bin at
# -- it instead - this makes DEPLOYMENT.sh safe to (re-)run in either
# -- environment without a manual edit.
# --------------------------------------------------------------------------------
z_config_file="${script_dir}/COMMON/z_config.py"

if [[ -f "${z_config_file}" ]]; then
    real_sas_bin=""
    for candidate in \
        "$(command -v sas 2>/dev/null || true)" \
        "/sas/sasbin94/sashome/SASFoundation/9.4/sasexe/sas" \
        "/sas/sasbin94/sashome/SASFoundation/9.4/sas"; do
        if [[ -n "${candidate}" && -x "${candidate}" ]]; then
            real_sas_bin="${candidate}"
            break
        fi
    done

    echo "-"
    if [[ -n "${real_sas_bin}" ]]; then
        echo "Real SAS executable found at ${real_sas_bin} - pointing sas_bin at it."
        sed -i "s|^sas_bin = .*|sas_bin = '${real_sas_bin}'|" "${z_config_file}"
    else
        echo "No real SAS executable found on this machine - sas_bin stays on FAKE-SAS-BIN.sh."
        sed -i "s|^sas_bin = .*|sas_bin = '../FAKE-SAS-BIN.sh'|" "${z_config_file}"
    fi
else
    echo "-"
    echo "WARNING: ${z_config_file} not found - skipping SAS-executable detection."
fi

# --------------------------------------------------------------------------------
# -- sas01_sasdata_PROD_S3_Bucket_processing: a repo-root symlink standing in for
# -- the real SAS server's /sas01/sasdata/PROD/S3_Bucket_processing directory
# -- (see COMMON/z_config.py's f_get_prog_config('S3_Bucket_processing')
# -- ['path_to_logfile']/['path_to_sasfile']). Machine-specific and gitignored, so it must be
# -- (re-)created on each machine this is deployed to. Skipped under
# -- DEPLOYMENT_SKIP_S3_CHECK=1 since it needs an interactive prompt when
# -- missing/broken, which tests/test_DEPLOYMENT.sh's isolated tmpdir runs
# -- can't supply.
# --------------------------------------------------------------------------------
if [[ "${skip_s3_check}" -eq 1 ]]; then
    echo "-"
    echo "DEPLOYMENT_SKIP_S3_CHECK=1: skipping sas01_sasdata_PROD_S3_Bucket_processing link check."
else
    sas_data_link="${script_dir}/sas01_sasdata_PROD_S3_Bucket_processing"

    if [[ -L "${sas_data_link}" && -d "${sas_data_link}" ]]; then
        echo "-"
        echo "${sas_data_link} -> $(readlink "${sas_data_link}") (OK)."
    else
        echo "-"
        if [[ -L "${sas_data_link}" ]]; then
            echo "${sas_data_link} is a symlink but its target ($(readlink "${sas_data_link}")) does not exist or is not a directory."
        elif [[ -e "${sas_data_link}" ]]; then
            echo "WARNING: ${sas_data_link} exists but is not a symlink - leaving it as-is."
        else
            echo "${sas_data_link} does not exist."
        fi

        if [[ ! -e "${sas_data_link}" || -L "${sas_data_link}" ]]; then
            echo "This must point at the real directory that emulates/is the SAS-server PROD"
            echo "data dir for S3_Bucket_processing (containing 'log/' and 'source/' subfolders)."
            read -r -p "Enter the real directory to link it to: " sas_data_target
            if [[ -z "${sas_data_target}" || ! -d "${sas_data_target}" ]]; then
                echo "ERROR: (${sas_data_target}) is not an existing directory. Aborting."
                exit 1
            fi
            rm -f "${sas_data_link}"
            ln -s "${sas_data_target}" "${sas_data_link}"
            echo "Created ${sas_data_link} -> ${sas_data_target}"
        fi
    fi
fi

write_credentials=1

if [[ -f "${env_file}" ]]; then
    echo "-"
    echo "${env_file} already exists."
    echo "This file holds the real AWS Access Key ID / Secret Access Key that the"
    echo "S3_Bucket_processing-<NAME>.sh wrapper sources at runtime."
    echo ""
    echo "Answer 'y' ONLY if you want to replace those credentials with new ones you"
    echo "are about to type in (for example: rotating a leaked/expiring AWS key, or"
    echo "fixing a value that was entered wrong last time)."
    echo ""
    echo "Answer 'N' (default) to leave the existing credentials as they are and just"
    echo "re-verify S3 access - this is what you want if the job is already deployed"
    echo "and working."
    echo "-"
    read -r -p "Overwrite ${env_file}? [y/N] " overwrite_answer
    if [[ ! "${overwrite_answer}" =~ ^[Yy]$ ]]; then
        echo "Leaving ${env_file} untouched."
        write_credentials=0
    fi
fi

if [[ "${write_credentials}" -eq 1 ]]; then
    echo "-"
    echo "Setting up AWS credentials for: ${key_file}"
    echo "-"

    env_lines=()

    while IFS='|' read -r bucket folder file_mask key_name_var key_value_var <&3; do
        [[ -z "${bucket}" ]] && continue

        if [[ "${key_name_var}" != \$* || "${key_value_var}" != \$* ]]; then
            echo "WARNING: skipping line for bucket=(${bucket}) folder=(${folder}) mask=(${file_mask}) - fields 4/5 are not \$VAR references."
            continue
        fi

        key_name_var="${key_name_var#\$}"
        key_value_var="${key_value_var#\$}"

        echo "-"
        echo "Combination: bucket=(${bucket}) folder=(${folder}) file_mask=(${file_mask})"
        read -r -p "  AWS Access Key ID for \$${key_name_var}: " access_key_id
        read -r -s -p "  AWS Secret Access Key for \$${key_value_var}: " secret_access_key
        echo ""

        if [[ -z "${access_key_id}" || -z "${secret_access_key}" ]]; then
            echo "ERROR: empty value entered for bucket=(${bucket}) folder=(${folder}) file_mask=(${file_mask}). Aborting."
            exit 1
        fi

        env_lines+=("export ${key_name_var}=${access_key_id}")
        env_lines+=("export ${key_value_var}=${secret_access_key}")
    done 3< "${key_file}"

    if [[ ${#env_lines[@]} -eq 0 ]]; then
        echo "ERROR: no valid bucket|folder|file_mask|\$VAR|\$VAR lines found in ${key_file}. Nothing written."
        exit 1
    fi

    printf '%s\n' "${env_lines[@]}" > "${env_file}"
    chmod 600 "${env_file}"

    echo "-"
    echo "Wrote ${env_file} (chmod 600)."
    echo "This file is gitignored - it holds the real AWS credentials and must never be committed."
fi

# --------------------------------------------------------------------------------
# -- Verify boto3 can reach each bucket|folder combination listed in ${key_file},
# -- using the credentials just exported from ${env_file}.
# --------------------------------------------------------------------------------
if [[ "${skip_s3_check}" -eq 1 ]]; then
    echo "-"
    echo "Deployment complete (S3 verification skipped)."
    exit 0
fi

echo "-"
echo "Verifying S3 access for each combination in ${key_file}..."
echo "-"

set -a
source "${env_file}"
set +a

"${venv_python}" - "${key_file}" << 'PYEOF'
import sys
import os
import boto3
from botocore.exceptions import ClientError

key_file = sys.argv[1]
failures = 0

with open(key_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        bucket, folder, file_mask, key_name_var, key_value_var = line.split('|')

        access_key_id = os.environ.get(key_name_var.lstrip('$'))
        secret_access_key = os.environ.get(key_value_var.lstrip('$'))

        print(f"-\nChecking bucket=({bucket}) folder=({folder}) mask=({file_mask})...")

        if not access_key_id or not secret_access_key:
            print(f"  FAILED: {key_name_var}/{key_value_var} not set in {os.path.basename(key_file)!r}'s .env file.")
            failures += 1
            continue

        session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
        s3c = session.client('s3')

        try:
            s3c.head_bucket(Bucket=bucket)
        except ClientError as e:
            print(f"  FAILED: cannot access bucket ({bucket}): {e}")
            failures += 1
            continue

        try:
            s3c.list_objects_v2(Bucket=bucket, Prefix=f'{folder}/', MaxKeys=1)
        except ClientError as e:
            print(f"  FAILED: cannot list folder ({folder}) in bucket ({bucket}): {e}")
            failures += 1
            continue

        print("  OK.")

if failures:
    print(f"-\n{failures} combination(s) FAILED S3 access verification.")
    sys.exit(1)

print("-\nAll combinations verified successfully.")
PYEOF

echo "-"
echo "Deployment complete."
