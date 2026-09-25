
import os
import ftplib
import logging
import z_config


#----------------------------------------------------------
def f_ftp_one_file(f_ftp_hostname,
                  f_ftp_user,
                  f_ftp_pass,
                  f_ftp_remote_folder,
                  f_file_to_ftp):

    # my_local_dir_with_path, my_local_filename_without_path = os.path.split(f_file_to_ftp)
    my_local_dir_with_path = os.path.dirname(f_file_to_ftp)
    
    print(f"FTP-HOST:               {f_ftp_hostname}")
    print(f"DIR-WHERE-FILE-TO-FTP:  {my_local_dir_with_path}")
    print(f"FILE-TO-FTP-WITH-PATH:  {f_file_to_ftp}")

    ftp = ftplib.FTP(f_ftp_hostname)
    ftp.set_debuglevel(1)
    # ftp.set_debuglevel(3)
    ftp.login(f_ftp_user, f_ftp_pass)
    ftp.cwd(f_ftp_remote_folder)
    ftp.pwd()
    # ftp.dir()

    cur_directory = os.getcwd()
    os.chdir(my_local_dir_with_path)

    # Unfortunately, what FTP calls text is still bytes for Python 3. 
    # Python 3 strings use Unicode characters that need to be encoded to bytes 
    # in order to be written to files and FTP deals with files. 
    # But here it is even simpler: you have just to open the local file in binary mode ('rb') to have it deliver bytes instead of strings:

    with open(f_file_to_ftp,'rb') as my_local_file_opened_as_object:      # use binary mode for file
        # f_file_to_ftp = /tmp/PROD.FTP.AMR.SAS.SCORE.AWS
        my_local_filename_without_path = os.path.basename(f_file_to_ftp)
        # my_local_filename_without_path = PROD.FTP.AMR.SAS.SCORE.AWS
        try:
            # ftp.storlines('STOR ' + my_local_filename_without_path, my_local_file_opened_as_object)
            # ftp.storlines("APPE '" + my_local_filename_without_path + "'", my_local_file_opened_as_object)
            ftp.storlines(f"APPE '{my_local_filename_without_path}'", my_local_file_opened_as_object)
            print(f'SUCCESS: FILE-TO-FTP-WITH-PATH {f_file_to_ftp} was uploaded.')
        except Exception as e:
            print(f'ERROR: FILE-TO-FTP-WITH-PATH {f_file_to_ftp} was NOT uploaded.')
            print(f"{e.message}\n {e.args}\n")
            return 'FAILED'


    ftp.quit()
    # my_local_file_opened_as_object.close()

    os.chdir(cur_directory)

    return 'SUCCESS'
#----------------------------------------------------------

