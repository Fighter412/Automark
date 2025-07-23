import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_file(bucket, local_name, s3_name):# Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(local_name, bucket, s3_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def download_file(bucket, s3_name, local_name):
    # Download the file
    s3 = boto3.client('s3')
    s3.download_file(bucket, s3_name, local_name)


