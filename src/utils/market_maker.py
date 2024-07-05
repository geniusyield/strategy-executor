import math
from api import Api, ApiException

class MarketMaker:
    """Handle buy and sell orders."""

    def __init__(self, api_client, config, logger):
        self.api_client : Api = api_client
        self.logger = logger

        # Strategy Configuration:
        self.position_size = float(config["POSITION_SIZE_LOVELACES"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"

    def place_buy_order(self, price):
        self.logger.info(" ⚙️ Placing BUY order...")

        try:
            balance_available = int(self.api_client.get_balances().get(self.base_asset, 0))
            self.logger.debug(f" > balance_available : {balance_available}")
            self.logger.debug(f" > self.position_size: {self.position_size}")

            order_size = min(self.position_size, balance_available)
            if not order_size:
                self.logger.info(" ⚠️ Insufficient balance to place BUY order! ⚠️")
                return

            offered_amount = int(math.floor(order_size))

            self.logger.info(f" > Place BUY order: {offered_amount}  at price {price}...")
            response = self.api_client.place_order(
                     offered_amount=f"{offered_amount}",
                     offered_token=self.base_asset,
                     price_token=self.target_asset,
                     price_amount=f"{int(math.floor(offered_amount / price))}"
            )
            self.logger.info(f" > [OK] PLACED NEW BUY ORDER: {response.order_ref}")
        # pylint: disable=bare-except
        except:
            self.logger.error(" > ⚠️ [FAILED] Could not place BUY order. ⚠️")
            self.logger.exception(" > Exception! ")

    def place_sell_order(self, price):
        self.logger.info(" ⚙️ Placing SELL order...")

        try:
            balance_available = int(self.api_client.get_balances().get(self.target_asset, 0))
            self.logger.info(f" > balance_available : {balance_available}")
            order_size = min(self.position_size / price, balance_available)
            self.logger.info(f" > order_size : {order_size}")
            self.logger.info(f" > price : {price}")
            if not order_size:
                self.logger.info("⚠️ Insufficient balance to place SELL order! ⚠️")
                return

            self.logger.info(f" > Place SELL order: {order_size} at price {price}...")
            response = self.api_client.place_order(
              offered_amount=f"{int(math.floor(order_size))}",
              offered_token=self.target_asset,
              price_token=self.base_asset,
              price_amount=f"{int(math.floor(order_size * price))}"
            )
            self.logger.info(f" > [OK] PLACED NEW SELL ORDER: {response.order_ref}")
        # pylint: disable=bare-except
        except:
            self.logger.error(" > ⚠️ [FAILED] Could not place SELL order. ⚠️")
            self.logger.exception(" > Exception! ")

    def get_buy_orders(self):
        own_orders = self.api_client.get_own_orders(self.market)
        return own_orders.bids

    def get_sell_orders(self):
        own_orders = self.api_client.get_own_orders(self.market)
        return own_orders.asks

    def cancel_buy_orders(self):
        self.logger.info(" > Cancel all BUY orders...")
        self.cancel_orders("bid")
        self.logger.info(" > [OK] Canceled all BUY orders.")

    def cancel_sell_orders(self):
        self.logger.info(" > Cancel all SELL orders...")
        self.cancel_orders("ask")
        self.logger.info(" > [OK] Canceled all SELL orders.")

    def cancel_orders(self, side):
        while True:
            orders = []
            own_orders = self.api_client.get_own_orders(self.market)
            if side == "ask":
                orders = own_orders.asks
            else:
                orders = own_orders.bids

            if len(orders) == 0:
                return
            else:
                self.logger.info(f" Remaining {side} orders: {len(orders)}.")

            order = orders[0]
            try:
                self.logger.info(f" ⚙️ Canceling order: {order.output_reference}")
                self.api_client.cancel_order(order.output_reference)
                self.logger.info(f" > [OK] Canceled order: {order.output_reference}")
            except ApiException:
                # pylint: disable=line-too-long
                self.logger.error(" > ⚠️ [FAILED] could not cancel order: {order.output_reference} ⚠️")
                self.logger.exception(" > Exception! ")

    def log_orders(self):
        own_orders = self.api_client.get_own_orders(self.market)

        self.logger.info(" ON-CHAIN ORDERS:")

        if (len(own_orders.asks) + len(own_orders.bids)) == 0:
            self.logger.info(" > No orders.")
            return

        for sell_order in own_orders.asks:
            self.logger.info(f" > SELL: {sell_order.output_reference}")

        for buy_order in own_orders.bids:
            self.logger.info(f" > BUY: {buy_order.output_reference} ")
