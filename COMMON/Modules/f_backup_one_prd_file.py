
import os
import shutil

import logging
import z_config


logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')


#   -----------------------------------------------------------------------------------------------------------
def f_backup_one_prd_file(f_file_prd_with_path):

    # Only one filename is passed as an argument (f_file_prd_with_path).

    if os.path.exists(f_file_prd_with_path):

        folder_destination_for_gziped_PRD = z_config.folder_destination_for_gziped_PRD

        if os.path.exists(folder_destination_for_gziped_PRD):

            try:
                shutil.move(f_file_prd_with_path, os.path.join(folder_destination_for_gziped_PRD, os.path.basename(f_file_prd_with_path)))
                logger.debug(f'.PRD FILE ({f_file_prd_with_path}) WAS MOVED TO BACKUP FOLDER ({folder_destination_for_gziped_PRD}).')
            except Exception as e:
                logger.debug(f'WARNING: .PRD FILE ({f_file_prd_with_path}) WAS NOT MOVED TO ({folder_destination_for_gziped_PRD})')
                logger.debug(e)
                return 'WARNING'
        else:
            logger.debug(f"WARNING: DESTINATION FOLDER FOR .PRD FILES ({folder_destination_for_gziped_PRD}) DOESN'T EXIST.")
            return 'WARNING'
    else:
        logger.debug(f"WARNING: .PRD FILES ({f_file_prd_with_path}) DOESN'T EXIST.")
        return 'WARNING'

    return 'SUCCESS'

        # l_file_prd_with_path = [f_file_prd_with_path]

        # l_komanda = [z_config.l_gzip_bin_with_parameters,
        #             *l_file_prd_with_path]

        # l_komanda = []
        # l_komanda.extend(z_config.l_gzip_bin_with_parameters)
        # l_komanda.append(f_file_prd_with_path)

        # logger.debug('')
        # logger.debug("COMMAND:")
        # logger.debug(l_komanda)
        # logger.debug('')

        # # -- BEZ microseconds
        # time_start = datetime.now().replace(microsecond=0)

        # vivod = subprocess.run(l_komanda,
        #                         stdout=subprocess.PIPE,
        #                         stderr=subprocess.STDOUT,
        #                         shell=False)
        
        # # -- BEZ microseconds
        # time_end = datetime.now().replace(microsecond=0)

        # time_skolko_vremeni_rabotalo = time_end - time_start

        # logger.debug('')
        # logger.debug(f'ReturnCode: {vivod.returncode}')
        # logger.debug(vivod.stdout)
        # logger.debug('')
        # logger.debug(f'The compress (gzip) program ran for ({str(time_skolko_vremeni_rabotalo)}) seconds')
        # logger.debug('')


        # #   -- Checking if gzip WAS SUCCESSFULL.

        # f_expected_file_prd_with_path = f_file_prd_with_path + '.gz'

        # if os.path.exists( f_expected_file_prd_with_path ):
        #     logger.debug(f'THE COMPRESS (gzip) WAS SUCCESSFULL.')
        #     logger.debug(f'COMPRESSED .PRD.gz FILE {f_expected_file_prd_with_path} WAS CREATED.')
        #     #   -- NOTIFY MOVE_PRD_FILE_PROGRAMM ABOUT COMPRESSED FILE .PRD FILE CREATION
        #     #   -- CREATING .FBACKUP FILE

        #     flagfile_for_move_gzip_prd_to_backup = f_file_prd_with_path + '.FBACKUP'

        #     logger.debug(f'CREATING FBACKUP-FLAG-FILE ({flagfile_for_move_gzip_prd_to_backup}) TO TELL THAT .PRD.gz WAS CREATED.')

        #     with open( flagfile_for_move_gzip_prd_to_backup, 'w') as f:
        #         f.write(str(datetime.now().replace(microsecond=0)))

        # #   -- Checking if .FBACKUP FILE WAS CREATED SUCCESSFULLY.

        #     if os.path.exists( flagfile_for_move_gzip_prd_to_backup ):
        #         logger.debug(f'FBACKUP FILE {flagfile_for_move_gzip_prd_to_backup} WAS CREATED.')
        #         return 'SUCCESS'
        #     else:
        #         logger.debug('FBACKUP FILE {flagfile_for_move_gzip_prd_to_backup} WAS NOT CREATED.')
        #         return 'ERROR'
        # else:
        #     logger.debug(f'THE COMPRESS (gzip) FAILED.')
        #     logger.debug(f'COMPRESSED .PRD.gz FILE {f_expected_file_prd_with_path} WAS NOT CREATED.')
        #     logger.debug(f'.PRD FILE {f_file_prd_with_path} WILL NOT BE MOVED. IT IS AVAILABLE TO RE-RUN.')
        #     logger.debug('FBACKUP FILE {flagfile_for_move_gzip_prd_to_backup} WILL NOT BE CREATED.')
        #     return 'ERROR'
#   -----------------------------------------------------------------------------------------------------------

