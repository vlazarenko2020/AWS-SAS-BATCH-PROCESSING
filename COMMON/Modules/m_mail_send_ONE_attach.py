#!/usr/bin/env python
#
# Sends an HTML e-mail with at most one file attachment. Two delivery methods:
#   - mail_send_ONE_attach:     SMTP relay at the caller-supplied f_smtpserver
#                                (internal relay, no auth). ClassSASProgram
#                                passes z_config.f_get_prog_config(...)['mail']['SMTP']
#                                for this.
#   - mail_send_ONE_attach_SES: AWS SES via boto3, for use when no SMTP relay
#                                is reachable (e.g. local/dev). Uses the same
#                                AWS key as S3_Bucket_processing (the
#                                AWS_KEY_1/AWS_KEY_VALUES_1 env vars sourced
#                                from AWS_KEY/.env-<NAME>) unless explicit
#                                credentials are passed in.
#
# The real module ClassSASProgram.py was originally written against lives at
# '/usr/local/vbin/common_py' on the real SAS server, outside this git tree.
# This local copy lives in Modules/ instead, and ClassSASProgram.py's import
# was changed to `from Modules.m_mail_send_ONE_attach import ...` to match -
# that changed import line must be reverted to the original unqualified
# `from m_mail_send_ONE_attach import ...` before deploying to the real SAS
# server, or it will fail to import there.

import os
import smtplib
import boto3
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ClassMailSend():

    @staticmethod
    def _build_message(f_from_addr,
                        f_to_addr_list,
                        f_cc_addr_list,
                        f_subject,
                        f_telo,
                        f_file_to_attach_with_path):

        msg = MIMEMultipart()
        msg['From']    = f_from_addr
        msg['To']      = ', '.join(f_to_addr_list)
        msg['Cc']      = ', '.join(f_cc_addr_list)
        msg['Subject'] = f_subject

        msg.attach(MIMEText(f_telo, 'html'))

        if f_file_to_attach_with_path:
            with open(f_file_to_attach_with_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename="{os.path.basename(f_file_to_attach_with_path)}"')
            msg.attach(part)

        return msg


    @staticmethod
    def mail_send_ONE_attach(f_from_addr,
                              f_to_addr_list,
                              f_cc_addr_list,
                              f_subject,
                              f_telo,
                              f_file_to_attach_with_path,
                              f_smtpserver):

        msg = ClassMailSend._build_message(f_from_addr,
                                            f_to_addr_list,
                                            f_cc_addr_list,
                                            f_subject,
                                            f_telo,
                                            f_file_to_attach_with_path)

        all_recipients = f_to_addr_list + f_cc_addr_list

        with smtplib.SMTP(f_smtpserver) as server:
            server.sendmail(f_from_addr, all_recipients, msg.as_string())


    @staticmethod
    def mail_send_ONE_attach_SES(f_from_addr,
                                  f_to_addr_list,
                                  f_cc_addr_list,
                                  f_subject,
                                  f_telo,
                                  f_file_to_attach_with_path,
                                  f_aws_region=None,
                                  f_aws_access_key_id=None,
                                  f_aws_secret_access_key=None):

        # Same AWS key as S3_Bucket_processing uses (see
        # S3_Bucket_processing/info/s3_folder_mask_aws-key.info,
        # line 1 -> $AWS_KEY_1/$AWS_KEY_VALUES_1), unless the caller passed
        # explicit credentials. Fail closed if neither is available.
        if f_aws_access_key_id is None:
            f_aws_access_key_id = os.environ.get('AWS_KEY_1')
        if f_aws_secret_access_key is None:
            f_aws_secret_access_key = os.environ.get('AWS_KEY_VALUES_1')
        if not f_aws_access_key_id or not f_aws_secret_access_key:
            raise RuntimeError("mail_send_ONE_attach_SES: no AWS credentials available "
                                "(pass f_aws_access_key_id/f_aws_secret_access_key, or "
                                "export AWS_KEY_1/AWS_KEY_VALUES_1).")

        f_aws_region = f_aws_region or os.environ.get('AWS_REGION', 'us-east-2')

        msg = ClassMailSend._build_message(f_from_addr,
                                            f_to_addr_list,
                                            f_cc_addr_list,
                                            f_subject,
                                            f_telo,
                                            f_file_to_attach_with_path)

        all_recipients = f_to_addr_list + f_cc_addr_list

        ses_client = boto3.client('ses',
                                region_name=f_aws_region,
                                aws_access_key_id=f_aws_access_key_id,
                                aws_secret_access_key=f_aws_secret_access_key)

        ses_client.send_raw_email(Source=f_from_addr,
                                Destinations=all_recipients,
                                RawMessage={'Data': msg.as_string()})
