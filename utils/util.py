import json
from typing import Dict, Union
import logging
import os

from langchain_openai import OpenAI

import boto3
from boto3.resources.base import ServiceResource


logger = logging.getLogger("service_util")

def get_config_settings(runtime_app_path: str, runtime_env: str) -> Dict:
    """
    Get environment and secret values
    Args: None

    Returns: Dict
    """
    try:
        logger.info("get_config_settings")

        # get config settings
        config_dict = get_value_from_json(f"{runtime_app_path}/config.json", runtime_env)

        return config_dict

    except Exception as e:
        raise e


def get_value_from_json(json_file: str, key: str = None) -> str:
    try:
        with open(json_file) as f:
            data = json.load(f)
            if key is None:
                return data
            else:
                return data[key]
    except Exception as e:
        raise e

def create_db_engine(db_dict: Dict) -> ServiceResource:
    return create_dynamo_engine(db_dict)

def create_dynamo_engine(config_dict: Dict) -> ServiceResource:
    """
    Create AWS Dynamo db engine
    Args:
        db_dict: dictionary containing credential values

    Returns: Connection
    """
    logger.info("create_dynamo_engine")
    # get db info
    db_dict = config_dict["dynamo_info"]

    engine = boto3.resource('dynamodb', endpoint_url=db_dict['endpoint_url'], region_name=db_dict['region_name'])
    
    return engine

def create_openai_connection(openai_key: str) -> OpenAI:

    # create OpenAI connection
    openai = OpenAI(
        openai_api_key=openai_key,
        temperature=0,
        model_name="gpt-3.5-turbo-instruct",
    )

    return openai

def logging_lv_from_str(str_in: str) -> int:
    logging_lv = logging.NOTSET

    if str_in == 'DEBUG':
        logging_lv = logging.DEBUG
    elif str_in == 'INFO':
        logging_lv = logging.INFO
    elif str_in == 'WARNING':
        logging_lv = logging.WARNING
    elif str_in == 'ERROR':
        logging_lv = logging.ERROR
    else:
        logging_lv = logging.CRITICAL
    
    return logging_lv
