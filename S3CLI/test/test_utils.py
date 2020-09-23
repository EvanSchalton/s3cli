from S3CLI.utils import loadConfig
import os

configPath = os.environ['S3CLI_AWS_USER_CONFIG']

def test_can_load_config():
    config = loadConfig(configPath)

    for key in [
        'region_name',
        'aws_access_key_id',
        'aws_secret_access_key'
    ]:
        assert key in config