from client.models import *
from typing import cast, List, Any, TypeVar
from client.types import *
from client.api.settings import get_settings
from client.api.markets import get_markets
from client.api.fees import get_trading_fees
from client.api.balances import get_balances_address
from client.api.assets import get_assets_id
from client.api.orders import post_orders
from client.api.orders import delete_orders
from client.api.orders import post_orders_fill
from client.api.orders import get_order_books_market_id
from client.api.historical_prices import get_historical_prices_maestro_market_dex
import time

class ApiException(Exception):
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        super().__init__(f"API request failed with status {status_code}: {response}")

class FillRequest:
    def __init__(self, order_ref: str, amount: str) -> None:
        self.order_ref = order_ref
        self.amount = amount

class Api:

    def __init__(self, client, own_address : str, wait_for_confirmation : int, logger):
        self.client = client
        self.own_address = own_address
        self.wait_for_confirmation = wait_for_confirmation
        self.logger = logger

    def process_response(self, response : Response[ErrorResponse | Any]):
        if response.status_code < 300:
            return response.parsed
        else:
            raise ApiException(response.status_code, response)

    def get_settings(self):
        response: Response[ErrorResponse | Settings] = get_settings.sync_detailed(client=self.client)
        return cast(Settings, self.process_response(response))

    def get_markets(self):
        response: Response[ErrorResponse | List[Market]] = get_markets.sync_detailed(client=self.client)
        return cast(List[Market], self.process_response(response))

    def get_asset(self, asset_id : str):
        response: Response[ErrorResponse | Asset] = get_assets_id.sync_detailed(client=self.client, id=asset_id)
        return cast(Asset, self.process_response(response))

    def get_balances(self):
        response: Response[ErrorResponse | Any] = get_balances_address.sync_detailed(client=self.client, address=self.own_address)
        return cast(Any, self.process_response(response))

    def get_trading_fees(self):
        response: Response[ErrorResponse | Fees] = get_trading_fees.sync_detailed(client=self.client)
        return cast(Fees, self.process_response(response))

    def get_order_book(self, market_id : str):
        response: Response[ErrorResponse | OrderBookInfo] = get_order_books_market_id.sync_detailed(client=self.client, market_id=market_id)
        return cast(OrderBookInfo, self.process_response(response))

    def get_own_orders(self, market_id : str):
        response: Response[ErrorResponse | OrderBookInfo] = get_order_books_market_id.sync_detailed(client=self.client, market_id=market_id, address=self.own_address)
        return cast(OrderBookInfo, self.process_response(response))

    def get_price_history(self, market_id : str, resolution : str, from_date : str | Unset = UNSET, until_date: Unset | str = UNSET, sort="asc", limit=100, dex="minswap"):
        response: Response[ErrorResponse | List[MarketOHLC]] = get_historical_prices_maestro_market_dex.sync_detailed(client=self.client, market=market_id, dex=dex, resolution=resolution, from_=from_date, to=until_date, sort=sort, limit=limit)
        return cast(List[MarketOHLC], self.process_response(response))

    def get_market_price(self, market_id : str):
        response: Response[ErrorResponse | List[MarketOHLC]] = get_historical_prices_maestro_market_dex.sync_detailed(client=self.client, market=market_id, dex="minswap", resolution="1m", sort="desc", limit=1)
        return cast(List[MarketOHLC], self.process_response(response))

    def place_order(self, offered_amount : str, offered_token : str, price_token : str, price_amount : str):
        self.logger.info(f"[PLACE-ORDER] Placing order...")
        self.logger.info(f"[PLACE-ORDER] offered_amount: {offered_amount}")
        self.logger.info(f"[PLACE-ORDER] offered_token: {offered_token}")
        self.logger.info(f"[PLACE-ORDER] price_token: {price_token}")
        self.logger.info(f"[PLACE-ORDER] price_amount: {price_amount}")
        body = PostOrderParameters()
        body.offer_amount = offered_amount
        body.offer_token = offered_token
        body.price_token = price_token
        body.price_amount = price_amount
        response : Response[ErrorResponse | PostOrderResponse] = post_orders.sync_detailed(client=self.client, body=body)

        if isinstance(response.parsed, PostOrderResponse):
            self.logger.info(f"[PLACE-ORDER] Placed order: {response.parsed.transaction_id}")
            self.logger.info(f"[PLACE-ORDER] Waiting {self.wait_for_confirmation} seconds for confirmation...")
            time.sleep(self.wait_for_confirmation)
            self.logger.info(f"[PLACE-ORDER] [OK] Done!")

        if isinstance(response.parsed, ErrorResponse):
            self.logger.info(f"[PLACE-ORDER] [FAILED] ⚠️ [{response.parsed.error_code}] {response.parsed.message}")

        return cast(PostOrderResponse, self.process_response(response))

    def cancel_order(self, order_reference : str):
          self.logger.info(f"[CANCEL-ORDER] Canceling order...")
          self.logger.info(f"[CANCEL-ORDER] order_reference: {order_reference}")
          body = DeleteOrderParameters()
          body.address=self.own_address
          body.order_references=[order_reference]
          response: Response[ErrorResponse | DeleteOrderResponse] = delete_orders.sync_detailed(client=self.client, body=body)

          if isinstance(response.parsed, DeleteOrderResponse):
            self.logger.info(f"[CANCEL-ORDER] [OK] Canceled: {response.parsed.transaction_id}")
            self.logger.info(f"[CANCEL-ORDER] Waiting {self.wait_for_confirmation} seconds for confirmation...")
            time.sleep(self.wait_for_confirmation)
            self.logger.info(f"[CANCEL-ORDER] [OK] Done!")

          if isinstance(response.parsed, ErrorResponse):
            self.logger.info(f"[CANCEL-ORDER] [FAILED] ⚠️ [{response.parsed.error_code}] {response.parsed.message}")

          return cast(DeleteOrderResponse, self.process_response(response))

    def direct_fill(self, *fills: FillRequest):

        self.logger.info(f"[DIRECT-FILL] Direct filling from on-chain orders...")

        # Verify that the we do not try to fill from too many on-chain orders:
        if len(fills) > 5:
            self.logger.error("[DIRECT-FILL] Cannot fill from more than 5 on-chain orders.")
            raise ValueError("[DIRECT-FILL] Cannot fill from more than 5 on-chain orders.")

        # Verify FillRequest instances:
        for index, fill in enumerate(fills):
            if isinstance(fill, FillRequest):
                self.logger.info(f"[DIRECT-FILL] #{index+1} ref:    {fill.order_ref} ")
                self.logger.info(f"[DIRECT-FILL] #{index+1} amount: {fill.amount} ")
            else:
                self.logger.error("[DIRECT-FILL] Each fill must be an instance of Fill.")
                raise TypeError("[DIRECT-FILL] Each fill must be an instance of Fill.")

        # Build the request body:
        body = PostOrderFillParameters()
        body.order_references_with_amount = []
        for fill in fills:
            body.order_references_with_amount.append([fill.order_ref, fill.amount])

        # Send the request:
        response : Response[ErrorResponse | PostOrderFillResponse] = post_orders_fill.sync_detailed(client=self.client, body=body)

        if isinstance(response.parsed, PostOrderFillResponse):
            self.logger.info(f"[DIRECT-FILL] [OK] SUCCESS. transaction_id: {response.parsed.transaction_id}")
            self.logger.info(f"[DIRECT-FILL] Waiting {self.wait_for_confirmation} seconds for confirmation...")
            time.sleep(self.wait_for_confirmation)

        if isinstance(response.parsed, ErrorResponse):
            self.logger.info(f"[DIRECT-FILL] [FAILED] ⚠️ [{response.parsed.error_code}] {response.parsed.message}")

        return cast(PostOrderFillResponse, self.process_response(response))
