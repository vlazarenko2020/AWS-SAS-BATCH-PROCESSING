

host_name       = "metaapp"

m_possible_thread_numbers = [ '1', '2', '3', '4' ]
#m_dir_base                  = '/usr/local/vbin/PROD/sas_ftp_processing_root'
m_dir_base                  = '.'
m_suffiks_i_am_working      = '___i_am_working__.thread'
m_allowed_users             = ['MRSERVICEUSER', 'EMSERVICEUSER']

host_name       = "sas-server.example.com"

l_gzip_bin_with_parameters = ['/usr/bin/gzip', '-vf']
gzip_bin_with_parameters   = '/usr/bin/gzip -vf'
folder_destination_for_gziped_PRD = '/sas-software-depot/PRD_FILES_BACKUP'

# -- Mail SMTP server/FROM/TO used to live here as standalone globals
# -- (c_smtpserver, c_ses_verified_from_addr, c_ses_verified_to_addr_list,
# -- c_to_addr_list_to_add_to_recipient_list). They now live per-job inside
# -- each l_prog_config entry's 'mail' sub-dict below - see f_get_prog_config().

#sas_bin = '/sas/sasbin94/sashome/SASFoundation/9.4/sasexe/sas'
# sas_bin = '/sas/sasbin94/sashome/SASFoundation/9.4/sas'
# -- DEPLOYMENT.sh sets this line automatically each time it runs: it checks
# -- whether a real `sas` executable is available on this machine (PATH lookup
# -- + the two known install paths above) and points sas_bin at it if so,
# -- otherwise leaves/sets it to '../FAKE-SAS-BIN.sh'. A real SAS license is too
# -- expensive to have in a dev environment, so FAKE-SAS-BIN.sh (which emulates
# -- just enough of the real binary's -log/-print/-sysin behavior for
# -- ClassSASProgram to run end-to-end) is the permanent fallback here - don't
# -- hand-edit this line, re-run DEPLOYMENT.sh instead.
sas_bin = '../FAKE-SAS-BIN.sh'

# -----------------------------------------------------------------------------------------------
# -- Replaces the old 8 separate dic_path_to_* / dic_compress dictionaries. Each of those used to
# -- need one entry added per job/path, all keyed by the same path/system-name string. Here, one
# -- job/path = one entry in l_prog_config: a single-key dict {path_name: {all the settings for
# -- that path}}. Same information, one place per job, including its "mail" sub-dict
# -- (SMTP/from/to) so mail config lives alongside everything else instead of in
# -- separate globals. Look up a job's settings with f_get_prog_config(path_name)
# -- below - e.g. f_get_prog_config('S3_Bucket_processing').
# -----------------------------------------------------------------------------------------------
l_prog_config = [

    {
        '/sas01/sasdata/PROD/staging/data/IT_Marketing': {
            'path_to_user':       'MRSERVICEUSER',
            'path_to_mailfile':   './info/PROD/MRSERVICEUSER',
            'path_to_systemname': 'IT_Marketing',
            'path_to_logfile':    '/sas01/sasdata/PROD/staging/log/IT_Marketing',
            'path_to_sasfile':    '/sas01/sasdata/PROD/staging/source/IT_Marketing',
            'compress':           True,
            'path_to_ftp':        '',
            'path_to_aws_key':    '',
            'mail': {
                'SMTP': 'smtp.example.internal',
                'from': 'SAS-AWS-FLAG Processing<sas-status@notification.example.com>',
                'to':   ['user@example.com'],
            },
        }
    },

    {
        '/sas01/sasdata/DBM/staging/data': {
            'path_to_user':       'dont_do_su_to_EMSERVICEUSER',
            'path_to_mailfile':   './info/PROD/EMSERVICEUSER_DBM_STAGING_DATA',
            'path_to_systemname': 'DBM_staging_data',
            'path_to_logfile':    '/sas01/sasdata/DBM/staging/log',
            'path_to_sasfile':    '/sas01/sasdata/DBM/staging/source',
            'compress':           True,
            'path_to_ftp':        '',
            'path_to_aws_key':    '../AWS_KEY/EMSERVICEUSER',
            'mail': {
                'SMTP': 'smtp.example.internal',
                'from': 'SAS-AWS-FLAG Processing<sas-status@notification.example.com>',
                'to':   ['user@example.com'],
            },
        }
    },

    {
        '/sas01/sasdata/PROD/scoring/inputs': {
            'path_to_user':       'dont_do_su_to_EMSERVICEUSER',
            'path_to_mailfile':   './info/PROD/EMSERVICEUSER_SCORING_INPUTS',
            'path_to_systemname': 'DBM_scoring_inputs',
            'path_to_logfile':    '/sas01/sasdata/PROD/scoring/inputs_log',
            'path_to_sasfile':    '/sas01/sasdata/PROD/scoring/code_1',
            'compress':           False,
            'path_to_ftp':        '',
            'path_to_aws_key':    '../AWS_KEY/EMSERVICEUSER',
            'mail': {
                'SMTP': 'smtp.example.internal',
                'from': 'SAS-AWS-FLAG Processing<sas-status@notification.example.com>',
                'to':   ['user@example.com'],
            },
        }
    },

    {
        '/sas01/sasdata/PROD/scoring/code_2': {
            'path_to_user':       'dont_do_su_to_EMSERVICEUSER',
            'path_to_mailfile':   './info/PROD/EMSERVICEUSER_SCORING_CODE2',
            'path_to_systemname': 'DBM_scoring_code2',
            'path_to_logfile':    '/sas01/sasdata/PROD/scoring/code_2_log',
            'path_to_sasfile':    '/sas01/sasdata/PROD/scoring/code_2',
            'compress':           True,
            'path_to_ftp':        '/SAS/AWS/FTP/10.0.0.1-REMOTE',
            'path_to_aws_key':    '../AWS_KEY/EMSERVICEUSER',
            'mail': {
                'SMTP': 'smtp.example.internal',
                'from': 'SAS-AWS-FLAG Processing<sas-status@notification.example.com>',
                'to':   ['user@example.com'],
            },
        }
    },

    {
        'S3_Bucket_processing': {
            'path_to_user':       'dont_do_su_to_EMSERVICEUSER',
            'path_to_mailfile':   './info/PROD/S3_Bucket_processing',
            'path_to_systemname': 'S3_Bucket_processing',
            'path_to_logfile':    '../sas01_sasdata_PROD_S3_Bucket_processing/log',
            'path_to_sasfile':    '../sas01_sasdata_PROD_S3_Bucket_processing/source',
            'compress':           True,
            'path_to_ftp':        '',
            'path_to_aws_key':    './info/s3_folder_mask_aws-key.info',
            'mail': {
                'SMTP': 'SES',
                'from': 'SAS-AWS-FLAG S3 Processing<user@example.com>',
                'to':   ['user@example.com'],
            },
        }
    },

]


def f_get_prog_config(f_path_key):
    # -- Looks up f_path_key (e.g. 'S3_Bucket_processing', system_short_name in the .sh wrappers)
    # -- in l_prog_config and returns its settings dict, or None if no entry matches -
    # -- same "key not found" shape as a plain dict.get() on the old dic_path_to_* dictionaries.
    for d_entry in l_prog_config:
        if f_path_key in d_entry:
            return d_entry[f_path_key]
    return None


if __name__ == "__main__":
    # -- Quick self-check: confirm the lookup returns the expected
    # -- 'S3_Bucket_processing' settings.
    l_expected = [
        ('path_to_user',       'dont_do_su_to_EMSERVICEUSER'),
        ('path_to_mailfile',   './info/PROD/S3_Bucket_processing'),
        ('path_to_systemname', 'S3_Bucket_processing'),
        ('path_to_logfile',    '../sas01_sasdata_PROD_S3_Bucket_processing/log'),
        ('path_to_sasfile',    '../sas01_sasdata_PROD_S3_Bucket_processing/source'),
        ('compress',           True),
        ('path_to_ftp',        ''),
        ('path_to_aws_key',    './info/s3_folder_mask_aws-key.info'),
        ('mail', {
            'SMTP': 'SES',
            'from': 'SAS-AWS-FLAG S3 Processing<user@example.com>',
            'to':   ['user@example.com'],
        }),
    ]

    d_config = f_get_prog_config('S3_Bucket_processing')
    f_all_passed = True

    if d_config is None:
        print("FAIL: f_get_prog_config('S3_Bucket_processing') returned None")
        f_all_passed = False
    else:
        for f_field, f_expected_value in l_expected:
            f_actual_value = d_config.get(f_field)
            if f_actual_value == f_expected_value:
                print(f"PASS: {f_field} = {f_actual_value!r}")
            else:
                print(f"FAIL: {f_field} = {f_actual_value!r} (expected {f_expected_value!r})")
                f_all_passed = False

    print("FAIL: f_get_prog_config('does_not_exist') should return None" if
        f_get_prog_config('does_not_exist') is not None else
        "PASS: f_get_prog_config('does_not_exist') returned None")

    exit(0 if f_all_passed else 1)
