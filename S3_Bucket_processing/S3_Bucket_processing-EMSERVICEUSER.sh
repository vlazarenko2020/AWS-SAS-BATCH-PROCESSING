#!/bin/bash
#
system_short_name='S3_Bucket_processing'
system_type='S3'
# system_type='filesystem'

s3_bucket_with_dir='your-s3-bucket/EMSERVICEUSER-DEV'

# - directory (folder) with flag files -- FAKE FOR S3 -- needed to search for parameters in z_config
dir_with_flag_file='S3_Bucket_processing'

thread_to_use=1
# ----- mask: what .FLAG files to process
# ----- The mask MUST have star (*) because I am using split('*') to get startswith and endswith parts
file_mask_in_S3='EMSERVICEUSER*.FLAG'
# -- OR 
file_mask_in_S3='*.FLAG'
# ----------------------------------------
python_bin='/path/to/repo/.venv/bin/python'

# ----- real AWS secret values live only here (gitignored), never in info/s3_folder_mask_aws-key.info itself
source "$(dirname "${BASH_SOURCE[0]}")/../AWS_KEY/.env-EMSERVICEUSER"


# IT_Marketing     - IMEET SVOJ LOG_DIR
# DBM_staging_data - IMEET SVOJ LOG_DIR 
#
dir_log_no_path=log-${system_short_name}


#base_dir="/usr/local/vbin/PROD/sas_ftp_processing_root"
base_dir='.'

dir_log_with_path=${base_dir}/${dir_log_no_path}
LOG_FILE=${dir_log_with_path}/`date '+%Y-%m-%d-%H_%M'`--thread-${thread_to_use}.log

#prog_name_with_path=${base_dir}/sas_ftp_processing_root.py
prog_name_with_path=${base_dir}/../COMMON/sas_ftp_and_S3_Bucket_processing.py


if [[ "${1}" != "test" ]]; 
then 
     exec 1>>${LOG_FILE}
     exec 2>&1
fi

# # --------------------------------------------------------------------------------------
# # -- Creating test .PRD and .FLAG files for DEVELOPMENT TESTING
# ./development_test_progs/development_create_FLAG_files_S3.sh
# # --------------------------------------------------------------------------------------


echo "-"
echo "-"
echo "-"

echo ${python_bin} ${prog_name_with_path} -t ${system_type} -s ${system_short_name} -b ${s3_bucket_with_dir} -d ${dir_with_flag_file} -n ${thread_to_use} -m ${file_mask_in_S3}
echo ''
# ----- commented out for local testing: ${python_bin} doesn't exist off the SAS server,
# ----- and the full pipeline would try to run the real `sas` binary + send real e-mails.
${python_bin} ${prog_name_with_path} -t ${system_type} -s ${system_short_name} -b ${s3_bucket_with_dir} -d ${dir_with_flag_file} -n ${thread_to_use} -m ${file_mask_in_S3}


echo "-"
echo "-"
echo "-"

