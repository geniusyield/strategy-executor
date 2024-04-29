from client import AuthenticatedClient
from client.models import ErrorResponse, Settings
from client.api.settings import get_settings
from client.types import Response
from typing import cast, Union
from flask import Flask, jsonify
import threading
import time
import os
import sys
import importlib
import yaml
import time
from api import Api
from api import ApiException
from datetime import datetime
import logging
from flask_wtf.csrf import CSRFProtect

# Spin up Flask Application
app = Flask(__name__)

# Setup CSRF Protection.
csrf = CSRFProtect(app)
csrf.init_app(app)

logger = logging.getLogger('gunicorn.error')

def check_env_variable(var_name):
    if var_name not in os.environ:
        logger.critical(f"Error: Environment variable {var_name} is not set.")
        raise RuntimeError(f"Error: Environment variable {var_name} is not set.")
    return os.environ[var_name]

SERVER_API_KEY = check_env_variable('SERVER_API_KEY')
BACKEND_URL = check_env_variable('BACKEND_URL')
STRATEGY = check_env_variable('STRATEGY')
EXECUTION_DELAY = int(check_env_variable('EXECUTION_DELAY'))
STARTUP_DELAY = int(check_env_variable('STARTUP_DELAY'))
RETRY_DELAY = int(check_env_variable('RETRY_DELAY'))
CONFIRMATION_DELAY = int(check_env_variable('CONFIRMATION_DELAY'))
CONFIG = yaml.safe_load(check_env_variable('CONFIG'))

@app.route('/')
@app.route('/health')
def health_check():
    # Return service health information
    return jsonify(status='healthy', message='Service is up and running!')

def load_strategy(strategy_class):
    module = importlib.import_module(f".{strategy_class}", ".strategies")
    if hasattr(module, 'init'):
        module.init()
    strategy_class_ref  = getattr(module, strategy_class)
    return strategy_class_ref

def worker():
    client = AuthenticatedClient(base_url=f"{BACKEND_URL}/v0/", token=SERVER_API_KEY, auth_header_name="api-key", prefix="")
    with client as client:
        attempt_successful = False
        own_address : str = ""

        logger.info(f" Connecting to backend at: {BACKEND_URL}...")
        logger.info(f" > Wait {STARTUP_DELAY} seconds for backend start...")
        time.sleep(STARTUP_DELAY)
        while not attempt_successful:
            try:
                logger.info(f" > Connecting to backend...")
                response: Response[ErrorResponse | Settings] = get_settings.sync_detailed(client=client)
                settings_response: Response[Settings] = cast(Response[Settings], response)
                if (settings := settings_response.parsed) is not None:
                    logger.info(f" [OK] Backend is available at: {BACKEND_URL} ✅ ")
                    logger.info(f" BACKEND CONFIGURATION: ")
                    logger.info(f" > Version: {settings.version}")
                    logger.info(f" > Backend: {settings.backend}")
                    logger.info(f" > Revision: {settings.revision}")
                    logger.info(f" > Addr.: {settings.address}")
                    own_address = str(settings.address)
                    attempt_successful = True
                else:
                    logger.info(f" > Could not parse response. Retry again...")
            except Exception as e:
                # If an exception occurs, print the message and wait for the backend to start:
                logger.info(f" > Exception: {str(e)}")
                logger.info(f" > Backend is not available. Retry in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
                # The loop will then automatically retry

        logger.info(f" > [OK] Succesfully connected to backend.")
        api_client = Api(client, own_address, CONFIRMATION_DELAY, logger)
        logger.info("==============================================")
        logger.info("[OK] Initialization is done ✅ ")

        logger.info(f"Loading strategy {STRATEGY}")
        strategy_class_ref = load_strategy(STRATEGY)
        strategy = strategy_class_ref(api_client, CONFIG, logger)
        logger.info(f" [OK] Strategy is loaded.")

        while True:
          logger.info("==============================================")
          logger.info(f" > Invoking strategy: {STRATEGY}... ⚙️⏳ ")
          start_time = time.time()
          logger.info(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
          try:
              strategy.execute(api_client, CONFIG, logger)
          except Exception:
              logger.error(f" ❌ Strategy execution has failed with an exception. ❌ ")
              logger.exception(" ❌ Exception occurred:")
          else:
              logger.info(f"[OK] Strategy execution has been finished ✅ ")
          finally:
              end_time = time.time()
              execution_time = end_time - start_time
              logger.info(f"End time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
              logger.info(f"Execution time: {execution_time:.4f} seconds")

          logger.info(f"Wait {EXECUTION_DELAY}s until next execution...")
          time.sleep(EXECUTION_DELAY)

if __name__ == 'app':
    logger.info("==============================================")
    logger.info(" 🚀 Started trading strategy executor.")
    logger.info("==============================================")
    worker_thread = threading.Thread(target=worker)
    worker_thread.start()
