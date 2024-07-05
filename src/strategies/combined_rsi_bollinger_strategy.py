import time
from datetime import datetime

from talipp.indicators import BB, RSI

from api import Api
from src.utils.market_maker import MarketMaker
from src.web_scrapers.fear_greed_index_scraper import FearGreedIndexScraper


# pylint: disable=invalid-name
class combined_rsi_bollinger_strategy:
    def __init__(self, api_client, config, logger):
        logger.info(" > init: combined_rsi_bollinger_strategy instance created.")

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
        self.api_client: Api = api_client
        self.logger = logger
        self.initialized = False
        self.last_candle = None

        # Validate configuration
        try:
            self.validate_config(config)
        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise

        # Strategy Configuration:
        self.position_size = float(config["POSITION_SIZE_LOVELACES"])
        self.rsi_period = int(config["RSI_PERIOD"])
        self.rsi_overbought = float(config["RSI_OVERBOUGHT"])
        self.rsi_oversold = float(config["RSI_OVERSOLD"])
        self.bb_period = int(config["BB_PERIOD"])
        self.bb_std_dev = float(config["BB_STD_DEV"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"
        self.use_fear_and_greed = config.get("USE_FEAR_AND_GREED", False)
        self.fear_and_greed_index_threshold = int(config["FEAR_AND_GREED_INDEX_THRESHOLD"])

        # Log strategy configuration
        logger.info(" STRATEGY CONFIGURATION:")
        logger.info(f" > base_asset         : {self.base_asset}")
        logger.info(f" > target_asset       : {self.target_asset}")
        logger.info(f" > market             : {self.market}")
        logger.info(f" > position_size      : {self.position_size}")
        logger.info(f" > rsi_period         : {self.rsi_period}")
        logger.info(f" > rsi_overbought     : {self.rsi_overbought}")
        logger.info(f" > rsi_oversold       : {self.rsi_oversold}")
        logger.info(f" > bb_period          : {self.bb_period}")
        logger.info(f" > bb_std_dev         : {self.bb_std_dev}")
        logger.info(f" > use_fear_and_greed     : {self.use_fear_and_greed}")
        if self.use_fear_and_greed:
            logger.info(f" > fear_greed_threshold: {self.fear_and_greed_index_threshold}")

        # Create indicator instances
        self.rsi = RSI(self.rsi_period)
        self.bb = BB(self.bb_period, self.bb_std_dev)

        self.market_maker = MarketMaker(api_client, config, logger)

        if self.use_fear_and_greed:
            self.fgis = FearGreedIndexScraper(self.logger)
        else:
            self.fgis = None

    def validate_config(self, config):
        required_fields = [
            "POSITION_SIZE_LOVELACES",
            "RSI_PERIOD",
            "RSI_OVERBOUGHT",
            "RSI_OVERSOLD",
            "BB_PERIOD",
            "BB_STD_DEV",
            "BASE_ASSET",
            "TARGET_ASSET",
            "FEAR_AND_GREED_INDEX_THRESHOLD"
        ]

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required configuration field: {field}")

        # Validate types and ranges
        try:
            assert float(config["POSITION_SIZE_LOVELACES"]) > 0, "POSITION_SIZE_LOVELACES must be positive"
            assert 2 <= int(config["RSI_PERIOD"]) <= 100, "RSI_PERIOD must be between 2 and 100"
            assert 50 <= float(config["RSI_OVERBOUGHT"]) <= 100, "RSI_OVERBOUGHT must be between 50 and 100"
            assert 0 <= float(config["RSI_OVERSOLD"]) <= 50, "RSI_OVERSOLD must be between 0 and 50"
            assert 2 <= int(config["BB_PERIOD"]) <= 100, "BB_PERIOD must be between 2 and 100"
            assert 0 < float(config["BB_STD_DEV"]) <= 5, "BB_STD_DEV must be between 0 and 5"
            assert 0 <= int(config["FEAR_AND_GREED_INDEX_THRESHOLD"]) <= 100, "FEAR_AND_GREED_INDEX_THRESHOLD must be between 0 and 100"
        except ValueError as e:
            raise ValueError(f"Invalid configuration value: {str(e)}") from e
        except AssertionError as e:
            raise ValueError(f"Configuration validation failed: {str(e)}") from e

        # Validate asset names (check if string is provided and not empty)
        assert isinstance(config["BASE_ASSET"], str) and config["BASE_ASSET"].strip(), "BASE_ASSET should be a non-empty string"
        assert isinstance(config["TARGET_ASSET"], str) and config["TARGET_ASSET"].strip(), "TARGET_ASSET should be a non-empty string"

    def get_fear_and_greed_index(self):
        if not self.use_fear_and_greed or self.fgis is None:
            return None

        return self.fgis.get_index_value() or self.fear_and_greed_index_threshold

    def process_candle(self, candle):
        if self.initialized:
            self.logger.info(f" > processing candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")
        else:
            self.logger.info(f" > processing init candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")

        if (not self.last_candle is None) and (self.last_candle.timestamp == candle.timestamp):
            self.logger.info(" > Candle has already been processed. Nothing to do.")
            return

        self.last_candle = candle

        # Feed the indicators
        value = float(candle.base_close)
        self.rsi.add(value)
        self.bb.add(value)

        if len(self.rsi) < self.rsi_period or len(self.bb) < self.bb_period:
            self.logger.info(f" Indicators: Initializing... RSI({len(self.rsi)}/{self.rsi_period}), BB({len(self.bb)}/{self.bb_period})  ⚙️ ⏳ ")
            return

        current_rsi = self.rsi[-1]
        current_bb = self.bb[-1]
        # Calculate middle band as average of upper and lower bands
        middle_band = (current_bb.ub + current_bb.lb) / 2
        
        if self.initialized:
            fear_and_greed_index = self.get_fear_and_greed_index()

        self.logger.info(f" RSI: {current_rsi:.2f}")
        self.logger.info(f" BB: Lower {current_bb.lb:.2f}, Middle {middle_band:.2f}, Upper {current_bb.ub:.2f}")
        if self.initialized:
            if fear_and_greed_index is not None:
                self.logger.info(f" Fear & Greed Index: {fear_and_greed_index}")
            else:
                self.logger.info(" Fear & Greed Index: Not available")

        if not self.initialized:
            self.logger.info(" -> Initialization phase. Do not place orders yet.")
            return

        # Trading logic
        buy_signal = (current_rsi < self.rsi_oversold and value <= current_bb.lb)
        sell_signal = (current_rsi > self.rsi_overbought and value >= current_bb.ub)

        if fear_and_greed_index is not None:
            buy_signal = buy_signal and (fear_and_greed_index < self.fear_and_greed_index_threshold)
            sell_signal = sell_signal and (fear_and_greed_index > 100 - self.fear_and_greed_index_threshold)

        if buy_signal:
            self.logger.info(" -> Strong BUY signal: RSI oversold, price below lower BB" +
                            (f", high fear (index: {fear_and_greed_index})" if fear_and_greed_index is not None else ""))
            self.market_maker.cancel_sell_orders()
            if len(self.market_maker.get_buy_orders()) > 0:
                self.logger.info(" > Already placed BUY order. Nothing to do.")
            else:
                self.market_maker.place_buy_order(candle.base_close)
        elif sell_signal:
            self.logger.info(" -> Strong SELL signal: RSI overbought, price above upper BB" +
                            (f", high greed (index: {fear_and_greed_index})" if fear_and_greed_index is not None else ""))
            self.market_maker.cancel_buy_orders()
            if len(self.market_maker.get_sell_orders()) > 0:
                self.logger.info(" > Already placed SELL order. Nothing to do.")
            else:
                self.market_maker.place_sell_order(candle.base_close)
        else:
            self.logger.info(" -> No clear signal or conflicting indicators. Holding position.")

        self.market_maker.log_orders()

    # pylint: disable=unused-argument
    def execute(self, api_client: Api, config, logger):
        current_time = datetime.now()

        if self.last_execution_time is None:
            logger.info("Executing for the first time -> initialize.")
            candles = api_client.get_price_history(self.market, resolution="1m", sort="asc", limit=max(self.rsi_period, self.bb_period)*5)
            for candle in candles[:-1]:
                self.logger.info("--------------------------------------------------------------------------------")
                self.process_candle(candle)
                time.sleep(1)
            logger.info(" > [OK] Initialized.")
            logger.info("========================================================================")
            self.initialized = True
            self.last_candle = None
        else:
            time_since_last_execution = (current_time - self.last_execution_time).total_seconds()
            logger.info(f"Last executed: {self.last_execution_time}")
            logger.info(f"Seconds since last execution: {time_since_last_execution} seconds")

        self.last_execution_time = current_time  # Update last execution time
        self.initialized = True

        try:
            get_market_price = api_client.get_market_price(self.market)
            print(get_market_price)
            candle = get_market_price[0]
            self.process_candle(candle)
        # pylint: disable=bare-except
        except:
            logger.error(" > ⚠️ [FAILED] could not process candle ⚠️")
            logger.exception(" > Exception! ")
