#!/usr/bin/python -tt
#


import sys
import os
import logging
import getpass
from datetime import datetime, time, timedelta
import subprocess
import re

sys.path.append('/usr/local/vbin/common_py')
# from m_mail_send_WITHOUT_attach_html import mail_send_WITHOUT_attach_html
from Modules.m_mail_send_ONE_attach import ClassMailSend

import z_config

##### --- MOVE COMPRESS TO    sas_ftp_processing_root
#import f_gzip_prd_file_if_it_was_passed_as_argument

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')


class ClassSASProgram():

#   -----------------------------------------------------------------------------------------------------------
  def __init__(self,
              c_event):

      # Need three OR four (fourth parameter is optional) arguments:
      # 1) sas_file_with_path
      # 2) log_dir_with_path
      # 3) mail_file_base_with_path
      # 4) l_prd_files_with_path -- if .PRD files are needed to be compressed. It is a list because it can be more than one .PRD file for one .FLAG file

      self.system_short_name     = c_event["SYSTEM-SHORT-NAME"] # -- need to get access to log cur program folder
      self.sas_file_with_path       = c_event["SAS-FILE-WITH-PATH"]
      self.log_dir_with_path        = c_event["LOGDIR-WITH-PATH"]
      self.mail_file_base_with_path = c_event["FILE MAIL SENDERS"]
      # WILL NOT CHECK IF .PRD FILE EXISTS
      # SOME .SAS PROGRAMS WILL RUN WITHOUT .PRD FILE
      # CAN ADD function FOR CHECKING FOR ONE OR MORE .PRD FILES.
      self.l_prd_files_with_path   = c_event["LIST-PRD-FILES-WITH-PATH"]   # -- the list can be empty if we don't need .PRD files. I am checking the list later in .PRD move section.
      self.history_file_with_path  = f"log-{self.system_short_name}/history.log"

      logger.debug(f'SAS program file:   {self.sas_file_with_path}')
      logger.debug(f'Log dir:            {self.log_dir_with_path}')
      logger.debug(f'Mail file:          {self.mail_file_base_with_path}')
      logger.debug(f'SAS PRD files:      {self.l_prd_files_with_path}')

      # ------------------------------------------------------------
      self.f_check_arguments()
      # -- IF SOMETHING DOESN'T EXIST -- THERE WILL BE exit() FROM WHOLE PROGRAM
      # ------------------------------------------------------------

      (self.sas_file_dir, self.sas_file_without_path) = os.path.split(self.sas_file_with_path)
      # -- GET THE NAME OF CURRENT RUNNING .py PROGRAM
      self.cur_py_prog_name = os.path.basename(__file__)
      # -- GET USERNAME WHO STARTED THIS .py PROGRAM
      self.os_user_started_this_prog = getpass.getuser()

      # -- CHECK IF USER (whoami) WHO STARTED THIS PROG IS ALLOWED TO DO THIS
      # -- z_config.m_allowed_users KEEPS THE LIST OF ALLOWED LINUX USERS
      if self.os_user_started_this_prog in z_config.m_allowed_users:
        logger.debug(f'CURRENT USER ({self.os_user_started_this_prog}) IS ALLOWED TO RUN THIS PROGRAM.')
      else:
        logger.debug(f'CURRENT USER ({self.os_user_started_this_prog}) IS NOT ALLOWED TO RUN THIS PROGRAM.')
        exit()

    # -- a_file_mail_with_path --- ITS EXISTANCE WAS CHECKED IN self.f_check_arguments()

      self.to_addr_list = []
      self.to_addr_list, self.from_full_string = self.f_fill_list_of_mail_recipients_and_from()
      self.mail_config = z_config.f_get_prog_config(self.system_short_name)['mail']
      self.l_gzip_bin_with_parameters = z_config.l_gzip_bin_with_parameters


#   -----------------------------------------------------------------------------------------------------------



#   -----------------------------------------------------------------------------------------------------------
  def f_check_arguments(self):

      if os.path.exists(self.sas_file_with_path):
        logger.debug('FILE ' + self.sas_file_with_path + ' EXISTS.')
      else:
        logger.debug(f"ERROR: FILE {self.sas_file_with_path} DOESN'T EXIST. EXITING.")
        return "FAILURE"
        exit()

      if os.path.exists(self.log_dir_with_path):
        logger.debug(f'FOLDER {self.log_dir_with_path} EXISTS.')
      else:
        logger.debug(f"ERROR: FOLDER {self.log_dir_with_path} DOESN'T EXIST. EXITING.")
        return "FAILURE"
        exit()

      f_file_mail_recipients_with_path = self.mail_file_base_with_path + '.USERS'
      f_file_mail_from_with_path     = self.mail_file_base_with_path + '.FROM'

      if os.path.exists(f_file_mail_recipients_with_path):
        logger.debug(f'FILE {f_file_mail_recipients_with_path} EXISTS.')
      else:
        logger.debug(f"ERROR: FILE {f_file_mail_recipients_with_path} DOESN'T EXIST. EXITING.")
        return "FAILURE"
        exit()

      if os.path.exists(f_file_mail_from_with_path):
        logger.debug(f'FILE {f_file_mail_from_with_path} EXISTS.')
      else:
        logger.debug(f"ERROR: FILE {f_file_mail_from_with_path} DOESN'T EXIST. EXITING.")
        return "FAILURE"
        exit()
#   -----------------------------------------------------------------------------------------------------------


#   -----------------------------------------------------------------------------------------------------------
  def f_fill_list_of_mail_recipients_and_from(self):

      f_file_mail_recipients_with_path = self.mail_file_base_with_path  + '.USERS'
      f_file_mail_from_with_path     = self.mail_file_base_with_path  + '.FROM'

      logger.debug('f_file_mail_recipients_with_path = ' + f_file_mail_recipients_with_path)
      logger.debug('f_file_mail_from_with_path     = ' + f_file_mail_from_with_path)

      with open(f_file_mail_recipients_with_path) as temp_file:
        f_list_emails = [line.rstrip('\n') for line in temp_file]
        logger.debug('f_list_emails: ')
        logger.debug(f_list_emails)

      with open(f_file_mail_from_with_path) as temp_from_file:
        f_list_from = [line.rstrip('\n') for line in temp_from_file]

      # -- I NEED ONLY FIRST LINE IN FILE. IT IS from full line.
      f_from_full_string = f_list_from[0]
      logger.debug('f_from_full_string = ' + f_from_full_string)

      logger.debug('')
      logger.debug('MAIL RECIPIENTS:')
      logger.debug(f_list_emails)
      logger.debug('')

      logger.debug('')
      logger.debug(f'FROM-FIELD-FULL: {f_from_full_string}')
      logger.debug('')

      return f_list_emails, f_from_full_string
#   -----------------------------------------------------------------------------------------------------------


# #   -----------------------------------------------------------------------------------------------------------
#   def f_chek_logfile_for_errors(self,
#                               ff_file_log_with_path):
#     # -- logfile exists -- this was checked earlier
#     f_obrazec_dly_poiska = b"ERROR: "
#     # f_obrazec_dly_poiska =  "ERROR: "

#     with open(ff_file_log_with_path, "r") as f:
#         f_y_n_error_in_log = "SUCCESS"
#         for line in f.readlines():
#           line_fixed = line.encode('utf-8').strip()
#           if re.match(f_obrazec_dly_poiska, line_fixed):
#               logger.debug('LINE WITH ERROR:\n' + line)
#               f_y_n_error_in_log = "ERROR"

#     return f_y_n_error_in_log
# #   -----------------------------------------------------------------------------------------------------------
# #   -----------------------------------------------------------------------------------------------------------
#   def f_chek_logfile_for_errors(self,
#                               ff_file_log_with_path):
#     # -- logfile exists -- this was checked earlier
#     f_obrazec_dly_poiska = b"ERROR: "
#     # f_obrazec_dly_poiska =  "ERROR: "

#     with open(ff_file_log_with_path, "rb") as f:
#         f_y_n_error_in_log = "SUCCESS"
#         for line in f.readlines():
#           if re.match(f_obrazec_dly_poiska, line):
#               logger.debug('LINE WITH ERROR:\n' + line.decode('utf-8'))
#               f_y_n_error_in_log = "ERROR"

#     return f_y_n_error_in_log
# #   -----------------------------------------------------------------------------------------------------------
#   -----------------------------------------------------------------------------------------------------------
  def f_chek_logfile_for_errors(self,
                              ff_file_log_with_path):
    # -- logfile exists -- this was checked earlier
    f_obrazec_dly_poiska = "ERROR: "

    # l_komanda = ['cat', ff_file_log_with_path, '|', 'grep', f"{f_obrazec_dly_poiska}", '|', 'wc', '-l']
    # logger.debug('')
    # logger.debug(l_komanda)
    # logger.debug('')
    # vivod = subprocess.run(l_komanda,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.STDOUT,
    #                       shell=False)

    komanda = f'cat {ff_file_log_with_path} | grep "{f_obrazec_dly_poiska}" | wc -l'
    logger.debug('')
    logger.debug(komanda)
    logger.debug('')
    vivod = subprocess.run(komanda,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          shell=True)

    logger.debug('')
    logger.debug(f'ReturnCode: {vivod.returncode}')
    logger.debug(f'Output:     {vivod.stdout.strip()}')
    logger.debug('')
    if vivod.returncode == 0:
      if vivod.stdout.strip() != b'0':
        return "ERROR"
      else:
        return "SUCCESS"
    else:
      return "ERROR"




#   -----------------------------------------------------------------------------------------------------------
  def f_send_email_or_post_to_webhook(self,
                              f_event_for_email_webhook):

      # f_event_for_email_webhook = {
      #   "FROM ADDRESS": self.mail_config['from'],
      #   "TO ADDRESS": self.mail_config['to'],
      #   "CC ADDRESS LIST": [],
      #   "SMTP SERVER": self.mail_config['SMTP']
      #   "SUBJECT": c_subject,
      #   "BODY": None,
      #   "LOGFILE TO ATTACH": f_file_log_with_path,
      #   "PROG RUNNING TIME": time_skolko_vremeni_rabotalo}

      if f_event_for_email_webhook["BODY"] is None:
          prom_telo = f'<HTML><BODY><PRE>\nRunning time: H:MM:SS - {str(f_event_for_email_webhook["PROG RUNNING TIME"])}\n\n</PRE></BODY></HTML>'
      else:
          prom_telo = f'<HTML><BODY><PRE>\nRunning time: H:MM:SS - {str(f_event_for_email_webhook["PROG RUNNING TIME"])}\n\n{f_event_for_email_webhook["BODY"]}\n</PRE></BODY></HTML>'

      # -- Need to handle if there is no log-file to attach
      # if f_event_for_email_webhook["LOGFILE TO ATTACH"] is None:
      # else:
       

      try:
          if self.mail_config['SMTP'] == 'SES':
              ClassMailSend.mail_send_ONE_attach_SES(f_from_addr    = self.mail_config['from'],
                                  f_to_addr_list = self.mail_config['to'],
                                  f_cc_addr_list = [],
                                  f_subject      = f_event_for_email_webhook["SUBJECT"],
                                  f_telo         = prom_telo,
                                  f_file_to_attach_with_path = f_event_for_email_webhook["LOGFILE TO ATTACH"])
          else:
              ClassMailSend.mail_send_ONE_attach(f_from_addr    = self.mail_config['from'],
                                  f_to_addr_list = self.mail_config['to'],
                                  f_cc_addr_list = [],
                                  f_subject      = f_event_for_email_webhook["SUBJECT"],
                                  f_telo         = prom_telo,
                                  f_file_to_attach_with_path = f_event_for_email_webhook["LOGFILE TO ATTACH"],
                                  f_smtpserver   = self.mail_config['SMTP'])
          f_email_send_status = "SUCCESS"
      except Exception as e:
          f_email_send_status = "ERROR"
          logger.debug(e)

      return f_email_send_status
#   -----------------------------------------------------------------------------------------------------------


#   -----------------------------------------------------------------------------------------------------------
  def f_run_sas_program(self):

      f_file_log_without_path = self.sas_file_without_path.split(".sas")[0] + '.log'
      f_file_log_with_path   = self.log_dir_with_path + '/' + f_file_log_without_path

      logger.debug(f'f_file_log_without_path = {f_file_log_without_path}')
      logger.debug(f'f_file_log_with_path   = {f_file_log_with_path}')

      if os.path.exists(f_file_log_with_path):
          date_str = datetime.now().strftime('%Y%m%d%H%M%S')
          logger.debug(f'SAS LOGFILE {f_file_log_with_path} EXISTS. IT IS GOING TO BE REMANED TO {f_file_log_with_path}-{date_str}')
          os.rename(f_file_log_with_path, f'{f_file_log_with_path}-{date_str}')
      else:
          logger.debug(f"SAS LOGFILE ({f_file_log_with_path}) DOESN'T EXIST.")

      # sas_bin = '/sas/sasbin94/sashome/SASFoundation/9.4/sas'
      sas_bin = z_config.sas_bin

      sas_arguments = ['-work',
                       self.log_dir_with_path,
                       '-log',
                       self.log_dir_with_path,
                       '-print',
                       self.log_dir_with_path,
                       '-sysin',
                       self.sas_file_with_path,
                       '-nodms']

      l_komanda = [sas_bin,
                *sas_arguments]
      logger.debug('')
      logger.debug("COMMAND:")
      logger.debug(l_komanda)
      logger.debug('')



      if os.path.exists(self.history_file_with_path):
          append_write = 'a' # append if already exists
      else:
          append_write = 'w' # make a new file if not

      print(f"append_write = {append_write}")

      with open(self.history_file_with_path, append_write) as fh:
          # -- BEZ microseconds
          time_start = datetime.now().replace(microsecond=0)
          prom_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          # -- write to file - beginning of a line
          sas_file_without_path_and_ext = os.path.splitext(os.path.basename(self.sas_file_with_path))[0]
          prom_stage_for_history = 'STARTED'
          prom_sas_job_status_for_history = '-'
          fh.write(f"{time_start},{self.system_short_name},{sas_file_without_path_and_ext},{self.sas_file_with_path},{self.log_dir_with_path},{self.mail_file_base_with_path},'-',{prom_stage_for_history},'-',{prom_sas_job_status_for_history}\n")
          # 2022-06-06 23:06:02,DBM_scoring_inputs,MODEL_INFO,/sas01/sasdata/PROD/scoring/code_1/MODEL_INFO.sas,/sas01/sasdata/PROD/scoring/inputs_log,./info/PROD/EMSERVICEUSER_SCORING_INPUTS,-,START,-,-


      prom_sas_job_status_for_history = 'SUCCESS'
      try:
          vivod = subprocess.run(l_komanda,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=False)
          # vivod = os.popen(komanda).read()
      except Exception as e:
          logger.debug(f'ERROR: Command {l_komanda} FAILED.')
          logger.debug(f"{e.message}\n {e.args}\n")
          prom_sas_job_status_for_history = 'FAILED'

      prom_stage_for_history = 'COMPLETED'
      time_end = datetime.now().replace(microsecond=0)
      # -- BEZ microseconds
      time_end = datetime.now().replace(microsecond=0)
      time_skolko_vremeni_rabotalo = time_end - time_start
      # -- write to file - end of the line
      with open(self.history_file_with_path, append_write) as fh:
          fh.write(f"{time_start},{self.system_short_name},{sas_file_without_path_and_ext},{self.sas_file_with_path},{self.log_dir_with_path},{self.mail_file_base_with_path},{time_end},{prom_stage_for_history},{str(time_skolko_vremeni_rabotalo)},{prom_sas_job_status_for_history}\n")
          # 2022-06-06 23:06:02,DBM_scoring_inputs,MODEL_INFO,/sas01/sasdata/PROD/scoring/code_1/MODEL_INFO.sas,/sas01/sasdata/PROD/scoring/inputs_log,./info/PROD/EMSERVICEUSER_SCORING_INPUTS,2022-06-06 23:16:02,COMPLETED,SUCCESS
          # 2022-06-06 23:06:02,DBM_scoring_inputs,MODEL_INFO,/sas01/sasdata/PROD/scoring/code_1/MODEL_INFO.sas,/sas01/sasdata/PROD/scoring/inputs_log,./info/PROD/EMSERVICEUSER_SCORING_INPUTS,2022-06-06 23:16:02,COMPLETED,FAILED

      logger.debug('')
      logger.debug(f'ReturnCode: {vivod.returncode}')
      logger.debug(vivod.stdout)
      logger.debug('')
      logger.debug(f'The SAS program runs for ({str(time_skolko_vremeni_rabotalo)}) seconds')
      logger.debug('')



      # WILL NOT USE vivod.stdout FOR PROGRAM SUCCESS/FAILURE
      # WILL CHECK IF SAS-LOG-FILE WAS CREATED
      # IF IT WAS CREATED -- SUCCESS
      # IF IT WAS NOT CREATED -- ERROR

      if os.path.exists(f_file_log_with_path):
          logger.debug(f'NEW SAS LOGFILE ({f_file_log_with_path} HAS BEEN CREATED. WILL CHECK IT FOR ERRORS.')
          # ------------------------------------------------------------
          y_n_error_in_log = self.f_chek_logfile_for_errors(f_file_log_with_path)
          # possible values: "ERROR", "SUCCESS"( IN CASE OF NO-ERROR)
          # ------------------------------------------------------------
          #   return:
          #   - ERROR
          if y_n_error_in_log == 'ERROR':
              logger.debug('')
              logger.debug('SENDING ERROR E-MAIL.')
              logger.debug('')
              c_subject = f'SAS-ERROR {self.os_user_started_this_prog} - {self.sas_file_without_path}'
          else:
              # y_n_error_in_log = 'SUCCESS'  -- IT WAS SET IN self.f_chek_logfile_for_errors(f_file_log_with_path)
              logger.debug('')
              logger.debug('SENDING SUCCESS E-MAIL.')
              logger.debug('')
              c_subject = f'SAS-SUCCESS {self.os_user_started_this_prog} - {self.sas_file_without_path}'



          event_for_email_webhook = {
            "FROM ADDRESS": self.mail_config['from'],
            "TO ADDRESS": self.mail_config['to'],
            "CC ADDRESS LIST": [],
            "SMTP SERVER": self.mail_config['SMTP'],
            "SUBJECT": c_subject,
            "BODY": None,
            "LOGFILE TO ATTACH": f_file_log_with_path,
            "PROG RUNNING TIME": time_skolko_vremeni_rabotalo
          }
          email_send_status = self.f_send_email_or_post_to_webhook(event_for_email_webhook)

      else: # Log file was not created

          c_subject = f'SAS-WARNING {self.os_user_started_this_prog} - {self.sas_file_without_path}'
          c_message_for_body = f' NEW SAS LOGFILE ({f_file_log_with_path} WAS NOT CREATED.\n SOMETHING WAS WRONG.\n CANNOT CONFIRM THAT THE .sas PROGRAM RUN WAS SUCCESSFULL.'
          logger.debug(c_message_for_body)  # -- USED ALSO IN event_for_email_webhook

          event_for_email_webhook = {
            "FROM ADDRESS": self.mail_config['from'],
            "TO ADDRESS": self.mail_config['to'],
            "CC ADDRESS LIST": [],
            "SMTP SERVER": self.mail_config['SMTP'],
            "SUBJECT": c_subject,
            "BODY": c_message_for_body,
            "LOGFILE TO ATTACH": None,
            "PROG RUNNING TIME": time_skolko_vremeni_rabotalo
          }
          y_n_error_in_log = "WARNING"
          email_send_status = self.f_send_email_or_post_to_webhook(event_for_email_webhook)

      if email_send_status == 'SUCCESS':
          logger.debug(f'STATUS E-MAIL WAS SENT SUCCESSFULLY.')
      else:  # email_send_status == 'ERROR':
          logger.debug(f'WARNING: STATUS E-MAIL WAS NOT SENT. CHECK E-MAIL CONFIG.')
          y_n_error_in_log = "WARNING"

      # THERE ARE NO ERRORS IN SAS-LOG-FILE -- y_n_error_in_log = "SUCCESS"
      # THERE ARE    ERRORS IN SAS-LOG-FILE -- y_n_error_in_log = "ERROR"
      # E-MAIL WAS NOT SENT                 -- y_n_error_in_log = "WARNING"
      return y_n_error_in_log
#   -----------------------------------------------------------------------------------------------------------


# #   -----------------------------------------------------------------------------------------------------------
#   def run_sas_program_main(self):

#       # -- ARGUMENTS WERE ALREADY CHECKED IN self.init 
#       # -- RUNNING LINUX USER WAS ALREDY CHECKED IN self.init 

#       # -- self.f_run_sas_program()
#       # -- Need to know if completed with ERROR 
#       # -- In case of error - Pernell need to re-run the .FLAG file without re-SFTP .PRD file
#       # -- So the .PRD file has to be available for Pernell to re-run without re-sendind .PRD file(s)
#       # -- 'ERROR'   - don't move/rename .PRD data file
#       # -- 'SUCCESS' - move/rename .PRD data file
#       # WILL CHECKED (INSIDE self.f_run_sas_program) IF SAS-LOG-FILE WAS CREATED
#       # IF IT WAS CREATED AND ERRORS WERE NOT FOUND -- y_n_error_in_log = SUCCESS
#       # IF IT WAS CREATED AND ERRORS WERE     FOUND -- y_n_error_in_log = ERROR
#       # IF IT WAS NOT CREATED -- y_n_error_in_log = WARNING
#       # ------------------------------------------------------------
#       y_n_error_in_log = self.f_run_sas_program()
#       # THERE ARE NO ERRORS IN SAS-LOG-FILE -- y_n_error_in_log = "SUCCESS"
#       # THERE ARE    ERRORS IN SAS-LOG-FILE -- y_n_error_in_log = "ERROR"
#       # E-MAIL WAS NOT SENT                 -- y_n_error_in_log = "WARNING"

#       # ------------------------------------------------------------


# #   -----------------------------------------------------------------------------------------------------------



if __name__ == "__main__":
  main()


