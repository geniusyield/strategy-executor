import logging
import math
from typing import Any, Dict, List

from api import Api, ApiException


class MarketMaker:
    """
    Handle buy and sell orders for a specific market.

    This class provides methods to place, cancel, and retrieve buy and sell orders
    for a given market using the provided API client.

    Attributes:
        api_client (Api): The API client for market interactions.
        logger (logging.Logger): Logger for outputting information and errors.
        position_size (float): The maximum size of a position in the base asset.
        base_asset (str): The base asset of the market.
        target_asset (str): The target asset of the market.
        market (str): The market identifier (e.g., "BASE_TARGET").
    """

    def __init__(self, api_client: Api, config: Dict[str, str], logger: logging.Logger):
        """
        Initialize the MarketMaker.

        Args:
            api_client (Api): The API client for market interactions.
            config (Dict[str, str]): Configuration parameters for the market maker.
            logger (logging.Logger): Logger for outputting information and errors.
        """
        self.api_client = api_client
        self.logger = logger

        self.position_size = float(config["POSITION_SIZE_LOVELACES"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"

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
                self.logger.error(f" > ⚠️ [FAILED] could not cancel order: {order.output_reference} ⚠️")
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
