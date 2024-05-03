# aws utils
import boto3
from botocore.exceptions import ClientError
from typing import Dict, BinaryIO
import logging
from typing import Dict
import json
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mindset_aws_util")

REGION_NAME = "us-east-1"


def get_secret_dict(secret_name: str) -> Dict:
    logger.info("get_secret_dict")
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=REGION_NAME)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]
    secret_dict = json.loads(secret)
    return secret_dict
