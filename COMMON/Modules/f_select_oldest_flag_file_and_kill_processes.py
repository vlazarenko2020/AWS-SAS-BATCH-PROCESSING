
import os
import glob
import logging

import z_config

from Modules.f_check_sasfile_i_logdir_presence import f_check_sasfile_i_logdir_presence
from Modules.f_kill_users_if_ORDER_HIST import f_kill_users_if_ORDER_HIST

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')

#----------------------------------------------------------
def f_select_oldest_flag_file_and_kill_processes(f_dir_with_flag_files):

    r_event = {}
    logger.debug(f'FLAG-FILE-FOLDER: {f_dir_with_flag_files}')

    l_flag_files_with_path = sorted(glob.glob(f_dir_with_flag_files + "/*.FLAG"),
                                  key=os.path.getmtime)

    if len(l_flag_files_with_path) != 0:

        for idx, cur_flag_file_with_path in enumerate(l_flag_files_with_path):

            cur_prd_file_with_path = cur_flag_file_with_path.replace('.FLAG', '')

            logger.debug('--')
            logger.debug('--')
            logger.debug('--')
            logger.debug(f'CUR-FLAG-FILE-{str(idx + 1)}: {cur_flag_file_with_path}')

            if os.path.exists(cur_prd_file_with_path):
                logger.debug(f'PRD-FILE ({cur_prd_file_with_path}) EXISTS.')

                # current_yes_no, current_sas_file_with_path, current_log_dir_with_path = f_check_sasfile_i_logdir_presence(cur_flag_file_with_path)
                from_event = f_check_sasfile_i_logdir_presence(cur_flag_file_with_path)
                # from_event = {
                #     "YES_NO": 'YES',
                #     "SAS-FILE-WITH-PATH": current_sas_file_with_path,
                #     "LOGDIR-WITH-PATH": current_log_dir_with_path
                # }

                if from_event["YES_NO"] == 'YES':

                    # ---------------------------------------------------------------------------------------------
                    # --- Check if .FLAG file is for "ORDER_ITEM_HIST_WEEKEND" table
                    f_kill_users_if_ORDER_HIST(cur_flag_file_with_path)
                    # current_sas_file_with_path = ''
                    # current_log_dir_with_path = ''
                    # ---------------------------------------------------------------------------------------------

                    # -- SUCCESS
                    r_event = { 
                        "YES_NO": "YES",
                        "FLAG-FILE-WITH-PATH": cur_flag_file_with_path,
                        "SAS-FILE-WITH-PATH": from_event["SAS-FILE-WITH-PATH"],
                        "LOGDIR-WITH-PATH": from_event["LOGDIR-WITH-PATH"],
                        "PRD-FILES-WITH-PATH": [cur_prd_file_with_path],
                        "COMPRESS-PRD": z_config.f_get_prog_config(f_dir_with_flag_files)['compress'] # -- True/False
                    } 
                    # -- NO NEED TO LOOK FOR NEXT FLAG-FILE in FOR-LOOP
                    # -- I NEED THE FIRST QUALIFY FLAG-FILE TO FINISH THIS FUNCTION
                    return r_event

                else:
                    logger.debug("SAS-FILE OR LOGDIR DOESN'T EXIST. WILL TRY NEXT FLAG FILE IN MY LOOP.")
                    # -- GO TO NEXT LOOP
            else:
                logger.debug(f"CUR-PRD-FILE-WITH-PATH {cur_prd_file_with_path} DOESN'T EXIST. WILL TRY NEXT FLAG FILE IN MY LOOP.")
                # -- GO TO NEXT LOOP
    else:
        logger.debug('List l_flag_files_with_path is EMPTY.')


    # -- FLAG FILE IS NOT PRESENT
    # -- QUALIFY FLAG-FILE WAS NOT FOUND BECAUSE AS SOON AS IT FOUND IN FOR-LOOP return STATEMENT IS RUN
    # -- SO I AM retun'ING 'FAILED' EVENT
    r_event = {
        "YES_NO": "NO",  # -- FLAG FILE WAS NOT FOUND
        "FLAG-FILE-WITH-PATH": 'PLACEHOLDER',
        "SAS-FILE-WITH-PATH": 'PLACEHOLDER',
        "LOGDIR-WITH-PATH": 'PLACEHOLDER',
        "PRD-FILES-WITH-PATH": 'PLACEHOLDER',
        "COMPRESS-PRD": False
    } 
    return r_event
#----------------------------------------------------------

