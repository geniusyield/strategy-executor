from client.models import settings
from client.models import fees
from client.models import market
from client.models import market_ohlc
from client.models import post_order_parameters
from client.models import post_order_response
from client.models import post_order_response
from client.models import delete_order_parameters
from client.models import order_book_info
from client.models import order_info
from client.api.settings import get_settings
from client.api.markets import get_markets
from client.api.fees import get_trading_fees
from client.api.balances import get_balances_address
from client.api.assets import get_assets_id
from client.api.orders import post_orders
from client.api.orders import delete_orders
from client.api.orders import get_order_books_market_id
from client.api.historical_prices import get_historical_prices_maestro_market_dex
import time

class ApiException(Exception):
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        super().__init__(f"API request failed with status {status_code}: {response}")

class Api:

    own_address = None

    def __init__(self, client, own_address, wait_for_confirmation):
        self.client = client
        self.own_address = own_address
        self.wait_for_confirmation = wait_for_confirmation

    def process_response(self, response):
        if response.status_code < 300:
            return response.parsed
        else:
            raise ApiException(response.status_code, response)

    def get_settings(self):
        response: Response[settings] = get_settings.sync_detailed(client=self.client)
        return self.process_response(response)

    def get_markets(self):
        response: Response[markets] = get_markets.sync_detailed(client=self.client)
        return self.process_response(response)

    def get_asset(self, asset_id):
        response: Response[asset] = get_assets_id.sync_detailed(client=self.client, id=asset_id)
        return self.process_response(response)

    def get_balances(self):
        response: Response[balances] = get_balances_address.sync_detailed(client=self.client, address=self.own_address)
        return self.process_response(response)

    def get_trading_fees(self):
        response: Response[fees] = get_trading_fees.sync_detailed(client=self.client)
        return self.process_response(response)

    def get_order_book(self, market_id):
        response: Response[order_book_info] = get_order_books_market_id.sync_detailed(client=self.client, market_id=market_id)
        return self.process_response(response)

    def get_own_orders(self, market_id):
        response: Response[order_book_info] = get_order_books_market_id.sync_detailed(client=self.client, market_id=market_id, address=self.own_address)
        return self.process_response(response)

    def get_price_history(self, market_id, resolution, from_date, until_date, sort="asc", limit=1000):
        response: Response[order_book_info] = get_historical_prices_maestro_market_dex.sync_detailed(client=self.client, market=market_id, dex="genius-yield", resolution=resolution, from_=from_date, to=until_date)
        return self.process_response(response)

    def get_market_price(self, market_id):
        response: Response[order_book_info] = get_historical_prices_maestro_market_dex.sync_detailed(client=self.client, market=market_id, dex="genius-yield", resolution="1m", sort="desc", limit=1)
        return self.process_response(response)

    def place_order(self, offered_amount, offered_token, price_token, price_amount):
        body: post_order_parameters = post_order_parameters.PostOrderParameters()
        body.offer_amount=offered_amount
        body.offer_token=offered_token
        body.price_token=price_token
        body.price_amount=price_amount
        response: Response[post_order_response] = post_orders.sync_detailed(client=self.client, body=body)
        time.sleep(self.wait_for_confirmation)
        return self.process_response(response)

    def cancel_order(self, order_reference):
          body: delete_order_parameters = delete_order_parameters.DeleteOrderParameters()
          body.address=self.own_address
          body.order_references=[order_reference]
          response: Response[delete_order_response] = delete_orders.sync_detailed(client=self.client, body=body)
          time.sleep(self.wait_for_confirmation)
          return self.process_response(response)
