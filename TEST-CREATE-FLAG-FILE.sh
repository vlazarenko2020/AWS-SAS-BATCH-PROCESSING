#!/bin/bash
#
# Uploads an empty test .FLAG file straight to S3, for exercising the
# S3_Bucket_processing-EMSERVICEUSER.sh -> ClassS3FlagFile flow end-to-end without
# needing a real mainframe job to drop one. Also drops a matching placeholder
# .sas file into sas01_sasdata_PROD_S3_Bucket_processing/source, since
# ClassS3FlagFile only processes a .FLAG file whose corresponding local .sas
# file already exists (z_config.dic_path_to_sasfile['S3_Bucket_processing']).
#
# Uses this repo's .venv (created by `uv sync` / DEPLOYMENT.sh) + boto3, and
# the same S3_Bucket_processing/info/s3_folder_mask_aws-key.info +
# AWS_KEY/.env-EMSERVICEUSER credential lookup the real pipeline uses - so it only
# works once DEPLOYMENT.sh has been run.
#
# Targets the first bucket|folder|file_mask|$VAR|$VAR line in the key file
# and builds a filename that matches that file_mask (split on '*' into a
# prefix/suffix, same convention ClassS3FlagFile uses).
#
# The local .sas file's basename mirrors ClassS3FlagFile's own basename
# derivation (COMMON/Modules/ClassS3FlagFile.py: splits the flag object's
# basename on '.PRD', not on '.FLAG') so it's actually found and picked up
# by a real end-to-end run, not just superficially "same name".
#
# Usage:
#   ./TEST-CREATE-FLAG-FILE.sh [key_file]   # default: S3_Bucket_processing/info/s3_folder_mask_aws-key.info

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
key_file="${1:-${script_dir}/S3_Bucket_processing/info/s3_folder_mask_aws-key.info}"
env_file="${script_dir}/AWS_KEY/.env-EMSERVICEUSER"
venv_python="${script_dir}/.venv/bin/python"

if [[ ! -f "${key_file}" ]]; then
    echo "ERROR: ${key_file} not found."
    exit 1
fi
if [[ ! -f "${env_file}" ]]; then
    echo "ERROR: ${env_file} not found. Run ./DEPLOYMENT.sh first."
    exit 1
fi
if [[ ! -x "${venv_python}" ]]; then
    echo "ERROR: ${venv_python} not found. Run 'uv sync' (or ./DEPLOYMENT.sh) first."
    exit 1
fi

sas_source_dir="${script_dir}/sas01_sasdata_PROD_S3_Bucket_processing/source"
if [[ ! -d "${sas_source_dir}" ]]; then
    echo "ERROR: ${sas_source_dir} not found. Run ./DEPLOYMENT.sh first (it creates/verifies the sas01_sasdata_PROD_S3_Bucket_processing link)."
    exit 1
fi

line="$(grep -v '^[[:space:]]*$' "${key_file}" | head -n 1)"
if [[ -z "${line}" ]]; then
    echo "ERROR: ${key_file} has no bucket|folder|file_mask|\$VAR|\$VAR lines."
    exit 1
fi

IFS='|' read -r bucket folder file_mask key_name_var key_value_var <<< "${line}"

if [[ "${key_name_var}" != \$* || "${key_value_var}" != \$* ]]; then
    echo "ERROR: fields 4/5 of ${key_file} are not \$VAR references: ${line}"
    exit 1
fi
key_name_var="${key_name_var#\$}"
key_value_var="${key_value_var#\$}"

# -- file_mask (e.g. "*.FLAG") splits on '*' into a startswith/endswith pair,
# -- same convention ClassS3FlagFile uses to match objects.
IFS='*' read -r prefix_part suffix_part <<< "${file_mask}"

timestamp="$(date '+%Y%m%d_%H%M%S')"
object_name="${prefix_part}TEST_${timestamp}${suffix_part}"
object_key="${folder}/${object_name}"

# -- same basename ClassS3FlagFile itself computes: split on '.PRD', NOT on
# -- '.FLAG' (see COMMON/Modules/ClassS3FlagFile.py) - a name with no '.PRD'
# -- in it (like the one built above) keeps its '.FLAG' suffix here too.
sas_basename="${object_name%%.PRD*}"
sas_file="${sas_source_dir}/${sas_basename}.sas"

cat > "${sas_file}" << 'SASEOF'

proc setinit;
run;

SASEOF

echo "-"
echo "Created local .sas program: ${sas_file}"

set -a
source "${env_file}"
set +a

echo "-"
echo "Uploading test flag file to: s3://${bucket}/${object_key}"

"${venv_python}" - "${bucket}" "${object_key}" "${key_name_var}" "${key_value_var}" << 'PYEOF'
import sys
import os
import boto3

bucket, object_key, key_name_var, key_value_var = sys.argv[1:5]

access_key_id = os.environ.get(key_name_var)
secret_access_key = os.environ.get(key_value_var)

if not access_key_id or not secret_access_key:
    print(f"ERROR: {key_name_var}/{key_value_var} not set in environment.")
    sys.exit(1)

session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
s3c = session.client('s3')
s3c.put_object(Bucket=bucket, Key=object_key, Body=b'')
print("OK: created empty S3 object.")
PYEOF

echo "-"
echo "Done. s3://${bucket}/${object_key}"
