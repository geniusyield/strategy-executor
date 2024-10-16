import logging
import time
from datetime import datetime
from typing import Optional, Tuple, List
import os
import sys
from openai import OpenAI

from api import Api
from src.models.candlestick import Candlestick
from src.utils.logger_utils import LoggerUtils
from src.utils.market_maker import MarketMaker


# pylint: disable=invalid-name
class open_ai_strategy:
    """
    A trading strategy using ChatGPT for buy and sell decisions.

    This class implements a trading strategy that passes candlestick data to
    ChatGPT, asking for buy/sell decisions and at what price.

    Attributes:
        api_client (Api): The API client for market interactions.
        logger (logging.Logger): Logger for outputting information and errors.
        market_maker (MarketMaker): Handles order placement and management.
        initialized (bool): Whether the strategy has been initialized.
        last_candle (Optional[Candle]): The last processed candle.
        last_execution_time (Optional[datetime]): Timestamp of the last execution.
        candle_history (List[Candlestick]): A rolling buffer to store the last 100 candles.
    """

    def __init__(self, api_client: Api, config: dict, logger: logging.Logger):
        """
        Initialize the GPT-based strategy.

        Args:
            api_client (Api): The API client for market interactions.
            config (dict): Configuration parameters for the strategy.
            logger (logging.Logger): Logger for outputting information and errors.
        """
        logger.info(" > init: open_ai_strategy instance created.")
        LoggerUtils.log_warning(logger)

        self.api_client = api_client
        self.logger = logger
        self.initialized = False
        self.last_candle: Optional[Candlestick] = None
        self.last_execution_time: Optional[datetime] = None
        self.candle_history: List[Candlestick] = []  # Rolling buffer for the last 100 candles

        # Strategy Configuration
        self.position_size = float(config["POSITION_SIZE_LOVELACES"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"

        self.open_api_key = os.getenv("OPENAI_API_KEY")
        if self.open_api_key is None:
            sys.stderr.write("Error: The OPENAI_API_KEY environment variable is not set.\n")
            sys.exit(1)  # Exit with a non-zero status to indicate an error

        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        self._log_configuration()

        self.market_maker = MarketMaker(api_client, config, logger)

    def _log_configuration(self) -> None:
        """Log the strategy configuration."""
        self.logger.info(" STRATEGY CONFIGURATION:")
        self.logger.info(f" > base_asset         : {self.base_asset}")
        self.logger.info(f" > target_asset       : {self.target_asset}")
        self.logger.info(f" > market             : {self.market}")
        self.logger.info(f" > position_size      : {self.position_size}")

    def process_candle(self, candle: Candlestick) -> None:
        """
        Process a new candle and make trading decisions by asking ChatGPT.

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

        # Add the current candle to the rolling buffer and maintain the last 100 candles
        self.candle_history.append(candle)
        if len(self.candle_history) > 100:
            self.candle_history.pop(0)


        if not self.initialized:
            self.logger.info(" -> Initialization phase. Do not place orders yet.")
            return

        decision, price = self.ask_gpt_for_decision()

        self._execute_decision(decision, price)
        self.market_maker.log_orders()

    def ask_gpt_for_decision(self) -> Tuple[str, float]:
        """
        Query ChatGPT for a buy/sell decision based on the last 100 candles.

        Returns:
            Tuple[str, float]: The decision ("buy" or "sell") and the price at which to execute.
        """
        # Prepare the message to send to ChatGPT with the last 100 candles
        candle_data = "\n".join(
            [
                f"Timestamp: {candle.timestamp}, Open: {candle.base_open}, High: {candle.base_high}, "
                f"Low: {candle.base_low}, Close: {candle.base_close}"
                for candle in self.candle_history
            ]
        )

        prompt = (
            f"Based on the following candlestick data:\n{candle_data}\n\n"
            "Should I buy, hold, or sell? Please respond with BUY!, HOLD!, or SELL!, followed by a short reasoning."
        )

        try:
            # Call the OpenAI Completions API with the new interface in v1.5.1
            completion  = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a trading assistant helping with decision-making."},
                    {"role": "user", "content": prompt}
                ]
            )

            gpt_reply=completion.choices[0].message.content

            self.logger.info(f"GPT Response: {gpt_reply}")

            # Parse the response from GPT
            if "buy!" in gpt_reply.lower():
                return "buy", float(self.last_candle.base_close)
            elif "sell!" in gpt_reply.lower():
                return "sell", float(self.last_candle.base_close)
            else:
                return "hold!", float(self.last_candle.base_close)

        except Exception as e:
            self.logger.error(f"Error communicating with GPT: {str(e)}")
            return "hold!", float(self.last_candle.base_close)  # Default to hold if there's an error


    def _execute_decision(self, decision: str, price: float) -> None:
        """
        Execute the buy or sell decision based on GPT's suggestion.

        Args:
            decision (str): The decision ("buy" or "sell").
            price (float): The price at which to execute the decision.
        """
        if decision == "buy":
            self.logger.info(" -> ChatGPT suggests BUY! 🛒 🛒 🛒 ")
            self.market_maker.cancel_sell_orders()
            self.market_maker.cancel_buy_orders()
            self.market_maker.place_buy_order(price)
        elif decision == "sell":
            self.logger.info(" -> ChatGPT suggests SELL! 💲 💲 💲 ")
            self.market_maker.cancel_sell_orders()
            self.market_maker.cancel_buy_orders()
            self.market_maker.place_sell_order(price)

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
        candles = api_client.get_price_history(self.market, resolution="1d", sort="asc", limit=100)
        for candle in candles[:-1]:
            self.logger.info("--------------------------------------------------------------------------------")
            self.process_candle(candle)
            time.sleep(1)
        self.logger.info(" > [OK] Initialized.")
        self.logger.info("========================================================================")
        self.initialized = True
        self.last_candle = None
