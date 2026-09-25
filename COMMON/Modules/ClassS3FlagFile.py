#!/usr/local/vbin/.venv/python3.9/bin/python
#
# python - Boto3 S3, sort bucket by last modified - Stack Overflow
# https://stackoverflow.com/questions/44574548/boto3-s3-sort-bucket-by-last-modified

# Move and Rename objects within an S3 Bucket using Boto 3 | by Gregory Sánchez | plusteam | Medium
# https://medium.com/plusteam/move-and-rename-objects-within-an-s3-bucket-using-boto-3-58b164790b78

# How to Rename Amazon S3 Folder Objects with Python
# https://adamtheautomator.com/s3-rename-folder/

import sys, os
import boto3
import datetime
from pprint import pprint
import logging

sys.path.append('..')
import z_config


logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')




class ClassS3FlagFile():

    def __init__(self,
                f_event):

        # f_event = {
        #    "BOTO-S3-C":
        #    "BUCKET": 'your-s3-bucket',
        #    "PREFIX": 'PROD/FLAG_FILES' 
        # #    "PREFIX": 'DEV/FLAG_FILES' 
        #     "FILE-MASK": '.FLAG'
        # }

        self.dir_with_flag_files   = f_event["FLAG-FILE-DIR"]
        self.boto_s3_c          = f_event["BOTO-S3-C"]
        self.my_bucket          = f_event["BUCKET"]
        self.my_prefix          = f_event["PREFIX"]
        self.thread_number      = f_event["TREAD"]
        self.my_file_mask_in_s3 = f_event["FILE-MASK-IN-S3"] # - 'EMSERVICEUSER*.FLAG'
        # -----------------------------
        prom_elements = self.my_file_mask_in_s3.split('*')
        self.my_file_mask_in_s3_startswith = prom_elements[0] # - 'EMSERVICEUSER'
        self.my_file_mask_in_s3_endswith   = prom_elements[1] # - '.FLAG'
        # -----------------------------
        logger.debug(f'my_file_mask_in_s3_startswith: {self.my_file_mask_in_s3_startswith}')
        logger.debug(f'my_file_mask_in_s3_endswith:   {self.my_file_mask_in_s3_endswith}')
        # -----------------------------


        print(f'self.dir_with_flag_files: {self.dir_with_flag_files}')

        # --------------------------------------------------------------------------------
        # file_with_aws_key = z_config.dic_path_to_aws_key[self.dir_with_flag_files]
        # file_with_aws_key = '/usr/local/vbin/DEVELOPMENT/AWS_KEY/EMSERVICEUSER'
        # Each line in file_with_aws_key is an authorized combination:
        #     bucket_name|path_in_bucket|file_mask|AWS_Key_Name|AWS_Key_Value
        # Only a combination that is actually listed there is allowed to run.
        # AWS_Key_Name/AWS_Key_Value are not the real secret values - they are
        # environment variable NAMES (e.g. $AWS_KEY_1 / $AWS_KEY_VALUES_1), so the
        # real secrets never live in this file / in git. The real values are exported
        # by the matching AWS_KEY/.env-<NAME> file (gitignored) before this runs.
        file_with_aws_key = f_event["FILE-WITH-AWS-KEY"]

        f_aws_access_key_id     = None
        f_aws_secret_access_key = None

        with open(file_with_aws_key) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                l_bucket, l_folder, l_file_mask, l_key_name, l_key_value = line.split('|')
                if (l_bucket == self.my_bucket and
                        l_folder == self.my_prefix and
                        l_file_mask == self.my_file_mask_in_s3):
                    f_aws_access_key_id     = l_key_name
                    f_aws_secret_access_key = l_key_value
                    break
        # --------------------------------------------------------------------------------
        if f_aws_access_key_id is None:
            logger.critical(f"ERROR: NO AUTHORIZED COMBINATION FOUND IN ({file_with_aws_key}) FOR "
                            f"BUCKET=({self.my_bucket}) FOLDER=({self.my_prefix}) FILE-MASK=({self.my_file_mask_in_s3}). EXITING.")
            exit()
        # --------------------------------------------------------------------------------
        # Fields may be literal env-var references ($AWS_KEY_1) instead of raw values -
        # resolve those against the process environment. Fail closed if the referenced
        # environment variable isn't set (never fall back to treating it as a literal).
        if f_aws_access_key_id.startswith('$'):
            env_var_name = f_aws_access_key_id[1:]
            f_aws_access_key_id = os.environ.get(env_var_name)
            if f_aws_access_key_id is None:
                logger.critical(f"ERROR: ENVIRONMENT VARIABLE ({env_var_name}) REFERENCED IN ({file_with_aws_key}) IS NOT SET. EXITING.")
                exit()
        if f_aws_secret_access_key.startswith('$'):
            env_var_name = f_aws_secret_access_key[1:]
            f_aws_secret_access_key = os.environ.get(env_var_name)
            if f_aws_secret_access_key is None:
                logger.critical(f"ERROR: ENVIRONMENT VARIABLE ({env_var_name}) REFERENCED IN ({file_with_aws_key}) IS NOT SET. EXITING.")
                exit()
        # --------------------------------------------------------------------------------
        logger.debug(f'f_aws_access_key_id:     {f_aws_access_key_id}')
        # logger.debug(f'f_aws_secret_access_key: {f_aws_secret_access_key}')

        self.session = boto3.Session(
            aws_access_key_id=f_aws_access_key_id,
            aws_secret_access_key=f_aws_secret_access_key,
        )
        self.s3r = self.session.resource('s3')
        self.s3c = self.session.client('s3')
    # --------------------------------------------------------------------------------





    def s3_bucket_exists(self):
        # self.my_bucket = 'sdwdsdsdsdzxzsxzx'
        try:
            response = self.s3c.head_bucket(Bucket=self.my_bucket)
            #                             #   ExpectedBucketOwner='string')

            # plogger.debug(response)
            # {'ResponseMetadata': {'HTTPHeaders': {'content-type': 'application/xml',
            #                                     'date': 'Mon, 06 Dec 2021 16:02:21 GMT',
            #                                     'server': 'AmazonS3',
            #                                     'x-amz-access-point-alias': 'false',
            #                                     'x-amz-bucket-region': 'us-east-1',
            #                                     'x-amz-id-2': '5B/QeDwsR8OO5xnaoJlhLMT+yqZh3cm4s6eHSwoU7N2j+7/XZWxFJndeu3rpvLfIPg37PnwaRfM=',
            #                                     'x-amz-request-id': 'FEFDQCX9F5ZSDVFZ'},
            #                     'HTTPStatusCode': 200,
            #                     'HostId': '5B/QeDwsR8OO5xnaoJlhLMT+yqZh3cm4s6eHSwoU7N2j+7/XZWxFJndeu3rpvLfIPg37PnwaRfM=',
            #                     'RequestId': 'FEFDQCX9F5ZSDVFZ',
            #                     'RetryAttempts': 0}}
            # logger.debug(response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            logger.debug('')       
            logger.debug(f"ERROR: S3 BUCKET ({self.my_bucket}) DOESN'T EXIST OY I DON'T HAVE ACCESS TO THE BUCKET. EXITING.")        
            logger.debug(e)       
            logger.debug('')       
            exit() 
        logger.debug(f'SUCCESS: S3 BUCKET ({self.my_bucket}) EXISTS AND I HAVE RIGHTS TO ACCESS THE BUCKET.')       





    def s3_get_oldest_flag_file(self):

        # logger.debug(f'self.my_bucket = {self.my_bucket}')
        # logger.debug(f'self.my_prefix = {self.my_prefix}')

        unsorted = []
        for file in self.s3r.Bucket(self.my_bucket).objects.filter(Prefix=f'{self.my_prefix}/'):
            # self.my_file_mask_in_s3_startswith = 'EMSERVICEUSER'
            # self.my_file_mask_in_s3_endswith   = '.FLAG'
            logger.debug(f'file.key                           = {file.key}')
            if os.path.basename(file.key).endswith(self.my_file_mask_in_s3_endswith): # '.FLAG'
                if os.path.basename(file.key).startswith(self.my_file_mask_in_s3_startswith): # 'EMSERVICEUSER'
                    unsorted.append(file)

        # logger.debug('unsorted:')
        # logger.debug(unsorted)

        # self.l_flag_file_all = [obj.key for obj in sorted(unsorted, key=lambda x: x.last_modified, reverse=False)][0:1]
        self.l_flag_file_all  = [obj.key for obj in sorted(unsorted, key=lambda x: x.last_modified, reverse=False)]


        if len(self.l_flag_file_all) > 0: # There are files with our mask 'EMSERVICEUSER*.FLAG'

            logger.debug('')
            logger.debug("S3 Bucket's FLAG files to process using mask (self.my_file_mask_in_s3):")
            logger.debug("(self.l_flag_file_all):")
            logger.debug(self.l_flag_file_all)
            logger.debug('')

            for cur_s3_flag_file_without_path in self.l_flag_file_all:
                cur_flag_file_with_path = f"{self.dir_with_flag_files}/{cur_s3_flag_file_without_path}"

                self.flag_file_oldest = self.l_flag_file_all[0]

                # 'DEV/FLAG_FILES/1/vasyl_test_1.PRD.FLAG'
                logger.debug(f"Current S3 FLAG-FILE: ({self.flag_file_oldest})")
                logger.debug('')
                # 'DEV/FLAG_FILES/1/vasyl_test_1.PRD.FLAG'


                # -- I know FAKE self.dir_with_flag_files
                # -- I know S3 cur_s3_flag_file_without_path

                cur_flag_file_without_extention = cur_s3_flag_file_without_path.split('.FLAG')[0]
                cur_flag_file_without_extention = cur_s3_flag_file_without_path.split('.PRD')[0]

                d_prog_config     = z_config.f_get_prog_config(self.dir_with_flag_files)
                dir_for_sas_file  = d_prog_config['path_to_sasfile']
                dir_for_log_files = d_prog_config['path_to_logfile']


                cur_sas_file_with_path      = f"{dir_for_sas_file}/{os.path.basename(cur_flag_file_without_extention)}.sas"
                cur_dir_for_sas_logfiles = d_prog_config['path_to_logfile']



                if os.path.exists(cur_sas_file_with_path):

                    logger.debug(f" - Current S3 SAS-FILE:          ({cur_sas_file_with_path}) exists.")

                    if os.path.exists(cur_dir_for_sas_logfiles):
                        logger.debug(f" - Current Dir for SAS LogFiles: ({cur_dir_for_sas_logfiles}) exists.")
                        logger.debug('')
                        # -- SUCCESS
                        r_event = { 
                            "YES_NO": "YES",
                            "FLAG-FILE-WITH-PATH": cur_flag_file_with_path,
                            "SAS-FILE-WITH-PATH": cur_sas_file_with_path,
                            "LOGDIR-WITH-PATH": cur_dir_for_sas_logfiles,
                            "PRD-FILES-WITH-PATH": '',
                            "COMPRESS-PRD": False
                        } 
                        # -- NO NEED TO LOOK FOR NEXT FLAG-FILE in FOR-LOOP
                        # -- I NEED THE FIRST QUALIFY FLAG-FILE TO FINISH THIS FUNCTION
                        self. s3_move_flag_file()
                        return r_event
                    else:
                        logger.debug(f" - Current Dir for SAS LogFiles: ({cur_dir_for_sas_logfiles}) doesn't exists. Moving to the next S3 FLAG file.")
                else:
                    logger.debug(f" - Current S3 SAS-FILE: ({cur_sas_file_with_path}) doesn't exists. Moving to the next S3 FLAG file.")

            logger.debug(f"WARNING: All found .FLAG files have no correct local .sas files. Nothing to process in this run.")
            r_event = { 
                "YES_NO": "NO",
                "FLAG-FILE-WITH-PATH": 'NO-FILE',
                "SAS-FILE-WITH-PATH": 'NO-FILE',
                "LOGDIR-WITH-PATH": 'NO-DIR',
                "PRD-FILES-WITH-PATH": 'NO-FILE',
                "COMPRESS-PRD": False
            } 
        else:  # # There are no files with our mask 'EMSERVICEUSER*.FLAG' in S3 Bucket
            logger.debug('')
            logger.debug(f"No S3 Bucket's FLAG files to process using mask ({self.my_file_mask_in_s3}) were found.")
            logger.debug("Nothing to do.")
            logger.debug('')

            r_event = { 
                "YES_NO": "NO",
                "FLAG-FILE-WITH-PATH": 'NO-FILE',
                "SAS-FILE-WITH-PATH": 'NO-FILE',
                "LOGDIR-WITH-PATH": 'NO-DIR',
                "PRD-FILES-WITH-PATH": 'NO-FILE',
                "COMPRESS-PRD": False
            } 
        return r_event

            # self.flag_file_oldest = ''

            # cur_prd_file_with_path = cur_flag_file_with_path.replace('.FLAG', '')

            # if os.path.exists(cur_prd_file_with_path):
            #     logger.debug(f'PRD-FILE ({cur_prd_file_with_path}) EXISTS.')

            #     # current_yes_no, current_sas_file_with_path, current_log_dir_with_path = f_check_sasfile_i_logdir_presence(cur_flag_file_with_path)
            #     from_event = f_check_sasfile_i_logdir_presence(cur_flag_file_with_path)
            #     # from_event = {
            #     #     "YES_NO": 'YES',
            #     #     "SAS-FILE-WITH-PATH": current_sas_file_with_path,
            #     #     "LOGDIR-WITH-PATH": current_log_dir_with_path
            #     # }

            #     if from_event["YES_NO"] == 'YES':

            #         # ---------------------------------------------------------------------------------------------
            #         # --- Check if .FLAG file is for "ORDER_ITEM_HIST_WEEKEND" table
            #         f_kill_users_if_ORDER_HIST(cur_flag_file_with_path)
            #         # current_sas_file_with_path = ''
            #         # current_log_dir_with_path = ''
            #         # ---------------------------------------------------------------------------------------------

            #         # -- SUCCESS
            #         r_event = { 
            #             "YES_NO": "YES",
            #             "FLAG-FILE-WITH-PATH": cur_flag_file_with_path,
            #             "SAS-FILE-WITH-PATH": from_event["SAS-FILE-WITH-PATH"],
            #             "LOGDIR-WITH-PATH": from_event["LOGDIR-WITH-PATH"],
            #             "PRD-FILES-WITH-PATH": [cur_prd_file_with_path],
            #             "COMPRESS-PRD": z_config.dic_compress[f_dir_with_flag_files]
            #         } 
            #         # -- NO NEED TO LOOK FOR NEXT FLAG-FILE in FOR-LOOP
            #         # -- I NEED THE FIRST QUALIFY FLAG-FILE TO FINISH THIS FUNCTION
            #         return r_event

            #     else:
            #         logger.debug("SAS-FILE OR LOGDIR DOESN'T EXIST. WILL TRY NEXT FLAG FILE IN MY LOOP.")
            #         # -- GO TO NEXT LOOP
            # else:
            #     logger.debug(f"CUR-PRD-FILE-WITH-PATH {cur_prd_file_with_path} DOESN'T EXIST. WILL TRY NEXT FLAG FILE IN MY LOOP.")
            #     # -- GO TO NEXT LOOP

        # c_event_4 = {
        #     "YES_NO": "YES",
        #     "FLAG-FILE-WITH-PATH": cur_flag_file_with_path,
        #     "SAS-FILE-WITH-PATH": from_event["SAS-FILE-WITH-PATH":],
        #     "LOGDIR-WITH-PATH": from_event["LOGDIR-WITH-PATH"],
        #     "PRD-FILE-WITH-PATH": cur_prd_file_with_path
        # } 





    def s3_move_flag_file(self):

        cur_date_time_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # self.flag_file_oldest VALUE IS 'DEV/FLAG_FILES/vasyl_test_1.PRD.FLAG'
        flag_file_to_process_path_only       = os.path.dirname(self.flag_file_oldest)
        flag_file_to_process_filename_only   = os.path.basename(self.flag_file_oldest)
        # I cannot use DEV/FLAG_FILES/1/ because in S3 all subfolders are used to find .FLAG files
        # So I am using folder that is not under DEV/FLAG_FILES
        # The folder for .FLAG files backup (instead of DEV/FLAG_FILES/1/) is DEV/FLAG_FILES_PROCESSED/1
        flag_file_to_process__backup_location = os.path.join('DEV/FLAG_FILES_PROCESSED',
                                                            self.thread_number,
                                                            f'{cur_date_time_str}--{flag_file_to_process_filename_only}')
        # DEV/FLAG_FILES_PROCESSED/1/2022-01-05_13-10-33-vasyl_test_1.PRD.FLAG

        logger.debug(f"flag_file_to_process__backup_location: {flag_file_to_process__backup_location}")

        new_file_name_relative = flag_file_to_process__backup_location
        # 'DEV/FLAG_FILES/1/v-2.FLAG'
        old_file_name_with_Bucket_name = os.path.join(self.my_bucket, self.flag_file_oldest)
        # 'DEV/FLAG_FILES/v-2.FLAG'
        logger.debug(f"S3 Bucket:                      {self.my_bucket}")
        logger.debug(f"new_file_name_relative:         {new_file_name_relative}")
        logger.debug(f"old_file_name_with_Bucket_name: {old_file_name_with_Bucket_name}")


        logging.exception(f"Moving S3 Flag file ({old_file_name_with_Bucket_name}) to ({new_file_name_relative})")

        try:
            # Copy object A as object B
            #                                                                            |||||||||||||||||||||| --- | --- CURRENT FULL FILE PATH WITH BUCKET-NAME
            self.s3r.Object(self.my_bucket, new_file_name_relative).copy_from(CopySource=old_file_name_with_Bucket_name)
            #                               ||||||||||||||||||||||
            #                               | --- FUTURE NEW RELATIVE FILE PATH IN NEW FOLDER 
        except Exception:
            logging.exception(f"Cannot move file ({old_file_name_with_Bucket_name}) to ({new_file_name_relative})")
            

        # -- Delete Original FLAG file
        try:
            self.s3r.Object(self.my_bucket, self.flag_file_oldest).delete()
        except Exception:
            logging.exception(f"Cannot delete FLAG file ({self.flag_file_oldest})")





    def s3_flag_file_main(self):

        self.s3_bucket_exists()
        self.s3_get_oldest_flag_file()
        self.s3_move_flag_file()
