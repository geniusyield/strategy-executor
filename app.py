from flask import Flask, jsonify
import swagger_client
from swagger_client.rest import ApiException
import threading
import time
import os
import importlib
import yaml
app = Flask(__name__)
SERVER_API_KEY = os.environ['SERVER_API_KEY']
BACKEND_URL = os.environ['BACKEND_URL']
STRATEGY = os.environ['STRATEGY']
EXECUTION_DELAY = int(os.environ['EXECUTION_DELAY'])
STARTUP_DELAY = int(os.environ['STARTUP_DELAY'])
CONFIG = yaml.safe_load(os.environ['CONFIG'])

@app.route('/')
@app.route('/health')
def health_check():
    # Return service health information
    return jsonify(status='healthy', message='Service is up and running!')

def load_strategy(strategy_class):
    module = importlib.import_module(f".{strategy_class}", ".strategies")
    strategy_implementation = getattr(module, strategy_class)
    return strategy_implementation

def worker():
    print(f"Wait {STARTUP_DELAY}s until backend is ready...")
    time.sleep(STARTUP_DELAY)
    print(" [OK] Waiting is over.")
    print("Starting strategy....")

    print("Worker thread is starting...")
    print(f"Loading strategy {STRATEGY}")
    strategy = load_strategy(STRATEGY)
    print(f" [OK] Strategy is loaded.")

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

    resp = client["settings"].v0_settings_get()
    print("======[ BACKEND ] =====")
    print(f"Using version {resp.version} of {resp.backend}.")
    print("=======================")
    print("[OK] Initialization is done")

    while True:
      try:
          print("=======================")
          print(f"Invoking strategy ({STRATEGY})...")
          strategy.execute(client, CONFIG)
          print(f"[OK] Strategy exeuction has been finished")
      except ApiException as e:
          print("ApiException: %s\n" % e)

      print(f"Wait {EXECUTION_DELAY}s until next execution...")
      time.sleep(EXECUTION_DELAY)

if __name__ == 'app':
    worker_thread = threading.Thread(target=worker)
    worker_thread.start()
