import logging
import math
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from talipp.indicators import BB, RSI

from api import Api, ApiException


# pylint: disable=invalid-name
class simple_rsi_bollinger_strategy:
    """
    A trading strategy combining RSI and Bollinger Bands.

    This class implements a trading strategy that uses RSI and Bollinger Bands indicators
    to make buy and sell decisions in a given market.

    Attributes:
        api_client (Api): The API client for market interactions.
        logger (logging.Logger): Logger for outputting information and errors.
        rsi (RSI): RSI indicator instance.
        bb (BB): Bollinger Bands indicator instance.
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

        self.api_client = api_client
        self.logger = logger
        self.initialized = False
        self.last_candle: Optional[Any] = None
        self.last_execution_time: Optional[datetime] = None

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

    def _initialize_indicators(self, config: Dict[str, any]) -> None:
        """Initialize strategy indicators and components."""
        self.rsi = RSI(self.rsi_period)
        self.bb = BB(self.bb_period, self.bb_std_dev)

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
            "BB_PERIOD", "BB_STD_DEV", "BASE_ASSET", "TARGET_ASSET"
        ]

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required configuration field: {field}")

        # Validate types and ranges
        try:
            assert float(config["POSITION_SIZE_LOVELACES"]) > 0, \
                "POSITION_SIZE_LOVELACES must be positive"
            assert 2 <= int(config["RSI_PERIOD"]) <= 100, "RSI_PERIOD must be between 2 and 100"
            assert 50 <= float(config["RSI_OVERBOUGHT"]) <= 100, \
                "RSI_OVERBOUGHT must be between 50 and 100"
            assert 0 <= float(config["RSI_OVERSOLD"]) <= 50, "RSI_OVERSOLD must be between 0 and 50"
            assert 2 <= int(config["BB_PERIOD"]) <= 100, "BB_PERIOD must be between 2 and 100"
            assert 0 < float(config["BB_STD_DEV"]) <= 5, "BB_STD_DEV must be between 0 and 5"
            assert isinstance(config["BASE_ASSET"], str) and config["BASE_ASSET"].strip(), \
                "BASE_ASSET should be a non-empty string"
            assert isinstance(config["TARGET_ASSET"], str) and config["TARGET_ASSET"].strip(), \
                "TARGET_ASSET should be a non-empty string"
        except ValueError as e:
            raise ValueError(f"Invalid configuration value: {str(e)}") from e
        except AssertionError as e:
            raise ValueError(f"Configuration validation failed: {str(e)}") from e

    def process_candle(self, candle) -> None:
        """
        Process a new candle and make trading decisions.

        Args:
            candle (Candle): The new candle to process.
        """
        if self.initialized:
            self.logger.info(
                f" > processing candle - timestamp: {candle.timestamp} \
                    - base_close: {candle.base_close}"
            )
        else:
            self.logger.info(
                f" > processing init candle - timestamp: {candle.timestamp} \
                    - base_close: {candle.base_close}"
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

        self.logger.info(f" RSI: {current_rsi:.2f}")
        self.logger.info(f" BB: Lower {current_bb.lb:.2f}, \
                         Middle {middle_band:.2f}, Upper {current_bb.ub:.2f}")

    def _execute_trading_logic(self, value: float) -> None:
        """Execute the trading logic based on indicator values."""
        current_rsi = self.rsi[-1]
        current_bb = self.bb[-1]

        buy_signal = (current_rsi < self.rsi_oversold and value <= current_bb.lb)
        sell_signal = (current_rsi > self.rsi_overbought and value >= current_bb.ub)

        if buy_signal:
            self._handle_buy_signal()
        elif sell_signal:
            self._handle_sell_signal()
        else:
            self.logger.info(" -> No clear signal or conflicting indicators. Holding position.")

        self.log_orders()

    def _handle_buy_signal(self) -> None:
        """Handle a buy signal."""
        self.logger.info(" -> Strong BUY signal: RSI oversold, price below lower BB")
        self.cancel_sell_orders()
        if not self.get_buy_orders():
            self.place_buy_order(self.last_candle.base_close)
        else:
            self.logger.info(" > Already placed BUY order. Nothing to do.")

    def _handle_sell_signal(self) -> None:
        """Handle a sell signal."""
        self.logger.info(" -> Strong SELL signal: RSI overbought, price above upper BB")
        self.cancel_buy_orders()
        if not self.get_sell_orders():
            self.place_sell_order(self.last_candle.base_close)
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
            self.logger.info(
                "--------------------------------------------------------------------------------"
            )
            self.process_candle(candle)
            time.sleep(1)
        self.logger.info(" > [OK] Initialized.")
        self.logger.info("========================================================================")
        self.initialized = True
        self.last_candle = None

    def place_buy_order(self, price: float) -> None:
        """
        Place a buy order at the specified price.

        Args:
            price (float): The price at which to place the buy order.
        """
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

            self.logger.info(f" > Place BUY order: {offered_amount} at price {price}...")
            response = self.api_client.place_order(
                offered_amount=f"{offered_amount}",
                offered_token=self.base_asset,
                price_token=self.target_asset,
                price_amount=f"{int(math.floor(offered_amount / price))}"
            )
            self.logger.info(f" > [OK] PLACED NEW BUY ORDER: {response.order_ref}")
        # pylint: disable=broad-exception-caught
        except Exception as e:
            self.logger.error(f" > ⚠️ [FAILED] Could not place BUY order: {str(e)} ⚠️")
            self.logger.exception(" > Exception details: ")

    def place_sell_order(self, price: float) -> None:
        """
        Place a sell order at the specified price.

        Args:
            price (float): The price at which to place the sell order.
        """
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
        # pylint: disable=broad-exception-caught
        except Exception as e:
            self.logger.error(f" > ⚠️ [FAILED] Could not place SELL order: {str(e)} ⚠️")
            self.logger.exception(" > Exception details: ")

    def get_buy_orders(self) -> List[Any]:
        """
        Get all active buy orders for the current market.

        Returns:
            List[Any]: A list of active buy orders.
        """
        own_orders = self.api_client.get_own_orders(self.market)
        return own_orders.bids

    def get_sell_orders(self) -> List[Any]:
        """
        Get all active sell orders for the current market.

        Returns:
            List[Any]: A list of active sell orders.
        """
        own_orders = self.api_client.get_own_orders(self.market)
        return own_orders.asks

    def cancel_buy_orders(self) -> None:
        """Cancel all active buy orders for the current market."""
        self.logger.info(" > Cancel all BUY orders...")
        self.cancel_orders("bid")
        self.logger.info(" > [OK] Canceled all BUY orders.")

    def cancel_sell_orders(self) -> None:
        """Cancel all active sell orders for the current market."""
        self.logger.info(" > Cancel all SELL orders...")
        self.cancel_orders("ask")
        self.logger.info(" > [OK] Canceled all SELL orders.")

    def cancel_orders(self, side: str) -> None:
        """
        Cancel all orders of a specific side (buy or sell).

        Args:
            side (str): The side of orders to cancel ("ask" for sell, "bid" for buy).
        """
        while True:
            orders = self.get_sell_orders() if side == "ask" else self.get_buy_orders()

            if not orders:
                return

            self.logger.info(f" Remaining {side} orders: {len(orders)}.")

            order = orders[0]
            try:
                self.logger.info(f" ⚙️ Canceling order: {order.output_reference}")
                self.api_client.cancel_order(order.output_reference)
                self.logger.info(f" > [OK] Canceled order: {order.output_reference}")
            except ApiException as e:
                self.logger.error(
                    f" > ⚠️ [FAILED] could not cancel order: {order.output_reference} ⚠️"
                )
                self.logger.exception(f" > Exception: {str(e)}")

    def log_orders(self) -> None:
        """Log all active orders for the current market."""
        own_orders = self.api_client.get_own_orders(self.market)

        self.logger.info(" ON-CHAIN ORDERS:")

        if not own_orders.asks and not own_orders.bids:
            self.logger.info(" > No orders.")
            return

        for sell_order in own_orders.asks:
            self.logger.info(f" > SELL: {sell_order.output_reference}")

        for buy_order in own_orders.bids:
            self.logger.info(f" > BUY: {buy_order.output_reference}")