from flask import Flask, jsonify
from client import AuthenticatedClient
from client.models import settings
from client.models import post_order_parameters
from client.models import delete_order_parameters
from client.api.settings import get_settings
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
    # TEST ############################################
    client = AuthenticatedClient(base_url="http://server:8082/v0/", token=SERVER_API_KEY, auth_header_name="api-key", prefix="")
    with client as client:
        response: Response[settings] = get_settings.sync_detailed(client=client)
        logger.info(f"RESPONSE STATUS CODE: {response.status_code}")
        logger.info(f"RESPONSE: {response.parsed}")
        logger.info(response)
        # Place order:
        body: post_order_parameters = post_order_parameters.PostOrderParameters()
        body.offer_amount="1"
        body.offer_token="lovelace"
        body.price_token="66a524d7f34d954a3ad30b4e2d08023c950dfcd53bbe3c2314995da6.744d454c44"
        body.price_amount="1"
        body.address="addr_test1qz9zh342r6ynfhk974tmjxxxznrmmh0tre09tdh6gc3r6r2rq3uxt0yu4c0mg2ck6h8f0h3ykh7n4w68f7dr3mfch58q6rhtxg"
        response: Response[settings] = post_orders.sync_detailed(client=client, body=body)
        logger.info(f"POST RESPONSE STATUS CODE: {response.status_code}")
        logger.info(f"POST PARSED RESPONSE: {response.parsed}")
        logger.info(response)
        # Cancel order:
        body: delete_order_parameters = delete_order_parameters.DeleteOrderParameters()
        body.address="addr_test1qz9zh342r6ynfhk974tmjxxxznrmmh0tre09tdh6gc3r6r2rq3uxt0yu4c0mg2ck6h8f0h3ykh7n4w68f7dr3mfch58q6rhtxg"
        body.order_references=["47276d0ca1d40d818f893d656c503f335f4412439832e525a3c02b161a48627d#0"]
        response: Response[settings] = delete_orders.sync_detailed(client=client, body=body)
        logger.info(f"DELETE RESPONSE STATUS CODE: {response.status_code}")
        logger.info(f"DELETE PARSED RESPONSE: {response.parsed}")
        logger.info(response)
        
        
    time.sleep(1000)
    logger.info(f">>STOPPED <<")
    # TEST############################################

    logger.info("Worker thread is starting...")
    logger.info(f"Wait {STARTUP_DELAY}s until backend is ready...")
    time.sleep(STARTUP_DELAY)
    logger.info(" [OK] Waiting is over.")
    logger.info("Starting strategy....")

    # Create API client:
    configuration = swagger_client.Configuration()
    configuration.api_key['api-key'] = SERVER_API_KEY
    configuration.host = BACKEND_URL

    api_client= swagger_client.ApiClient(configuration)

    assets_api = swagger_client.AssetsApi(api_client)
    balances_api = swagger_client.BalancesApi(api_client)
    historical_prices_api = swagger_client.HistoricalPricesApi(api_client)
    markets_api = swagger_client.MarketsApi(api_client)
    order_book_api = swagger_client.OrderBookApi(api_client)
    orders_api = swagger_client.OrdersApi(api_client)
    settings_api = swagger_client.SettingsApi(api_client)
    trading_fees_api = swagger_client.TradingFeesApi(api_client)
    transaction_api = swagger_client.TransactionApi(api_client)

    client = {}
    client["assets"] = assets_api
    client["balances"] = balances_api
    client["historical_prices"] = historical_prices_api
    client["markets"] = markets_api
    client["order_book"] = order_book_api
    client["orders"] = orders_api
    client["settings"] = settings_api
    client["trading_fees"] = trading_fees_api
    client["transaction"] = transaction_api

    attempt_successful = False

    while not attempt_successful:
        try:
            resp = client["settings"].v0_settings_get()
            attempt_successful = True  # If success, update the flag to exit the loop
        except Exception as e:
            # If an exception occurs, print the message and wait for 5 seconds
            logger.info(f"Backend not available. Wait {RETRY_DELAY} seconds")
            logger.debug(e)
            time.sleep(RETRY_DELAY)
            # The loop will then automatically retry

    logger.info(f" > Using version {resp.version} of {resp.backend}.")
    logger.info("==============================================")
    logger.info("[OK] Initialization is done ✅ ")

    logger.info(f"Loading strategy {STRATEGY}")
    strategy_class_ref = load_strategy(STRATEGY)
    strategy = strategy_class_ref(client, CONFIG, logger)
    logger.info(f" [OK] Strategy is loaded.")

    while True:
      logger.info("==============================================")
      logger.info(f" > Invoking strategy ({STRATEGY})... ⚙️⏳ ")
      start_time = time.time()
      logger.info(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
      try:
          strategy.execute(client, CONFIG, logger)
      except Exception as e:
          logger.error(f" ❌ Strategy exeuction has failed with an exception. ❌ ")
          logger.error(" ❌ Exception : %s\n" % e)
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
