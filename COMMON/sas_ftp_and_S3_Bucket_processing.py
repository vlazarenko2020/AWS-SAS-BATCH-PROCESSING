#!/usr/local/vbin/.venv/python3.9/bin/python
#
#

import os
import argparse
import datetime
import shutil
import z_config

#from datetime import datetime

import logging
import logging.config
import logging.handlers

# from Modules.f_arguments                 import (f_argument_folder_with_flag_file,
#                                                  f_argument_thread_number)
from Modules.f_file_i_am_working        import f_file_i_am_working
from Modules.f_select_oldest_flag_file_and_kill_processes import f_select_oldest_flag_file_and_kill_processes
from Modules.ClassSASProgram             import ClassSASProgram
from Modules.ClassS3FlagFile             import ClassS3FlagFile

from Modules.f_ftp_scoring_status_file_to_mainframe       import f_ftp_scoring_status_file_to_mainframe
from Modules.f_run_different_logic_before_run_any_sas     import f_run_different_logic_before_run_any_sas
from Modules.f_run_different_logic_after_run_any_sas      import f_run_different_logic_after_run_any_sas
# from Modules.f_compress_prd_file_if_it_was_pass_as_argument import f_compress_prd_file_if_it_was_pass_as_argument

LOGGER_CONFIG_FILE_PREFIX = 'z_config_loggers'
#   -----------------------------------------------------------------------------------------------------------




def main():

    # now = datetime.now()
    # current_date_str = now.strftime("%Y%m%d%H%M%S")

    # -------------------------------------------------------------
    parser = argparse.ArgumentParser()
    # - type (filesystem/S3)
    parser.add_argument('-t',
                        required=True,
                        type=str)
    # - system short name
    parser.add_argument('-s',
                        required=True,
                        type=str)
    # - bucket with dir: 
    #    - your-s3-bucket/DEV/FLAG_FILES
    parser.add_argument('-b',
                        required=True,
                        type=str)
    # - directory (folder) with flag files -- FAKE FOR S3 -- needed to search for parameters in z_config
    parser.add_argument('-d',
                        required=True,
                        type=str)
    # - thread
    parser.add_argument('-n',
                        required=True,
                        type=str)
    # - mask for S3 files to diffirenciate EMSERVICEUSER and MRSERVICEUSER FLAG-files: '.FLAG'
    parser.add_argument('-m',
                        required=True,
                        type=str)
    # -------------------------------------------------------------
    args = parser.parse_args()

    system_type          = args.t
    system_short_name    = args.s
    folder_with_flag_file = args.d    # -- fake for S3
    thread_number        = args.n
    file_mask_in_S3      = args.m    # -- fake for filesystem
    # -------------------------------------------------------------





    # -----------------------------------------
    s3_bucket_with_dir    = args.b   # your-s3-bucket/DEV/FLAG_FILES
    l_elements            = s3_bucket_with_dir.split('/')
    s3_bucket_without_dir = l_elements[0]   # your-s3-bucket

    s3_bucket_dir_only = ''
    for element in l_elements[1:]: # ['DEV', 'FLAG_FILES']
        s3_bucket_dir_only = f"{s3_bucket_dir_only}/{element}"
        # DEV/FLAG_FILES/

    s3_bucket_dir_only = s3_bucket_dir_only[1:] # Removing leading '/' --- DEV/FLAG_FILES
    # DEV/FLAG_FILES
    # -----------------------------------------
    
    
    # -------------------------------------------------------------------------
    logging.config.fileConfig(f'{LOGGER_CONFIG_FILE_PREFIX}-{system_short_name}.ini')
    logger = logging.getLogger(__name__)
    logger.critical('-----------------------------------------------------------------------------------')
    logger.critical(f"Log Level in '{__name__}': {logger.level}")
    logger.critical('-----------------------------------------------------------------------------------')
    # -------------------------------------------------------------------------
    
    logger.debug(f'system_type:           {system_type}')
    logger.debug(f'system_name:           {system_short_name}')
    logger.debug(f's3_bucket_with_dir:    {s3_bucket_with_dir}')
    logger.debug(f's3_bucket_without_dir: {s3_bucket_without_dir}')
    logger.debug(f's3_bucket_dir_only:    {s3_bucket_dir_only}')
    logger.debug(f'thread_number:         {thread_number}')



    # -------------------------------------------------------------------------
    file_with_aws_key = z_config.f_get_prog_config('S3_Bucket_processing')['path_to_aws_key']
    if os.path.exists(file_with_aws_key):
        event = {
            "FILE-WITH-AWS-KEY": file_with_aws_key,
            "FLAG-FILE-DIR": 'S3_Bucket_processing',
            "BOTO-S3-C": '',  # - pass boto3 object
            "BUCKET": s3_bucket_without_dir,
            "PREFIX": s3_bucket_dir_only,
            # "PREFIX": 'PROD/FLAG_FILES',
            # "PREFIX": 'DEV/FLAG_FILES',
            "FILE-MASK-IN-S3": file_mask_in_S3,  # Initially '.FLAG'. But needs to be something like 'EMSERVICEUSER*.FLAG' or 'MRSERVICEUSER*.FLAG'
            "TREAD": thread_number
        }
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    if system_type == 'S3':
        iClassS3FlagFile = ClassS3FlagFile(event)
        # iClassS3FlagFile.s3_flag_file_main()
    # -------------------------------------------------------------------------




    # -------------------------------------------------------------------------
    # -- Cheking 1-st argument 'folder_with_flag_file'
    # --- 'folder_with_flag_file' is a key to all z_config dicrionary
    # --- So we will find:
    #   --  - user_to_run_any
    #   --  - mailfile_with_path
    if system_type == 'filesystem':
        if os.path.exists(folder_with_flag_file):
            logger.debug(f'ARGUMENT: FLAG-FILE-FOLDER {folder_with_flag_file} EXISTS.')
            user_to_run_any = z_config.f_get_prog_config(folder_with_flag_file)['path_to_user']
            mailfile_with_path   = z_config.f_get_prog_config(folder_with_flag_file)['path_to_mailfile']
        else:
            logger.debug(f"ERROR: ARGUMENT 'FLAG-FILE-FOLDER' {folder_with_flag_file} DOESN'T EXIST. EXITING.")
            exit()
    elif system_type == 'S3':
        iClassS3FlagFile.s3_bucket_exists()
        # IF THE BUCKET DOESN'T EXIST -- THERES 'exit()' IN iClassS3FlagFile.s3_bucket_exists()
        user_to_run_any = z_config.f_get_prog_config(folder_with_flag_file)['path_to_user']
        mailfile_with_path   = z_config.f_get_prog_config(folder_with_flag_file)['path_to_mailfile']

    logger.debug(f'user_to_run_any = {user_to_run_any}')
    logger.debug(f'mailfile_with_path   = {mailfile_with_path}')
    # -------------------------------------------------------------------------
    






    # -------------------------------------------------------------------------
#   -- Checking the 2-ND ARGUMENT - thread_number (1 OR 2 OR 3 OR 4)
#   -- Check if folder_with_flag_file/thread_folder EXISTS
    if system_type == 'filesystem':
        dir_thread_with_path = f"{folder_with_flag_file}/{thread_number}"
        if os.path.exists(dir_thread_with_path):
            logger.debug(f'FOLDER OF OUR-THREAD-NUMBER {dir_thread_with_path} EXISTS.')
        else:
            logger.debug(f'FOLDER OF OUR-THREAD-NUMBER {dir_thread_with_path} DOESN\'T EXIST. EXITING.')
            exit()
    elif system_type == 'S3':
        pass # dir_thread_with_path IN S3 BUCKET WILL BE CREATED ON-FLY IF IT DOESN'T EXIST
    # -------------------------------------------------------------------------




    # -------------------------------------------------------------------------
    # -- Checking if one instance of this program with thread is already working
    # -- NO -- Create file ___I_am_working_thread_1
    # -- NEED TO DO IT HERE --- AFTER PROVERKI thread FOLDER EXISTENCE
    if system_type == 'filesystem':
        c_event_3 = f_file_i_am_working(thread_number,
                                        folder_with_flag_file) 
    
        file_i_am_working_with_path = c_event_3["I-AM-WORKING-FILE"]
        logger.debug(f'I-AM-WORKING-FILE ({file_i_am_working_with_path}) WAS CREATED.')
    elif system_type == 'S3':
        c_event_3 = f_file_i_am_working(thread_number,
                                        folder_with_flag_file) 
    
        file_i_am_working_with_path = c_event_3["I-AM-WORKING-FILE"]
        logger.debug(f'I-AM-WORKING-FILE ({file_i_am_working_with_path}) WAS CREATED.')
    # -------------------------------------------------------------------------
    try:

    


    #   -- READ ALL .FLAG files (sorted by creating date) FROM folder_with_flag_file
    #   -- USE THE OLDEST .FLAG FILE.
    #   -- CHECK IF CORRESPONDING .PRD FILE EXISTS IN THE SAME DIR folder_with_flag_file
    #   -- CHECK IF CORRESPONDING .sas PROGRAMM EXISTS IN dir_with_sas_programs
    #   -- CHECK IF CORRESPONDING LOG DIR EXISTS


        # -------------------------------------------------------------------------
        if system_type == 'filesystem':
            # (current_yes_no, current_flag_file_with_path, current_sas_file_with_path, current_log_dir_with_path, current_prd_file_with_path) = f_select_oldest_flag_file_and_kill_processes(folder_with_flag_file)
            c_event_4 = f_select_oldest_flag_file_and_kill_processes(folder_with_flag_file)
            # c_event_4 = {
            #     "YES_NO": "YES",
            #     "FLAG-FILE-WITH-PATH": cur_flag_file_with_path,
            #     "SAS-FILE-WITH-PATH": from_event["SAS-FILE-WITH-PATH":],
            #     "LOGDIR-WITH-PATH": from_event["LOGDIR-WITH-PATH"],
            #     "PRD-FILE-WITH-PATH": cur_prd_file_with_path
            # } 
        elif system_type == 'S3':
            c_event_4 = iClassS3FlagFile.s3_get_oldest_flag_file()
        # -------------------------------------------------------------------------


        current_yes_no             = c_event_4["YES_NO"]
        current_flag_file_with_path = c_event_4["FLAG-FILE-WITH-PATH"]
        current_sas_file_with_path    = c_event_4["SAS-FILE-WITH-PATH"]
        current_log_dir_with_path     = c_event_4["LOGDIR-WITH-PATH"]
        current_l_prd_files_with_path = c_event_4["PRD-FILES-WITH-PATH"]
        current_should_I_compress_prd_files = c_event_4["COMPRESS-PRD"] # True/False



        logger.debug('')
        logger.debug(f'DO WE HAVE FLAG FILE TO RUN: {current_yes_no}')
    
        if current_yes_no == 'YES':  # NO - if FLAG file was not found

            logger.debug(f'...FLAG-FILE: ({current_flag_file_with_path}) WAS FOUND.' )

            logger.debug(f'current_flag_file_with_path = {current_flag_file_with_path}')
            logger.debug(f'current_sas_file_with_path    = {current_sas_file_with_path}')
            logger.debug(f'current_log_dir_with_path     = {current_log_dir_with_path}')
            logger.debug(f'current_l_prd_files_with_path = {current_l_prd_files_with_path}')

            if system_type == 'filesystem':

                cur_date_time_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

                # -- MOVE .FLAG FILE TO 1 OR 2 OR 3 OR 4 thread-FOLDER
                # -- Only the .FLAG file is moved into the thread folder. The .PRD data file
                # -- stays in its original location because the .sas program reads it from there
                # -- (and it's only backed up/compressed afterwards, on SAS-SUCCESS).

                (prom_dir, current_flag_file_without_path) = os.path.split( current_flag_file_with_path  )
                current_flag_file_with_thread_path = os.path.join(dir_thread_with_path,
                                                            f'{cur_date_time_str}--{current_flag_file_without_path}')
                logger.debug(f'MOVE {current_flag_file_with_path} TO {current_flag_file_with_thread_path}')
                try:
                    shutil.move(current_flag_file_with_path, current_flag_file_with_thread_path)
                    logger.debug(f'SUCESS: FILE {current_flag_file_with_path} WAS MOVED TO {current_flag_file_with_thread_path}')

                except Exception as e:
                    logger.debug(f'ERROR: FILE {current_flag_file_with_path} WAS NOT MOVED TO {current_flag_file_with_thread_path}')
                    logger.debug(e)

            elif system_type == 'S3':
                # S3 FLAG file was already moved during iClassS3FlagFile.s3_get_oldest_flag_file() execution
                pass

            # exit()







            # -------------------------------------------------------------------------------------------------
            # -- KILL ALL SESSIONS BEFORE ORDER_ITEM_HIST STARTS
            f_run_different_logic_before_run_any_sas()
            # -------------------------------------------------------------------------------------------------

            to_event_1 = {
                "SYSTEM-SHORT-NAME": system_short_name,
                "SAS-FILE-WITH-PATH": current_sas_file_with_path,
                "LOGDIR-WITH-PATH": current_log_dir_with_path,
                "FILE MAIL SENDERS": mailfile_with_path,
                "LIST-PRD-FILES-WITH-PATH": current_l_prd_files_with_path  # -- the list can be empty if we don't need .PRD files. I am checking the list later in .PRD move section.
            }
            iClassSASProgram = ClassSASProgram(to_event_1)
            # -- iClassSASProgram.run_sas_program_main() ---
            # -- RUN .sas PROGRAM
            # -- IF .log FILE WAS CREATED:
            # --    - SAS-ERROR:   SEND E-MAIL WITH ERROR   STATUS AND LOGFILE AS THE E-MAIL BODY
            # --    - SAS-SUCCESS: SEND E-MAIL WITH SUCCESS STATUS AND LOGFILE AS THE E-MAIL BODY
            # -- IF .log FILE WAS NOT CREATED:
            # --    - SAS-WARNING: SEND E-MAIL WITH WARNING STATUS AND WITHOUT LOGFILE AS THE E-MAIL BODY
            #                                ^^^^^^^^^^^^^^^^^^^^^^
            #                                ^^^^^^^^^^^^^^^^^^^^^^
            #                                ^^^^^^^^^^^^^^^^^^^^^^
            y_n_error_in_log = iClassSASProgram.f_run_sas_program()
            # ^^^^^^^^^^^
            # ^^^^^^^^^^^ -- Need to know if completed with ERROR because I need not to move/rename .PRD data file
            # ^^^^^^^^^^^ -- the operator needs to re-run the .FLAG file without re-SFTP .PRD file
            # ^^^^^^^^^^^ -- 'ERROR'   - don't move/rename .PRD data file
            # ^^^^^^^^^^^ -- 'SUCCESS' - move/rename .PRD data file

            # -------------------------------------------------------------------------------------------------
            f_run_different_logic_after_run_any_sas(folder_with_flag_file,
                                                    current_l_prd_files_with_path,
                                                    y_n_error_in_log,
                                                    current_should_I_compress_prd_files)
            # -------------------------------------------------------------------------------------------------

        else:  # NO - if FLAG file was not found
            logger.debug( '...FLAG-FILE: WAS NOT FOUND OR NOT READY. WILL TRY AGAIN FROM crontab. EXITING.' )


    finally:
        # -- Always remove the flag file here, even if the try block above exited early
        # -- (e.g. via exit()/SystemExit from ClassSASProgram's not-allowed-user check)
        # -- or raised - otherwise it's left behind and every future run refuses to
        # -- start, thinking a thread is already working.
        if os.path.exists(file_i_am_working_with_path):
            os.remove(file_i_am_working_with_path)
            logger.debug('')
            logger.debug('file_i_am_working_with_path (' + file_i_am_working_with_path + ') WAS DELETED.')
            logger.debug('')




if __name__ == "__main__":
  main()

