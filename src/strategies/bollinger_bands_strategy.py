import logging
import time
from datetime import datetime
from typing import Optional, Tuple

from talipp.indicators import BB

from api import Api
from src.models.candlestick import Candlestick
from src.utils.logger_utils import LoggerUtils
from src.utils.market_maker import MarketMaker


# pylint: disable=invalid-name
class bollinger_bands_strategy:
    """
    A trading strategy based on Bollinger Bands.

    This class implements a trading strategy that uses Bollinger Bands to make
    buy and sell decisions in a given market.

    Attributes:
        api_client (Api): The API client for market interactions.
        logger (logging.Logger): Logger for outputting information and errors.
        market_maker (MarketMaker): Handles order placement and management.
        bb (BB): Bollinger Bands indicator.
        initialized (bool): Whether the strategy has been initialized.
        last_candle (Optional[Candle]): The last processed candle.
        last_execution_time (Optional[datetime]): Timestamp of the last execution.
    """

    def __init__(self, api_client: Api, config: dict, logger: logging.Logger):
        """
        Initialize the Bollinger Bands strategy.

        Args:
            api_client (Api): The API client for market interactions.
            config (dict): Configuration parameters for the strategy.
            logger (logging.Logger): Logger for outputting information and errors.
        """
        logger.info(" > init: bollinger_bands_strategy instance created.")
        LoggerUtils.log_warning(logger)

        self.api_client = api_client
        self.logger = logger
        self.initialized = False
        self.last_candle: Optional[Candlestick] = None
        self.last_execution_time: Optional[datetime] = None
        self._values: Tuple[Optional[float], Optional[float]] = (None, None)

        # Strategy Configuration
        self.position_size = float(config["POSITION_SIZE_LOVELACES"])
        self.std_dev_multiplier = float(config["STD_DEV_MULTIPLIER"])
        self.period = int(config["PERIOD"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"

        self._log_configuration()

        self.bb = BB(self.period, self.std_dev_multiplier)
        self.market_maker = MarketMaker(api_client, config, logger)

    def _log_configuration(self) -> None:
        """Log the strategy configuration."""
        self.logger.info(" STRATEGY CONFIGURATION:")
        self.logger.info(f" > base_asset         : {self.base_asset}")
        self.logger.info(f" > target_asset       : {self.target_asset}")
        self.logger.info(f" > market             : {self.market}")
        self.logger.info(f" > position_size      : {self.position_size}")
        self.logger.info(f" > std_dev_multiplier : {self.std_dev_multiplier}")
        self.logger.info(f" > period             : {self.period}")

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
        self.bb.add(value)
        self._values = (self._values[-1], value)

        if len(self.bb) < 2 or self.bb[-1] is None or self.bb[-2] is None:
            self._log_initialization_status()
            return

        self._log_bollinger_bands()

        if not self.initialized:
            self.logger.info(" -> Initialization phase. Do not place orders yet.")
            return

        self._check_and_place_orders(candle)
        self.market_maker.log_orders()

    def _log_initialization_status(self) -> None:
        """Log the initialization status of Bollinger Bands."""
        self.logger.info(" BOLLINGER BANDS: Initializing...  ⚙️ ⏳ ")
        self.logger.info(" > Upper band: Not available.")
        self.logger.info(" > Lower band: Not available.")

    def _log_bollinger_bands(self) -> None:
        """Log the current Bollinger Bands values."""
        self.logger.info(" BOLLINGER BANDS: ")
        self.logger.info(f" > Upper band: {self.bb[-1].ub}")
        self.logger.info(f" > Lower band: {self.bb[-1].lb}")

    def _check_and_place_orders(self, candle: Candlestick) -> None:
        """
        Check Bollinger Bands crossovers and place orders accordingly.

        Args:
            candle (Candle): The current candle being processed.
        """
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self._handle_buy_signal(candle)
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self._handle_sell_signal(candle)

    def _handle_buy_signal(self, candle: Candlestick) -> None:
        """Handle a buy signal."""
        self.logger.info(" -> Price moved below the lower band -> BUY!  🛒 🛒 🛒 ")
        self.market_maker.cancel_sell_orders()
        if not self.market_maker.get_buy_orders():
            self.market_maker.place_buy_order(candle.base_close)
        else:
            self.logger.info(" > Already placed BUY order. Nothing to do.")

    def _handle_sell_signal(self, candle: Candlestick) -> None:
        """Handle a sell signal."""
        self.logger.info(" -> Price moved above the upper band -> SELL!  💲 💲 💲 ")
        self.market_maker.cancel_buy_orders()
        if not self.market_maker.get_sell_orders():
            self.market_maker.place_sell_order(candle.base_close)
        else:
            self.logger.info(" > Already placed SELL order. Nothing to do.")

    # pylint: disable=unused-argument
    def execute(self, api_client: Api, config: dict, logger: logging.Logger) -> None:
        """
        Execute the strategy.

        This method is called periodically to process new market data and make trading decisions.

        Args:
            api_client (Api): The API client for market interactions.
            config (dict): Configuration parameters for the strategy.
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
            get_market_price = api_client.get_market_price(self.market)
            print(get_market_price)
            candle = get_market_price[0]
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
        candles = api_client.get_price_history(self.market, resolution="1m", sort="asc", limit=self.period*5)
        for candle in candles[:-1]:
            self.logger.info("--------------------------------------------------------------------------------")
            self.process_candle(candle)
            time.sleep(1)
        self.logger.info(" > [OK] Initialized.")
        self.logger.info("========================================================================")
        self.initialized = True
        self.last_candle = None
