from datetime import datetime, timedelta
import math
from api import ApiException
from decimal import Decimal
import asyncio
import logging

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
        logger.info(" CONFIG:")
        logger.info(f" > base_asset         : {self.base_asset}")
        logger.info(f" > target_asset       : {self.target_asset}")
        logger.info(f" > market             : {self.market}")
        logger.info(f" > position_size      : {self.position_size}")
        logger.info(f" > std_dev_multiplier : {self.std_dev_multiplier}")
        logger.info(f" > period             : {self.period}")

        # Create the BB strategy instance with the config:
        self.bb = BB(self.period, self.std_dev_multiplier)

    def place_buy_order(self, api_client, logger):
        logging.info("Placing BUY order...")

        if self.sell_order_ref == None:
            logger.info(f" > No SELL order. Nothing to cancel.")
        else:
            try:
                response = api_client.cancel_order(self.sell_order_ref)
                logger.info(f" > [OK] Canceled SELL order: {self.sell_order_ref}")
                self.sell_order_ref = None
            except:
                logger.exception(f" > [FAILED] could not cancel order. ❌")

        try:
            # Get available balance (keep 100 ADA):
            HUNDRED_ADA=100000000
            balance_available = api_client.get_balances()[self.base_asset] - 100000000
            logging.info(" > balance_available : {balance_available}")
            logging.info(" > self.position_size: {self.position_size}")

            # Get best ask price:
            order_book = api_client.get_order_book(self.market)
            best_ask_price = float(order_book.asks[-1].price)
            order_size = min(self.position_size, balance_available) / float(best_ask_price)
            if not order_size:
                logging.info("Insufficient balance to place BUY order!")
                return

            logging.info(" > Place BUY order: {position_size}...")
            try:
                offered_amount = int(math.floor(order_size))
                response = api_client.place_order(
                         offered_amount=f"{offered_amount}",
                         offered_token=self.base_asset,
                         price_token=self.target_asset,
                         price_amount=f"{int(math.floor(offered_amount * best_ask_price))}"
                )
                logger.info(f" > [OK] PLACED NEW ORDER: {response.order_ref}")
                self.buy_order_ref=response.order_ref
            except:
                logger.exception(f" > [FAILED] could not place BUY order. ❌")
        except:
            logging.exception("Could not place BUY order.")

    def place_sell_order(self, api_client, logger):
        logging.info("Placing SELL order...")

        if self.buy_order_ref == None:
            logger.info(f" > No buy order. Nothing to cancel.")
        else:
            try:
                response = api_client.cancel_order(self.buy_order_ref)
                logger.info(f" > [OK] Canceled BUY order: {self.buy_order_ref}")
                self.buy_order_ref = None
            except:
                logger.exception(f" > [FAILED] could not cancel order. ❌")

        try:
            # Get balance:
            balance_available = api_client.get_balances().get(self.target_asset, 0)
            logging.info(" > balance_available : {balance_available}")

            # Get best bid price:
            order_book = api_client.get_order_book(self.market)
            best_bid_price = order_book.bids[-1].price
            order_size = min(self.position_size, balance_available) / float(best_bid_price)
            if not order_size:
                logging.info("Insufficient balance to place SELL order!")
                return

            logging.info(" > Place SELL order: {order_size} at ...")
            try:
                response = api_client.place_order(
                         offered_amount=f"{int(math.floor(order_size))}",
                         offered_token=self.target_asset,
                         price_token=self.target_asset,
                         price_amount=f"{int(math.floor(best_bid_price))}"
                )
                logger.info(f" > [OK] PLACED NEW ORDER: {response.order_ref}")
                self.buy_order_ref=response.order_ref
            except:
                logger.exception(f" > [FAILED] could not SELL place order. ❌")
        except:
            logging.exception("Could not place SELL order.")

    def process_candle(self, candle):
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

        if not self.initialized:
            self.logger.debug(f" > Initializing.... ")
            return

        if len(self.bb) < 2:
            return
        if self.bb[-1] == None or self.bb[-2] == None:
            return

        self.logger.debug(f" > self.bb: {self.bb}")
        self.logger.debug(f" > self.bb._values: {self._values}")
        self.logger.debug(f" > self.bb.input_values: {self.bb.input_values}")

        self.logger.info(f" Bollinger Bands: ")
        self.logger.info(f" > Upper band: {self.bb[-1].ub}")
        self.logger.info(f" > Lower band: {self.bb[-1].lb}")

        # Price moved below lower band ?
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self.logger.info(f" > Price moved below the lower band -> BUY!")
            self.place_buy_order(self.api_client, self.logger)
        # Price moved above upper band ?
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self.logger.info(f" > Price moved above the upper band -> SELL!")
            self.place_sell_order(self.api_client, self.logger)

    def execute(self, api_client, CONFIG, logger):
        current_time = datetime.now()

        if self.last_execution_time is None:
            logger.info("Executing for the first time")
            candles = api_client.get_price_history(self.market, resolution="1m", from_date=None, until_date=None, sort="asc", limit=self.period)
            for candle in candles[:-1]:
                self.process_candle(candle)
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
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")

        logger.info(f" > EXECUTION FINISHED.")
