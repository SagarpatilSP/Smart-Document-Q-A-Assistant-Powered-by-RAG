import boto3 
from botocore.exceptions import ClientError

S3_BUCKET = "ml-book-rag-data"
s3 = boto3.client("s3")

def upload_to_s3(local_path, s3_key):
    s3.upload_file(local_path, S3_BUCKET, s3_key)

def download_from_s3(local_path, s3_key):
    s3.download_file(S3_BUCKET, s3_key, local_path)

def s3_exists(s3_key):
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
        return True
    except ClientError:
        return False