from boto3 import resource
from .utils import loadConfig
import os


def connect(configPath=""):

    if configPath == "":
        configPath = os.environ['S3CLI_AWS_USER_CONFIG']

    config = loadConfig(configPath)


    s3 = resource(
        region_name=config['region_name'],
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
        api_version='2006-03-01',
        service_name='s3'
    )

    return s3