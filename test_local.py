from dotenv import load_dotenv
import boto3
import os
import io
from tempfile import NamedTemporaryFile
import pandas as pd
load_dotenv()

environment = os.getenv('ENVIRONMENT')

################################################
#aws
################################################
bucket_files_common = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_files_CUSTOM = os.getenv('S3_BUCKET_USERS_FILES')

s3_region = os.getenv('S3_UPLOADS_REGION')
s3_access_key = os.getenv('S3_UPLOADS_ACCESS_KEY')
s3_secret_key = os.getenv('S3_UPLOADS_SECRET_KEY')


s3 = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

print("cocou")