from datetime import datetime
import math
from api import Api
import time

from talipp.indicators import BB

class bollinger_bands_strategy:
    def __init__(self, api_client, CONFIG, logger):
        logger.info(" > init: bollinger_bands_strategy instance created.")

        # Internal state:
        self.start_time = datetime.now()
        self.counter = 0
        self.last_execution_time = None
        self.last_order_ref=None
        self._values = (None, None)
        self.api_client=api_client
        self.logger=logger
        self.initialized = False
        self.sell_order_ref = None
        self.buy_order_ref = None
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

    def place_buy_order(self, api_client, logger):
        logger.info(" ⚙️ Placing BUY order...")

        if not self.buy_order_ref == None:
            logger.info(f" > Already placed BUY order. Nothing to do.")
            return
        
        if self.sell_order_ref == None:
            logger.debug(f" > No SELL order. Nothing to cancel.")
        else:
            try:
                response = api_client.cancel_order(self.sell_order_ref)
                logger.info(f" > [OK] Canceled SELL order: {self.sell_order_ref}")
                self.sell_order_ref = None
            except:
                logger.exception(f" > ⚠️ [FAILED] could not cancel order: {self.sell_order_ref} ⚠️")
                logger.error(f" > Exception! ")
        try:
            HUNDRED_ADA=100000000
            balance_available = api_client.get_balances().get(self.base_asset, 0) - HUNDRED_ADA
            logger.debug(f" > balance_available : {balance_available}")
            logger.debug(f" > self.position_size: {self.position_size}")

            # Get best ask price:
            order_book = api_client.get_order_book(self.market)
            best_ask_price = float(order_book.asks[-1].price)
            order_size = min(self.position_size, balance_available) / float(best_ask_price)
            if not order_size:
                logger.info(" ⚠️ Insufficient balance to place BUY order! ⚠️")
                return

            logger.info(f" > Place BUY order: {order_size}...")
            offered_amount = int(math.floor(order_size))
            response = api_client.place_order(
                     offered_amount=f"{offered_amount}",
                     offered_token=self.base_asset,
                     price_token=self.target_asset,
                     price_amount=f"{int(math.floor(offered_amount * best_ask_price))}"
            )
            logger.info(f" > [OK] PLACED NEW BUY ORDER: {response.order_ref}")
            self.buy_order_ref=response.order_ref
        except:
            logger.error(" > ⚠️ [FAILED] Could not place BUY order. ⚠️")
            logger.exception(f" > Exception! ")

    def place_sell_order(self, api_client, logger):
        logger.info("Placing SELL order...")
        
        if not self.sell_order_ref == None:
            logger.info(f" > Already placed SELL order. Nothing to do.")
            return

        if self.buy_order_ref == None:
            logger.debug(f" > No BUY order placed. Nothing to cancel.")
        else:
            try:
                logger.info(f" ⚙️ Canceling BUY order: {self.buy_order_ref}")
                response = api_client.cancel_order(self.buy_order_ref)
                logger.info(f" > [OK] Canceled BUY order: {self.buy_order_ref}")
                self.buy_order_ref = None
            except:
                logger.error(f" > ⚠️ [FAILED] could not cancel order: {self.buy_order_ref} ⚠️")
                logger.exception(f" > Exception! ")
        try:
            balance_available = api_client.get_balances().get(self.target_asset, 0)
            logger.info(f" > balance_available : {balance_available}")

            order_book = api_client.get_order_book(self.market)
            best_bid_price = order_book.bids[-1].price
            order_size = min(self.position_size, balance_available) / float(best_bid_price)
            if not order_size:
                logger.info("⚠️ Insufficient balance to place SELL order! ⚠️")
                return

            logger.info(f" > Place SELL order: {order_size} at ...")
            response = api_client.place_order(
              offered_amount=f"{int(math.floor(order_size))}",
              offered_token=self.target_asset,
              price_token=self.target_asset,
              price_amount=f"{int(math.floor(best_bid_price))}"
            )
            logger.info(f" > [OK] PLACED NEW SELL ORDER: {response.order_ref}")
            self.sell_order_ref=response.order_ref
        except:
            logger.error(f" > ⚠️ [FAILED] Could not place SELL order. ⚠️")
            logger.exception(f" > Exception! ")

    def process_candle(self, candle):
        self.logger.info(f"--------------------------------------------------------------------------------")
        self.logger.info(f" > processsing candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")

        if (not self.last_candle == None) and (self.last_candle.timestamp == candle.timestamp):
            self.logger.info(f" > Candle has already been processsed.")
            return

        self.last_candle = candle

        # Feed the technical indicator.
        value = float(candle.base_close)
        self.bb.add(value)

        # Keep a small window of values to check if there is a crossover.
        self._values = (self._values[-1], value)

        self.logger.debug(f" > self.bb.input_values: {self.bb.input_values}")

        if len(self.bb) < 2 or self.bb[-1] == None or self.bb[-2] == None:
           self.logger.info(f" Bollinger Bands: Initializing...  ⚙️ ⏳ ")
           self.logger.info(f" > Upper band: Not available.")
           self.logger.info(f" > Lower band: Not available.")
           self.logger.info(f" Orders: ")
           self.logger.info(f" > On-Chain BUY order: {self.buy_order_ref} ")
           self.logger.info(f" > On-Chain SELL order: {self.sell_order_ref} ")
           return

        self.logger.info(f" Bollinger Bands: ")
        self.logger.info(f" > Upper band: {self.bb[-1].ub}")
        self.logger.info(f" > Lower band: {self.bb[-1].lb}")

        # Price moved below lower band ?
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self.logger.info(f" > Price moved below the lower band -> BUY!  🛒 🛒 🛒 ")
            self.place_buy_order(self.api_client, self.logger)
        # Price moved above upper band ?
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self.logger.info(f" > Price moved above the upper band -> SELL!  💲 💲 💲 ")
            self.place_sell_order(self.api_client, self.logger)
        
        self.logger.info(f" Orders: ")
        self.logger.info(f" > On-Chain BUY order: {self.buy_order_ref} ")
        self.logger.info(f" > On-Chain SELL order: {self.sell_order_ref} ")


    def execute(self, api_client : Api, CONFIG, logger):
        current_time = datetime.now()

        if self.last_execution_time is None:
            logger.info("Executing for the first time")
            candles = api_client.get_price_history(self.market, resolution="1m", sort="asc", limit=self.period)
            for candle in candles[:-1]:
                self.process_candle(candle)
                time.sleep(1)
        else:
            time_since_last_execution = (current_time - self.last_execution_time).total_seconds()
            logger.info(f"Last executed: {self.last_execution_time}")
            logger.info(f"Seconds since last execution: {time_since_last_execution} seconds")

        self.last_execution_time = current_time  # Update last execution time
        self.initialized = True

        self.counter += 1
        logger.info(f" > Counter: {self.counter}")

        try:
            get_market_price = api_client.get_market_price(self.market)
            candle=get_market_price[0]
            logger.info(f" > Base closing price: {candle.base_close}")
            self.process_candle(candle)
        except:
            logger.error(f" > ⚠️ [FAILED] could not process candle ⚠️")
            logger.exception(f" > Exception! ")

        logger.info(f" > EXECUTION FINISHED.")
