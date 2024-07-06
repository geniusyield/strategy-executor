import logging
from typing import Dict, Optional

from api import Api
from src.data_extraction.fear_and_greed_index_web_scraper import (
    FearAndGreedIndexWebScraper,
)
from src.models.candlestick import Candlestick
from src.utils.logger_utils import LoggerUtils
from src.utils.market_maker import MarketMaker


# pylint: disable=invalid-name
class fear_and_greed_index_strategy:
    """
    A trading strategy based on the Fear and Greed Index.

    This class implements a trading strategy that uses the Fear and Greed Index
    to make buy and sell decisions in a given market.

    Attributes:
        api_client (Api): The API client for market interactions.
        logger (logging.Logger): Logger for outputting information and errors.
        market_maker (MarketMaker): Handles order placement and management.
        fgis (FearGreedIndexScraper): Scraper for the Fear and Greed Index.
    """

    def __init__(self, api_client: Api, config: Dict[str, any], logger: logging.Logger):
        """
        Initialize the Fear and Greed Index strategy.

        Args:
            api_client (Api): The API client for market interactions.
            config (Dict[str, any]): Configuration parameters for the strategy.
            logger (logging.Logger): Logger for outputting information and errors.
        """
        logger.info(" > init: fear_and_greed_index_strategy instance created.")
        LoggerUtils.log_warning(logger)

        self.api_client = api_client
        self.logger = logger

        self._initialize_strategy_parameters(config)
        self._log_strategy_configuration()

        self.market_maker = MarketMaker(api_client, config, logger)
        self.fgis = FearAndGreedIndexWebScraper(self.logger)

    def _initialize_strategy_parameters(self, config: Dict[str, any]) -> None:
        """Initialize strategy parameters from the configuration."""
        self.fear_and_greed_index_threshold = int(config["FEAR_AND_GREED_INDEX_THRESHOLD"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"

    def _log_strategy_configuration(self) -> None:
        """Log the strategy configuration."""
        self.logger.info(" STRATEGY CONFIGURATION:")
        self.logger.info(f" > base_asset : {self.base_asset}")
        self.logger.info(f" > target_asset : {self.target_asset}")
        self.logger.info(f" > market : {self.market}")
        self.logger.info(f" > fear_greed_threshold: {self.fear_and_greed_index_threshold}")

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
        try:
            self.logger.info("Executing Strategy...")
            index_value = self.fgis.get_index_value()
            if index_value:
                self._process_index_value(index_value)
            else:
                self.logger.info('Failed to retrieve the Fear and Greed Index.')
        # pylint: disable=broad-exception-caught
        except Exception as e:
            self.logger.error(" > ⚠️ [FAILED] could not process market data ⚠️")
            self.logger.exception(f" > Exception: {str(e)}")

    def _process_index_value(self, index_value: int) -> None:
        """
        Process the Fear and Greed Index value and make trading decisions.

        Args:
            index_value (int): The current Fear and Greed Index value.
        """
        market_price = self._get_market_price()
        if market_price is None:
            return

        if index_value > self.fear_and_greed_index_threshold:
            self._handle_greed_signal(market_price)
        else:
            self._handle_fear_signal(market_price)

        self.market_maker.log_orders()

    def _get_market_price(self) -> Optional[Candlestick]:
        """
        Get the current market price.

        Returns:
            Optional[Candle]: The current market price as a Candle object, or None if retrieval fails.
        """
        try:
            return self.api_client.get_market_price(self.market)[0]
        # pylint: disable=broad-exception-caught
        except Exception as e:
            self.logger.error(f"Failed to retrieve market price: {str(e)}")
            return None

    def _handle_greed_signal(self, market_price: Candlestick) -> None:
        """
        Handle a greed signal (buy altcoins).

        Args:
            market_price (Candle): The current market price.
        """
        self.logger.info(" -> Greed? -> BUY ALTCOINS !  🛒 🛒 🛒 ")
        self.market_maker.cancel_sell_orders()
        if self.market_maker.get_buy_orders():
            self.logger.info(" > Already placed BUY order. Nothing to do.")
        else:
            self.market_maker.place_buy_order(market_price.base_close)

    def _handle_fear_signal(self, market_price: Candlestick) -> None:
        """
        Handle a fear signal (sell altcoins).

        Args:
            market_price (Candle): The current market price.
        """
        self.logger.info(" -> Fear? -> SELL ALTCOINS!  💲 💲 💲 ")
        self.market_maker.cancel_buy_orders()
        if self.market_maker.get_sell_orders():
            self.logger.info(" > Already placed SELL order. Nothing to do.")
        else:
            self.market_maker.place_sell_order(market_price.base_close)
