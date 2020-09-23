from ..s3connection import connect
from ..utils import loadConfig
import os
import boto3


def test_can_connect_to_s3():

    try:
        c = connect()
        assert isinstance(c, boto3.resources.factory.ServiceResource)
    except Exception as e:
        raise e