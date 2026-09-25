
import os
import datetime
import logging
import z_config

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')

#----------------------------------------------------------
def f_file_i_am_working(f_thread_number, f_dir_with_flag_files):

    r_event = {}
    logger.debug(f'z_config.m_dir_base             = {z_config.m_dir_base}')
    logger.debug(f'z_config.m_suffiks_i_am_working = {z_config.m_suffiks_i_am_working}')
    f_systemname = z_config.f_get_prog_config(f_dir_with_flag_files)['path_to_systemname']
    logger.debug(f'z_config.f_get_prog_config(f_dir_with_flag_files)["path_to_systemname"] = {f_systemname}')

    if os.path.exists(z_config.m_dir_base):
        logger.debug(f'FOLDER FOR I-AM-WORKING-FILE ({z_config.m_dir_base}) EXISTS.')
    else:
        logger.debug(f"FOLDER FOR I-AM-WORKING-FILE ({z_config.m_dir_base}) DOESN'T EXIST. EXITING.")
        exit()

    f_file_i_am_working_with_path  = f'{z_config.m_dir_base}/___{f_systemname}{z_config.m_suffiks_i_am_working}_{str(f_thread_number)}'

    logger.debug(f'file_i_am_working_with_path = {f_file_i_am_working_with_path}')

    if os.path.exists(f_file_i_am_working_with_path):
        logger.debug(f'I-AM-WORKING-FILE ({f_file_i_am_working_with_path}) EXISTS. IT MEANS ONE TREAD IS ALREADY RUNNING. EXITING.')
        exit()
    else:
        logger.debug(f"I-AM-WORKING-FILE ({f_file_i_am_working_with_path}) DOESN'T EXIST. WILL RUN THIS TREAD.")
        logger.debug(f'CREATING I-AM-WORKING-FILE ({f_file_i_am_working_with_path}) FOR TREAD {str(f_thread_number)}')

        # --- save START_TIME to I_AM_WORKING FILE
        f_current_date_time     = datetime.datetime.now()
        f_current_date_time_str = f_current_date_time.strftime('%Y-%m-%d_%H_%M')

        # ----------------------------------------------------------------------------------------
        with open(f_file_i_am_working_with_path, 'w+') as f:
          logger.debug(f'SAVING START TIME TO I-AM-WORKING-FILE: {f_current_date_time_str}')
          f.write(f'{f_current_date_time_str}\n')
        # ----------------------------------------------------------------------------------------

        r_event["I-AM-WORKING-FILE"] = f_file_i_am_working_with_path
        return r_event
#----------------------------------------------------------

