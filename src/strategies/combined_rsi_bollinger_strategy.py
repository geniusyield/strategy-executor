import logging
import time
from datetime import datetime
from typing import Dict, Optional

from talipp.indicators import BB, RSI

from api import Api
from src.data_extraction.fear_and_greed_index_web_scraper import (
    FearAndGreedIndexWebScraper,
)
from src.models.candlestick import Candlestick
from src.utils.logger_utils import LoggerUtils
from src.utils.market_maker import MarketMaker


# pylint: disable=invalid-name
class combined_rsi_bollinger_strategy:
    """
    A trading strategy combining RSI, Bollinger Bands, and optionally Fear & Greed Index.

    This class implements a trading strategy that uses RSI and Bollinger Bands indicators,
    along with an optional Fear & Greed Index to make buy and sell decisions in a given market.

    Attributes:
        api_client (Api): The API client for market interactions.
        logger (logging.Logger): Logger for outputting information and errors.
        market_maker (MarketMaker): Handles order placement and management.
        rsi (RSI): RSI indicator instance.
        bb (BB): Bollinger Bands indicator instance.
        fgis (Optional[FearGreedIndexScraper]): Fear & Greed Index scraper, if enabled.
    """

    def __init__(self, api_client: Api, config: Dict[str, any], logger: logging.Logger):
        """
        Initialize the Combined RSI Bollinger strategy.

        Args:
            api_client (Api): The API client for market interactions.
            config (Dict[str, any]): Configuration parameters for the strategy.
            logger (logging.Logger): Logger for outputting information and errors.

        Raises:
            ValueError: If the configuration is invalid.
        """
        logger.info(" > init: combined_rsi_bollinger_strategy instance created.")
        LoggerUtils.log_warning(logger)

        self.api_client = api_client
        self.logger = logger
        self.initialized = False
        self.last_candle: Optional[Candlestick] = None
        self.last_execution_time: Optional[datetime] = None
        self.cached_fear_and_greed_index = None

        try:
            self.validate_config(config)
        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise

        self._initialize_strategy_parameters(config)
        self._log_strategy_configuration()
        self._initialize_indicators(config)

    def _initialize_strategy_parameters(self, config: Dict[str, any]) -> None:
        """Initialize strategy parameters from the configuration."""
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

    def _log_strategy_configuration(self) -> None:
        """Log the strategy configuration."""
        self.logger.info(" STRATEGY CONFIGURATION:")
        self.logger.info(f" > base_asset : {self.base_asset}")
        self.logger.info(f" > target_asset : {self.target_asset}")
        self.logger.info(f" > market : {self.market}")
        self.logger.info(f" > position_size : {self.position_size}")
        self.logger.info(f" > rsi_period : {self.rsi_period}")
        self.logger.info(f" > rsi_overbought : {self.rsi_overbought}")
        self.logger.info(f" > rsi_oversold : {self.rsi_oversold}")
        self.logger.info(f" > bb_period : {self.bb_period}")
        self.logger.info(f" > bb_std_dev : {self.bb_std_dev}")
        self.logger.info(f" > use_fear_and_greed : {self.use_fear_and_greed}")
        if self.use_fear_and_greed:
            self.logger.info(f" > fear_greed_threshold: {self.fear_and_greed_index_threshold}")

    def _initialize_indicators(self, config: Dict[str, any]) -> None:
        """Initialize strategy indicators and components."""
        self.rsi = RSI(self.rsi_period)
        self.bb = BB(self.bb_period, self.bb_std_dev)
        self.market_maker = MarketMaker(self.api_client, config, self.logger)
        self.fgis = FearAndGreedIndexWebScraper(self.logger) if self.use_fear_and_greed else None

    @staticmethod
    def validate_config(config: Dict[str, any]) -> None:
        """
        Validate the configuration parameters.

        Args:
            config (Dict[str, any]): The configuration dictionary to validate.

        Raises:
            ValueError: If any configuration parameter is invalid or missing.
        """
        required_fields = [
            "POSITION_SIZE_LOVELACES", "RSI_PERIOD", "RSI_OVERBOUGHT", "RSI_OVERSOLD",
            "BB_PERIOD", "BB_STD_DEV", "BASE_ASSET", "TARGET_ASSET", "FEAR_AND_GREED_INDEX_THRESHOLD"
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
            assert 0 <= int(config["FEAR_AND_GREED_INDEX_THRESHOLD"]) <= 100, \
                "FEAR_AND_GREED_INDEX_THRESHOLD must be between 0 and 100"
            assert isinstance(config["BASE_ASSET"], str) and config["BASE_ASSET"].strip(), \
                "BASE_ASSET should be a non-empty string"
            assert isinstance(config["TARGET_ASSET"], str) and config["TARGET_ASSET"].strip(), \
                "TARGET_ASSET should be a non-empty string"
        except ValueError as e:
            raise ValueError(f"Invalid configuration value: {str(e)}") from e
        except AssertionError as e:
            raise ValueError(f"Configuration validation failed: {str(e)}") from e

    def get_fear_and_greed_index(self) -> Optional[int]:
        """
        Get the current Fear and Greed Index value.

        Returns:
            Optional[int]: The Fear and Greed Index value, or None if not available or not used.
        """
        if not self.use_fear_and_greed or self.fgis is None:
            return None
        return self.fgis.get_index_value() or self.fear_and_greed_index_threshold

    def process_candle(self, candle: Candlestick) -> None:
        """
        Process a new candle and make trading decisions.

        Args:
            candle (Candle): The new candle to process.
        """
        if self.initialized:
            self.logger.info(f" > processing candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}")
        else:
            self.logger.info(
                f" > processing init candle - timestamp: {candle.timestamp} - base_close: {candle.base_close}"
            )

        if self.last_candle and self.last_candle.timestamp == candle.timestamp:
            self.logger.info(" > Candle has already been processed. Nothing to do.")
            return

        self.last_candle = candle

        value = float(candle.base_close)
        self.rsi.add(value)
        self.bb.add(value)

        if len(self.rsi) < self.rsi_period or len(self.bb) < self.bb_period:
            self.logger.info(
                f" Indicators: Initializing... RSI({len(self.rsi)}/{self.rsi_period}), \
                    BB({len(self.bb)}/{self.bb_period}) ⚙️ ⏳ "
            )
            return

        self._log_indicator_values(value)

        if not self.initialized:
            self.logger.info(" -> Initialization phase. Do not place orders yet.")
            return

        self._execute_trading_logic(value)

    # pylint: disable=unused-argument
    def _log_indicator_values(self, value: float) -> None:
        """Log the current values of the indicators."""
        current_rsi = self.rsi[-1]
        current_bb = self.bb[-1]
        middle_band = (current_bb.ub + current_bb.lb) / 2
        fear_and_greed_index = None
        if self.initialized:
            # Prevent unnecessary calls to external website.
            fear_and_greed_index = self.get_fear_and_greed_index()
            self.cached_fear_and_greed_index = fear_and_greed_index

        self.logger.info(f" RSI: {current_rsi:.2f}")
        self.logger.info(f" BB: Lower {current_bb.lb:.2f}, Middle {middle_band:.2f}, Upper {current_bb.ub:.2f}")
        if fear_and_greed_index is not None:
            self.logger.info(f" Fear & Greed Index: {fear_and_greed_index}")
        else:
            self.logger.info(" Fear & Greed Index: Not available")

    def _execute_trading_logic(self, value: float) -> None:
        """Execute the trading logic based on indicator values."""
        current_rsi = self.rsi[-1]
        current_bb = self.bb[-1]
        fear_and_greed_index = self.cached_fear_and_greed_index or self.get_fear_and_greed_index()

        buy_signal = (current_rsi < self.rsi_oversold and value <= current_bb.lb)
        sell_signal = (current_rsi > self.rsi_overbought and value >= current_bb.ub)

        if fear_and_greed_index is not None:
            buy_signal = buy_signal and (fear_and_greed_index < self.fear_and_greed_index_threshold)
            sell_signal = sell_signal and (fear_and_greed_index > 100 - self.fear_and_greed_index_threshold)

        if buy_signal:
            self._handle_buy_signal(fear_and_greed_index)
        elif sell_signal:
            self._handle_sell_signal(fear_and_greed_index)
        else:
            self.logger.info(" -> No clear signal or conflicting indicators. Holding position.")

        self.market_maker.log_orders()

    def _handle_buy_signal(self, fear_and_greed_index: Optional[int]) -> None:
        """Handle a buy signal."""
        self.logger.info(" -> Strong BUY signal: RSI oversold, price below lower BB" +
                         (f", high fear (index: {fear_and_greed_index})" if fear_and_greed_index is not None else ""))
        self.market_maker.cancel_sell_orders()
        if not self.market_maker.get_buy_orders():
            self.market_maker.place_buy_order(self.last_candle.base_close)
        else:
            self.logger.info(" > Already placed BUY order. Nothing to do.")

    def _handle_sell_signal(self, fear_and_greed_index: Optional[int]) -> None:
        """Handle a sell signal."""
        self.logger.info(" -> Strong SELL signal: RSI overbought, price above upper BB" +
                         (f", high greed (index: {fear_and_greed_index})" if fear_and_greed_index is not None else ""))
        self.market_maker.cancel_buy_orders()
        if not self.market_maker.get_sell_orders():
            self.market_maker.place_sell_order(self.last_candle.base_close)
        else:
            self.logger.info(" > Already placed SELL order. Nothing to do.")

    # pylint: disable=unused-argument
    def execute(self, api_client: Api, config: Dict[str, any], logger: logging.Logger) -> None:
        """
        Execute the strategy.

        This method is called periodically to process new market data and make trading decisions.

        Args:
            api_client (Api): The API client for market interactions.
            config (Dict[str, any]): Configuration parameters for the strategy.
            logger (logging.Logger): Logger for outputting information and errors.
        """
        current_time = datetime.now()

        if self.last_execution_time is None:
            self._initialize_strategy(api_client)
        else:
            time_since_last_execution = (current_time - self.last_execution_time).total_seconds()
            logger.info(f"Last executed: {self.last_execution_time}")
            logger.info(f"Seconds since last execution: {time_since_last_execution} seconds")

        self.last_execution_time = current_time
        self.initialized = True

        try:
            market_price = api_client.get_market_price(self.market)
            print(market_price)
            candle = market_price[0]
            self.process_candle(candle)
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logger.error(" > ⚠️ [FAILED] could not process candle ⚠️")
            logger.exception(f" > Exception: {str(e)}")

    def _initialize_strategy(self, api_client: Api) -> None:
        """
        Initialize the strategy with historical data.

        Args:
            api_client (Api): The API client for fetching historical data.
        """
        self.logger.info("Executing for the first time -> initialize.")
        candles = api_client.get_price_history(
            self.market,
            resolution="1m",
            sort="asc",
            limit=max(self.rsi_period, self.bb_period) * 5
        )
        for candle in candles[:-1]:
            self.logger.info("--------------------------------------------------------------------------------")
            self.process_candle(candle)
            time.sleep(1)
        self.logger.info(" > [OK] Initialized.")
        self.logger.info("========================================================================")
        self.initialized = True
        self.last_candle = None
