#!/bin/bash
#

system_short_name=DBM_staging_data
dir_base='/sas01/sasdata/PROD/S3_Bucket_processing'


bucket_and_dir_with_flag_file='your-s3-bucket/DEV/FLAG_FILES'


create_flag_and_sas_files()
     {
     for i in {1..3}
     do
          file_without_path="${1}_${i}.PRD.FLAG"
          file_with_path="/tmp/${file_without_path}"

          echo touch "${file_with_path}" 
               touch "${file_with_path}" 

          echo aws s3 cp "${file_with_path}" "s3://${bucket_and_dir_with_flag_file}/"
               aws s3 cp "${file_with_path}" "s3://${bucket_and_dir_with_flag_file}/"

          echo rm "${file_with_path}"
               rm "${file_with_path}"

               
          sas_file_with_path="${dir_base}/source/${1}_${i}.sas"

          echo "proc setinit;" > ${sas_file_with_path}
          echo "run;" >> ${sas_file_with_path}
          echo "" >> ${sas_file_with_path}

     done

     echo "aws s3 ls s3://${bucket_and_dir_with_flag_file}/"
          aws s3 ls "s3://${bucket_and_dir_with_flag_file}/"

     echo ls -l "${dir_base}/source/${1}_*"
          ls -l  ${dir_base}/source/${1}_*

     }


create_flag_and_sas_files 'vasyl_test'
create_flag_and_sas_files 'EMSERVICEUSER_vasyl_test'
create_flag_and_sas_files 'MRSERVICEUSER_vasyl_test'




# for i in {1..5}
# do
#     file_without_path="${test_file_prefix}_${i}.PRD.FLAG"
#     file_with_path="/tmp/${file_without_path}"

#     echo touch "${file_with_path}" 
#          touch "${file_with_path}" 

#     echo aws s3 cp "${file_with_path}" "s3://${bucket_and_dir_with_flag_file}/"
#          aws s3 cp "${file_with_path}" "s3://${bucket_and_dir_with_flag_file}/"

#      sas_file_with_path="${dir_base}/source/${test_file_prefix}_${i}.sas"


#     echo "proc setinit;" > ${sas_file_with_path}
#     echo "run;" >> ${sas_file_with_path}
#     echo "" >> ${sas_file_with_path}

# done

# echo "aws s3 ls s3://${bucket_and_dir_with_flag_file}/"
#       aws s3 ls "s3://${bucket_and_dir_with_flag_file}/"

# echo ls -l "${dir_base}/source/${test_file_prefix}_*"
#      ls -l  ${dir_base}/source/${test_file_prefix}_*

      