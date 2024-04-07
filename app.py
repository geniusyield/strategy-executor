from flask import Flask, jsonify
from client import AuthenticatedClient
from client.models import settings
from client.models import market
from client.models import post_order_parameters
from client.models import post_order_response
from client.models import delete_order_parameters
from client.models import delete_order_response
from client.api.settings import get_settings
from client.api.markets import get_markets
from client.api.balances import get_balances_address
from client.api.assets import get_assets_id
from client.api.orders import post_orders
from client.api.orders import delete_orders
import threading
import time
import os
import sys
import importlib
import yaml
import time
from datetime import datetime
import logging

app = Flask(__name__)
logger = logging.getLogger('gunicorn.error')

class Api:

    own_address = None

    def __init__(self, client, own_address):
        self.client = client
        self.own_address = own_address

    def get_settings(self):
        response: Response[settings] = get_settings.sync_detailed(client=self.client)
        return response

    def get_markets(self):
        response: Response[markets] = get_markets.sync_detailed(client=self.client)
        return response

    def get_asset(self, asset_id):
        response: Response[asset] = get_assets_id.sync_detailed(client=self.client, id=asset_id)
        return response

    def get_balances(self):
        response: Response[balances] = get_balances_address.sync_detailed(client=self.client, address=self.own_address)
        return response
    
    def place_order(self, offered_amount, offered_token, price_token, price_amount):
        body: post_order_parameters = post_order_parameters.PostOrderParameters()
        body.offer_amount=offered_amount
        body.offer_token=offered_token
        body.price_token=price_token
        body.price_amount=price_amount
        response: Response[post_order_response] = post_orders.sync_detailed(client=self.client, body=body)
        return response

    def cancel_order(self, order_reference):
          body: delete_order_parameters = delete_order_parameters.DeleteOrderParameters()
          body.address="addr_test1qz9zh342r6ynfhk974tmjxxxznrmmh0tre09tdh6gc3r6r2rq3uxt0yu4c0mg2ck6h8f0h3ykh7n4w68f7dr3mfch58q6rhtxg"
          body.order_references=[order_reference]
          response: Response[delete_order_response] = delete_orders.sync_detailed(client=self.client, body=body)
          return response

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
    if hasattr(module, 'configure'):
        module.configure(my_config)
    strategy_class_ref  = getattr(module, strategy_class)
    return strategy_class_ref

def worker():
    client = AuthenticatedClient(base_url="http://server:8082/v0/", token=SERVER_API_KEY, auth_header_name="api-key", prefix="")
    with client as client:
        attempt_successful = False
        own_address = None
        logger.info(f" Connecting to backend at: {BACKEND_URL}...")
        while not attempt_successful:
            try:
                response: Response[settings] = get_settings.sync_detailed(client=client)
                logger.info(f" [OK] Backend is available at: {BACKEND_URL} ✅ ")
                logger.info(f" > Version: {response.parsed.version}")
                logger.info(f" > Backend: {response.parsed.backend}")
                logger.info(f" > Revision: {response.parsed.revision}")
                logger.info(f" > Address: {response.parsed.address}")
                own_address = response.parsed.address
                attempt_successful = True
            except Exception as e:
                # If an exception occurs, print the message and wait for 5 seconds
                logger.info(f" > Backend not available. Retry in {RETRY_DELAY} seconds...")
                logger.debug(e)
                time.sleep(RETRY_DELAY)
                # The loop will then automatically retry

        api_client = Api(client, own_address);
        logger.info("==============================================")
        logger.info("[OK] Initialization is done ✅ ")
    
        logger.info(f"Loading strategy {STRATEGY}")
        strategy_class_ref = load_strategy(STRATEGY)
        strategy = strategy_class_ref(api_client, CONFIG, logger)
        logger.info(f" [OK] Strategy is loaded.")
    
        while True:
          logger.info("==============================================")
          logger.info(f" > Invoking strategy ({STRATEGY})... ⚙️⏳ ")
          start_time = time.time()
          logger.info(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
          try:
              strategy.execute(api_client, CONFIG, logger)
          except Exception:
              logger.error(f" ❌ Strategy exeuction has failed with an exception. ❌ ")
              logger.exception(" ❌ Exception occurred:")
          else:
              logger.info(f"[OK] Strategy exeuction has been finished ✅ ")
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
