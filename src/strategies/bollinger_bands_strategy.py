import time
from datetime import datetime

from talipp.indicators import BB

from api import Api
from src.utils.market_maker import MarketMaker


# pylint: disable=invalid-name
class bollinger_bands_strategy:
    def __init__(self, api_client, config, logger):
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

        # Strategy Configuration:
        self.position_size = float(config["POSITION_SIZE_LOVELACES"])
        self.std_dev_multiplier = float(config["STD_DEV_MULTIPLIER"])
        self.period = int(config["PERIOD"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
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

        self.market_maker = MarketMaker(api_client, config, logger)

    def process_candle(self, candle):
        if self.initialized:
            self.logger.info(f" > processing candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")
        else:
            self.logger.info(f" > processing init candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")

        if (not self.last_candle is None) and (self.last_candle.timestamp == candle.timestamp):
            self.logger.info(" > Candle has already been processed. Nothing to do.")
            return

        self.last_candle = candle

        # Feed the technical indicator.
        value = float(candle.base_close)
        self.bb.add(value)

        # Keep a small window of values to check if there is a crossover.
        self._values = (self._values[-1], value)

        if len(self.bb) < 2 or self.bb[-1] is None or self.bb[-2] is None:
            self.logger.info(" BOLLINGER BANDS: Initializing...  ⚙️ ⏳ ")
            self.logger.info(" > Upper band: Not available.")
            self.logger.info(" > Lower band: Not available.")
            return

        self.logger.info(" BOLLINGER BANDS: ")
        self.logger.info(f" > Upper band: {self.bb[-1].ub}")
        self.logger.info(f" > Lower band: {self.bb[-1].lb}")

        if self.initialized is False:
            self.logger.info(" -> Initialization phase. Do not place orders yet.")
            return

        self.market_maker.place_buy_order(candle.base_close)

        # Price moved below lower band ?
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self.logger.info(" -> Price moved below the lower band -> BUY!  🛒 🛒 🛒 ")
            self.market_maker.cancel_sell_orders()
            if len(self.market_maker.get_buy_orders()) > 0:
                self.logger.info(" > Already placed BUY order. Nothing to do.")
            else:
                self.market_maker.place_buy_order(candle.base_close)
        # Price moved above upper band ?
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self.logger.info(" -> Price moved above the upper band -> SELL!  💲 💲 💲 ")
            self.market_maker.cancel_buy_orders()
            if len(self.market_maker.get_sell_orders()) > 0:
                self.logger.info(" > Already placed SELL order. Nothing to do.")
            else:
                self.market_maker.place_sell_order(candle.base_close)

        self.market_maker.log_orders()

    # pylint: disable=unused-argument
    def execute(self, api_client : Api, config, logger):
        current_time = datetime.now()

        if self.last_execution_time is None:
            logger.info("Executing for the first time -> initialize.")
            # pylint: disable=line-too-long
            candles = api_client.get_price_history(self.market, resolution="1m", sort="asc", limit=self.period*5)
            for candle in candles[:-1]:
                self.logger.info("--------------------------------------------------------------------------------")
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
            print(get_market_price)
            candle=get_market_price[0]
            self.process_candle(candle)
        # pylint: disable=bare-except
        except:
            logger.error(" > ⚠️ [FAILED] could not process candle ⚠️")
            logger.exception(" > Exception! ")
