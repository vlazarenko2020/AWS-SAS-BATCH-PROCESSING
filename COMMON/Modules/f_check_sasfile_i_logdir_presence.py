
import os
import logging
import z_config

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')

#----------------------------------------------------------
def f_check_sasfile_i_logdir_presence(f_current_flag_file_with_path):

    r_event = {}
              
    (current_flag_dir_with_path, current_flag_file_without_path) = os.path.split(f_current_flag_file_with_path )

    cur_sas_file_without_path = current_flag_file_without_path.replace('.PRD.FLAG', '.sas')
    cur_dir_of_sas_file   = z_config.f_get_prog_config(current_flag_dir_with_path)['path_to_sasfile']
    cur_sas_file_with_path   = os.path.join(cur_dir_of_sas_file,
                                        cur_sas_file_without_path)

    # logger.debug(f'CUR-SAS-FILE-BEZ-PATH: {cur_sas_file_without_path}')
    # logger.debug(f'CUR-SAS-FILE-WITH-PATH:   {cur_sas_file_with_path}')

    if os.path.exists(cur_sas_file_with_path):

        logger.debug(f'CUR-SAS-FILE-WITH-PATH: ({cur_sas_file_with_path}) EXISTS.')
        cur_log_dir_with_path = z_config.f_get_prog_config(current_flag_dir_with_path)['path_to_logfile']

        if os.path.exists(cur_log_dir_with_path ):

            logger.debug(f'CUR-LOGDIR-WITH-PATH: ({cur_log_dir_with_path}) EXISTS.')
            r_event = {
                "YES_NO": 'YES',
                "SAS-FILE-WITH-PATH": cur_sas_file_with_path,
                "LOGDIR-WITH-PATH": cur_log_dir_with_path
            }
        else:
            logger.debug(f"CUR-LOGDIR-WITH-PATH: ({cur_log_dir_with_path}) DOESN'T EXIST.")
            r_event = {
                "YES_NO": 'NO',
                "SAS-FILE-WITH-PATH": '',
                "LOGDIR-WITH-PATH": ''
            }
    else:
        logger.debug(f"CUR-SAS-FILE-WITH-PATH: ({cur_sas_file_with_path}) DOESN'T EXISTS.")
        r_event = {
            "YES_NO": 'NO',
            "SAS-FILE-WITH-PATH": '',
            "LOGDIR-WITH-PATH": ''
        }
    return r_event
#----------------------------------------------------------

