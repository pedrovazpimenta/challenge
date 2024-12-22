import os
import boto3
import pandas as pd
from contextlib import contextmanager

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

@contextmanager
def get_aws_s3_client():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        yield s3
    except Exception as e:
        raise e
    finally:
        s3.close()
    
def load_data(bucket: str, key: str) -> pd.DataFrame:
    """
    Load a file from an S3 bucket

    Args:
        bucket (str): the bucket name
        key (str): the key name

    Returns:
        pd.DataFrame: the dataframe file
    """
    with get_aws_s3_client() as s3:
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = pd.read_csv(obj["Body"])
    return data

def upload_model_binary(bucket: str, key: str, model_binary: bytes):
    """
    Upload a model binary to an S3 bucket

    Args:
        bucket (str): the bucket name
        key (str): the key name
        model_binary (bytes): the model binary
    """
    with get_aws_s3_client() as s3:
        s3.put_object(Bucket=bucket, Key=key, Body=model_binary)
        
def download_model_binary(bucket: str, key: str) -> bytes:
    """
    Download a model binary from an S3 bucket

    Args:
        bucket (str): the bucket name
        key (str): the key name

    Returns:
        bytes: the model binary
    """
    with get_aws_s3_client() as s3:
        obj = s3.get_object(Bucket=bucket, Key=key)
        model_binary = obj["Body"].read()
    return model_binary