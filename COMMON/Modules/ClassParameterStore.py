
import logging
import boto3
import json

logger = logging.getLogger(__name__)
logger.critical('-----------------------------------------------------------------------------------')
logger.warning(f"Log Level in '{__name__}': {logger.level}")
logger.critical('-----------------------------------------------------------------------------------')


class ClassParameterStore():

    def __init__(self,
                f_aws_access_key_id,
                f_aws_secret_access_key,
                f_parameter_store_path):


        logger.warning('-')
        logger.warning(f'- f_parameter_store_path = {f_parameter_store_path}')
        logger.warning('-')

        # self.ssm = boto3.client("ssm")

        self.session = boto3.Session(
            aws_access_key_id=f_aws_access_key_id,
            aws_secret_access_key=f_aws_secret_access_key,
        )
        self.ssm = self.session.client("ssm")

        self.parameter_store_path = f_parameter_store_path



    def get_parameter_as_dic(self):

        parameter1 = self.ssm.get_parameter(Name=self.parameter_store_path,
                                           WithDecryption=True)
        
        dic_parameter_real = json.loads(parameter1["Parameter"]["Value"])

        return dic_parameter_real





