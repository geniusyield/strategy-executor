from datetime import datetime
import math
from api import Api, ApiException
import time

from talipp.indicators import BB

class bollinger_bands_strategy:
    def __init__(self, api_client, CONFIG, logger):
        logger.info(" > init: bollinger_bands_strategy instance created.")

        logger.info("========================================================================")
        logger.info("                                                                        ")
        logger.info("                      ⚠️     WARNING!    ⚠️                            ")
        logger.info("                                                                        ")
        logger.info(" THIS IS ONLY A PROOF-OF-CONCEPT EXAMPLE STRATEGY IMPLEMENTATION.       ")
        logger.info("                                                                        ")
        logger.info(" IT IS ONLY INTENDED AS IMPLEMENTATION REFERENCE FOR TRADING STRATEGIES.")
        logger.info("                                                                        ")
        logger.info(" THIS IMPLEMENTATION IS NOT PRODUCTION-READY.                           ")
        logger.info("                                                                        ")
        logger.info("========================================================================")

        # Internal state:
        self.last_execution_time = None
        self._values = (None, None)
        self.api_client : Api = api_client
        self.logger = logger
        self.initialized = False
        self.last_candle = None

        # Strategy configuration:
        self.position_size = float(CONFIG["POSITION_SIZE_LOVELACES"])
        self.std_dev_multiplier = float(CONFIG["STD_DEV_MULTIPLIER"])
        self.period = int(CONFIG["PERIOD"])
        self.base_asset = CONFIG["BASE_ASSET"]
        self.target_asset = CONFIG["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"
        logger.info(" STRATEGY CONFIGURATION:")
        logger.info(f" > base_asset         : {self.base_asset}")
        logger.info(f" > target_asset       : {self.target_asset}")
        logger.info(f" > market             : {self.market}")
        logger.info(f" > position_size      : {self.position_size}")
        logger.info(f" > std_dev_multiplier : {self.std_dev_multiplier}")
        logger.info(f" > period             : {self.period}")

        # Create the BB strategy instance with the config:
        self.bb = BB(self.period, self.std_dev_multiplier)

    def place_buy_order(self, api_client, logger, price):
        logger.info(" ⚙️ Placing BUY order...")

        try:
            balance_available = int(api_client.get_balances().get(self.base_asset, 0))
            logger.debug(f" > balance_available : {balance_available}")
            logger.debug(f" > self.position_size: {self.position_size}")

            order_size = min(self.position_size, balance_available)
            if not order_size:
                logger.info(" ⚠️ Insufficient balance to place BUY order! ⚠️")
                return

            offered_amount = int(math.floor(order_size))

            logger.info(f" > Place BUY order: {offered_amount}  at price {price}...")
            response = api_client.place_order(
                     offered_amount=f"{offered_amount}",
                     offered_token=self.base_asset,
                     price_token=self.target_asset,
                     price_amount=f"{int(math.floor(offered_amount / price))}"
            )
            logger.info(f" > [OK] PLACED NEW BUY ORDER: {response.order_ref}")
        except:
            logger.error(" > ⚠️ [FAILED] Could not place BUY order. ⚠️")
            logger.exception(f" > Exception! ")

    def place_sell_order(self, api_client, logger, price):
        logger.info("Placing SELL order...")

        self.cancel_buy_orders()

        if len(self.get_sell_orders()) > 0:
            logger.info("Already placed SELL order. Nothing to do.")
            return

        try:
            balance_available = int(api_client.get_balances().get(self.target_asset, 0))
            logger.info(f" > balance_available : {balance_available}")
            order_size = min(self.position_size / price, balance_available)
            logger.info(f" > order_size : {order_size}")
            logger.info(f" > price : {price}")
            if not order_size:
                logger.info("⚠️ Insufficient balance to place SELL order! ⚠️")
                return

            logger.info(f" > Place SELL order: {order_size} at price {price}...")
            response = api_client.place_order(
              offered_amount=f"{int(math.floor(order_size))}",
              offered_token=self.target_asset,
              price_token=self.base_asset,
              price_amount=f"{int(math.floor(order_size * price))}"
            )
            logger.info(f" > [OK] PLACED NEW SELL ORDER: {response.order_ref}")
            self.sell_order_ref = response.order_ref
        except:
            logger.error(f" > ⚠️ [FAILED] Could not place SELL order. ⚠️")
            logger.exception(f" > Exception! ")

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
            if (side == "ask"):
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
                self.logger.error(f" > ⚠️ [FAILED] could not cancel order: {order.output_reference} ⚠️")
                self.logger.exception(f" > Exception! ")

    def process_candle(self, candle):
        if self.initialized:
            self.logger.info(f" > processsing candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")
        else:
            self.logger.info(f" > processsing init candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")

        if (not self.last_candle == None) and (self.last_candle.timestamp == candle.timestamp):
            self.logger.info(f" > Candle has already been processsed. Nothing to do.")
            return

        self.last_candle = candle

        # Feed the technical indicator.
        value = float(candle.base_close)
        self.bb.add(value)

        # Keep a small window of values to check if there is a crossover.
        self._values = (self._values[-1], value)

        if len(self.bb) < 2 or self.bb[-1] == None or self.bb[-2] == None:
           self.logger.info(f" BOLLINGER BANDS: Initializing...  ⚙️ ⏳ ")
           self.logger.info(f" > Upper band: Not available.")
           self.logger.info(f" > Lower band: Not available.")
           return

        self.logger.info(f" BOLLINGER BANDS: ")
        self.logger.info(f" > Upper band: {self.bb[-1].ub}")
        self.logger.info(f" > Lower band: {self.bb[-1].lb}")

        if self.initialized == False:
            self.logger.info(f" -> Initializaion phase. Do not place orders yet.")
            return

        self.place_buy_order(self.api_client, self.logger, candle.base_close)

        # Price moved below lower band ?
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self.logger.info(f" -> Price moved below the lower band -> BUY!  🛒 🛒 🛒 ")
            self.cancel_sell_orders()
            if len(self.get_buy_orders()) > 0:
                self.logger.info(" > Already placed BUY order. Nothing to do.")
            else:
                self.place_buy_order(self.api_client, self.logger, candle.base_close)
        # Price moved above upper band ?
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self.logger.info(f" -> Price moved above the upper band -> SELL!  💲 💲 💲 ")
            self.cancel_buy_orders()
            if len(self.get_sell_orders()) > 0:
                self.logger.info(" > Already placed SELL order. Nothing to do.")
            else:
                self.place_sell_order(self.api_client, self.logger, candle.base_low)

        self.log_orders()

    def log_orders(self):
        own_orders = self.api_client.get_own_orders(self.market)

        self.logger.info(" ON-CHAIN ORDERS:")

        if (len(own_orders.asks) + len(own_orders.bids)) == 0:
            self.logger.info(f" > No orders.")
            return

        for sell_order in own_orders.asks:
            self.logger.info(f" > SELL: {sell_order.output_reference}")

        for buy_order in own_orders.bids:
            self.logger.info(f" > BUY: {buy_order.output_reference} ")

    def execute(self, api_client : Api, CONFIG, logger):
        current_time = datetime.now()

        if self.last_execution_time is None:
            logger.info("Executing for the first time -> initialize.")
            candles = api_client.get_price_history(self.market, resolution="1m", sort="asc", limit=self.period*5)
            for candle in candles[:-1]:
                self.logger.info(f"--------------------------------------------------------------------------------")
                self.process_candle(candle)
                time.sleep(1)
            logger.info(" > [OK] Initialized.")
            logger.info("========================================================================")
            self.initialized = True
            self.last_candle=None
        else:
            time_since_last_execution = (current_time - self.last_execution_time).total_seconds()
            logger.info(f"Last executed: {self.last_execution_time}")
            logger.info(f"Seconds since last execution: {time_since_last_execution} seconds")

        self.last_execution_time = current_time  # Update last execution time
        self.initialized = True

        try:
            get_market_price = api_client.get_market_price(self.market)
            candle=get_market_price[0]
            self.process_candle(candle)
        except:
            logger.error(f" > ⚠️ [FAILED] could not process candle ⚠️")
            logger.exception(f" > Exception! ")
