from flask import Flask

from utils.util import get_config_settings, create_db_engine, logging_lv_from_str, create_openai_connection
from typing import Dict
from waitress import serve
import logging
import os
import traceback
from datetime import datetime
from pytz import timezone

from app.model import SkeletonApp
from app.api import routes


_RUNTIME_ENV = None
_SERVICE_NAME = "ssa_listing_validator"

_TIMEZONE = timezone("UTC")
_RUN_DATE = datetime.now(_TIMEZONE).strftime("%Y-%m-%d")

# initialize our Flask application
_logger = logging.getLogger(_SERVICE_NAME.lower() + "_service_layer")
_LOG_LV = None
_service = Flask(_SERVICE_NAME)
_app = None
_db = None
_openai = None
OPENAI_SECRET = None


def init_service() -> None:
    try:
        determine_runtime_env()
        _logger.info(f"Currently running within the {_RUNTIME_ENV} runtime environment @ {_RUN_DATE}.")

        config_settings_dict = get_config_settings(_RUNTIME_APP_PATH, _RUNTIME_ENV)

        config_logger(config_settings_dict)
        config_db(config_settings_dict)
        config_openai(config_settings_dict)

    except Exception as e:
        raise e

def determine_runtime_env() -> None:
    default_runtime_env = "local"

    global _RUNTIME_ENV
    global _RUNTIME_APP_PATH

    _RUNTIME_ENV = os.getenv("RUNTIME_ENV", "local")
    _RUNTIME_APP_PATH = os.getenv("RUNTIME_APP_PATH", os.getcwd())

def config_logger(config_settings_dict: Dict) -> None:
    # get logging level from config
    global _LOG_LV
    _LOG_LV = config_settings_dict["logging_level"]
    _logger.debug(f"Configuring root log at the {_LOG_LV} level.")

    # set root logging level
    logging_lv = logging_lv_from_str(_LOG_LV)
    logging.basicConfig(level=logging_lv)
    _logger.info(f"Configured root log at the ({_LOG_LV}:{logging_lv}) level.")
    

def config_db(config_settings_dict: Dict) -> None:
    try:
        _logger.info(f"Establishing a connect to DynamoDB.")

        # create engine
        global _db
        _db = create_db_engine(config_settings_dict)
        _logger.info(f"Connection to DynamoDB established.")
    except Exception as e:
        raise e

def config_openai(config_settings_dict: Dict) -> None:
    try:
        # get secret
        global OPENAI_SECRET
        OPENAI_SECRET = config_settings_dict["openai_secret"]
        _logger.debug(f"Establishing a connect to OpenAI.")

        # create OpenAI connection
        global _openai
        _openai = create_openai_connection(OPENAI_SECRET)
        _logger.info(f"Connection to OpenAI established.")

        

    except Exception as e:
        raise e

def create_config_parameters() -> Dict:
    return {
        'runtime_env': f"{_RUNTIME_ENV}",
        'logging_level': f"{_LOG_LV}",
        'open_ai_key': f"{OPENAI_SECRET}"
    }

#  main thread of execution to start the server
if __name__ == "__main__":
    try:
        init_service()

        # create a dict of config parameters determined during init
        config_parameters = create_config_parameters()
        
        # create an instance of the application
        _app = SkeletonApp(_db, _openai, config_parameters)

        # create a blueprint based on the app's defined routes
        app_blueprint = routes.generateAppBlueprint(_app)

        # register the routes created by the app's blueprint
        _service.register_blueprint(app_blueprint)
        
        # start the service
        serve(_service, host="0.0.0.0", port=8080)

    except Exception as e:
        error = traceback.format_exc()
        message = (
        "\n##########################################################"
        f"\n{_SERVICE_NAME} ENCOUNTERED UNEXPECTED ERROR"
        "\n##########################################################"
        f"\n{error}"
        )
        _logger.error(message)
