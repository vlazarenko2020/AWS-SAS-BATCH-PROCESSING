
import os
import re
import subprocess

l_all_ORDER_HIST_tables = [ r'^ORDER_ITEM_HIST', r'^CONTACT_MSTR_', r'^Z_BINARY_WEEKEND_COMPLETE' ]
#l_all_ORDER_HIST_tables = [ r'^ZZZ_', r'^XXX_' ]

kill_prog_with_path = '/usr/local/vbin/PROD/sas_ftp_processing_root/kill_all_regular_sas_users_sessions.sh'

def f_kill_users_if_ORDER_HIST( f_current_flag_file_with_path ):

  current_string = '---BEGINNING FUNCTION: f_kill_users_if_ORDER_HIST'
  print( '-' * 30 + '\n' + current_string + '\n' + '-' * 30 )
    
  print( '...' )
  print( '...current_flag_file_with_path: ' + f_current_flag_file_with_path )
  print( '...' )
          

  current_flag_file_without_path = os.path.basename(f_current_flag_file_with_path)
  current_flag_file_without_extension, current_flag_file_extension = os.path.splitext(current_flag_file_without_path)

  print( '...current_flag_file_without_extension: ' + current_flag_file_without_extension )
  print( '...current_flag_file_extension:     ' + current_flag_file_extension )
  print( '...' )
      

  for current_regex in l_all_ORDER_HIST_tables:
    match  = re.search( current_regex, current_flag_file_without_extension )
    if match:
    
         print( "Match:    %s =~ %s" % ( current_regex, current_flag_file_without_extension ))
#        print( "Match: {} =~ {}".format( current_regex, current_flag_file_without_extension )
#        komanda = ['/usr/local/vbin/PROD/sas_ftp_processing_root/kill_all_regular_sas_users_sessions.sh' ]
         komanda = [ kill_prog_with_path ]
         p1 = subprocess.Popen(komanda, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
         my_output, my_error = p1.communicate()
         print( '...output:' )
         print(  my_output )
         print( '...error:' )
         print( my_error )

    else:

#        print( "NO match: {} =~ {}".format( current_regex, current_flag_file_without_extension )
         print( "NO match: %s =~ %s" % ( current_regex, current_flag_file_without_extension ))

  print( '...' )

  current_string = '---END FUNCTION: f_kill_users_if_ORDER_HIST'
  print( '-' * 30 + '\n' + current_string + '\n' + '-' * 30 )
    