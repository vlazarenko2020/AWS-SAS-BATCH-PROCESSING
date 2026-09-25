
import os
import shutil

import z_config
from Modules.ClassParameterStore import ClassParameterStore
from Modules.f_ftp_one_file import f_ftp_one_file

import logging
import z_config

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')


#----------------------------------------------------------
def f_ftp_scoring_status_file_to_mainframe(f_dir_with_flag_files,
                                          f_current_prd_file_with_path ):

    if os.path.exists(f_current_prd_file_with_path):

        # --------------------------------------------------------------------------------
        file_with_aws_key = z_config.f_get_prog_config(f_dir_with_flag_files)['path_to_aws_key']
        with open(file_with_aws_key) as f:
            lines = f.readlines()
            aws_access_key_id      = lines[0].rstrip()
            aws_secret_access_key  = lines[1].rstrip()
        # --------------------------------------------------------------------------------

        ftp_connection_param_store_entry = z_config.f_get_prog_config(f_dir_with_flag_files)['path_to_ftp']
        logger.debug(f'PARAMETER-STORE-FTP-ENTRY: {ftp_connection_param_store_entry}')
        logger.debug(f'aws_access_key_id:         {aws_access_key_id}')
        # logger.debug(f'aws_secret_access_key:     {aws_secret_access_key}')

        # --------------------------------------------------------------------------------
        iClassParameterStore = ClassParameterStore(aws_access_key_id,
                                                    aws_secret_access_key,
                                                    ftp_connection_param_store_entry)
        d_parameter = iClassParameterStore.get_parameter_as_dic()
        # --------------------------------------------------------------------------------
        f_ftp_hostname        = d_parameter['host']
        f_ftp_user            = d_parameter['user']
        f_ftp_pass            = d_parameter['pass']
        f_ftp_remote_filename = d_parameter['file']
        f_ftp_remote_folder   = d_parameter['folder'] 
        
        logger.debug('')
        logger.debug(f'f_ftp_hostname        {f_ftp_hostname}')
        logger.debug(f'f_ftp_user            {f_ftp_user}')
        logger.debug(f'f_ftp_pass            {f_ftp_pass}')
        logger.debug(f'f_ftp_remote_filename {f_ftp_remote_filename}')    # PROD.FTP.AMR.SAS.SCORE.STATUS
        logger.debug(f'f_ftp_remote_folder   {f_ftp_remote_folder}')
        logger.debug('')
        
        f_ftp_remote_filename_with_local_path = '/tmp/' + f_ftp_remote_filename
        # /tmp/PROD.FTP.AMR.SAS.SCORE.STATUS
        
        try:
            shutil.copy( f_current_prd_file_with_path, f_ftp_remote_filename_with_local_path )
        except Exception as e:
            logger.debug(f'FAILED TO COPY {f_current_prd_file_with_path} TO {f_ftp_remote_filename_with_local_path}')
            logger.debug(e)
            return 'FTP FAILED'
        
        SUCCESS_FAILED = f_ftp_one_file( f_ftp_hostname      = f_ftp_hostname,
                                        f_ftp_user          = f_ftp_user,
                                        f_ftp_pass          = f_ftp_pass,
                                        f_ftp_remote_folder = f_ftp_remote_folder,
                                        f_file_to_ftp       = f_ftp_remote_filename_with_local_path)

        if SUCCESS_FAILED == 'SUCCESS':
            logger.debug('' )
            logger.debug('FTP COMPLETED WITH SUCCESS.' )
            logger.debug('' )
            return 'FTP SUCCESS'
        else:
            logger.debug('' )
            logger.debug('FTP FAILED.' )
            logger.debug('' )
            return 'FTP FAILED'
    else:
        logger.debug(f"FILE TO FTP TO MAINFRAME {f_current_prd_file_with_path} DOESN'T EXIST. FTP WILL NOT BE DONE." )
        return 'FTP FAILED'
    return 'FTP SUCCESS'  
#----------------------------------------------------------
