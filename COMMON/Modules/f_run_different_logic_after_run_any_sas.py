

from Modules.f_backup_one_prd_file import f_backup_one_prd_file
from Modules.f_ftp_scoring_status_file_to_mainframe import f_ftp_scoring_status_file_to_mainframe

import logging

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')


#   -----------------------------------------------------------------------------------------------------------
def f_run_different_logic_after_run_any_sas(f_folder_with_flag_file,
                                            f_l_prd_files_with_path,
                                            f_y_n_error_in_log,
                                            f_should_I_compress_prd_files):   # f_should_I_compress_prd_files - can be False/True

    # ------------------------------------------------------------------------------------------
    # FTP SCORING .PRD FILE TO MAINFRAME ONLY FOR /sas01/sasdata/PROD/scoring/code_2
    # FTP HAS TO BE BEFORE compress BECASE WE FTP NON-COMPRESSED .PRD FILE
    if f_folder_with_flag_file == '/sas01/sasdata/PROD/scoring/code_2' or f_folder_with_flag_file == '/sas01/sasdata/DEV-PROCESSING/DBM_scoring_code2':
    
        logger.debug(f'FOLDER-WITH-FLAG-FILES ARE ({f_folder_with_flag_file})')

        for cur_prd_files_with_path in f_l_prd_files_with_path:
            logger.debug(f'FTPING .PRD FILE ({cur_prd_files_with_path}) TO MAINFRAME')

            current_ftp_status = f_ftp_scoring_status_file_to_mainframe(f_folder_with_flag_file, 
                                                                    cur_prd_files_with_path)      
            if current_ftp_status == 'FTP SUCCESS':
                logger.debug(f'FTP-SUCCESS: SCORING .PRD FILE ({cur_prd_files_with_path}) WAS FTPed TO MAINFRAME.')
            else:
                logger.debug(f'FTP-ERROR: SCORING .PRD FILE ({cur_prd_files_with_path}) WAS NOT FTPed TO MAINFRAME.')
    
    else:
        pass
    # ------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------
    # -- NEED TO COMPRESS .PRD FILES -- IF .PRD FILES LIST WAS PASSED TO THE CLASS
    # -- SOME .sas PROGRAMS CAN BE EXECUTED WITHOUT .PRD FILE(S). SO THERE WILL BE NOTHING TO COMPRESS AND MOVE
    # -- ALSO IF THERE WERE ERRORS IN SAS .log FILE -- PERNELL WILL RE-SUBMIT .FLAG FILE AND NOT .PRD FILE -- SO .PRD FILES HAVE TO BE LEFT IN THEIR ORIGINAL LOCATION

    # THERE ARE NO ERRORS IN SAS-LOG-FILE -- f_y_n_error_in_log = "SUCCESS"
    # THERE ARE    ERRORS IN SAS-LOG-FILE -- f_y_n_error_in_log = "ERROR"
    # E-MAIL WAS NOT SENT                 -- f_y_n_error_in_log = "WARNING"
    if f_y_n_error_in_log == 'SUCCESS':
        if len(f_l_prd_files_with_path) != 0 and f_should_I_compress_prd_files:   # f_should_I_compress_prd_files - can be False/True

            logger.debug('THERE ARE .PRD FILES TO MOVE AND COMPRESS.')
            for cur_prd_files_with_path in f_l_prd_files_with_path:
                # ------------------------------------------------------------
                f_backup_one_prd_file(cur_prd_files_with_path)
                # ------------------------------------------------------------
        else:
            logger.debug('THERE ARE NO .PRD FILES TO MOVE AND COMPRESS.')
            logger.debug('OR "NO NEED CO COMPRESS" WAS PASSED TO THE CLASS.')
    else:
        logger.debug('THERE WERE ERRORS IN .SAS PROGRAM.')
        logger.debug('ALL .PRD FILES WILL BE LEFT IN THEIR ORIGINAL LOCATION IN ORDER TO AVOID THEIR FTP TRANSFER FOR .FLAG FILE RE-SUBMITION.')
    # ------------------------------------------------------------------------------------------

