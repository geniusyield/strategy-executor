# type: ignore
from datetime import datetime
from api import Api, ApiException
from logging import Logger
import polars as pl
import math


class single_order_strategy:
    def __init__(self, client: Api, CONFIG: dict[str, str], logger: Logger):

        # Internal state:
        self.client = client
        self.logger = logger
        self.counter = 0
        self.start_time = datetime.now()
        self.last_execution_time = None

        self.nft_token = {
            "actual": {"buy": None, "sell": None},
            "hedge": {"buy": None, "sell": None},
        }

        self.price = {
            "actual": {"buy": 0, "sell": 0},
            "hedge": {"buy": 0, "sell": 0}
        }

        self.offer_amount = {"actual": {"buy": 0, "sell": 0}}

        self.deficit = {"hedge": {"buy": 0, "sell": 0}}
        self.surplus = {"hedge": {"buy": 0, "sell": 0}}
        self.total = {"hedge": {"buy": 0, "sell": 0}}
        self.std = 0

        # strategy configuration
        self.base_asset = CONFIG["BASE_ASSET"]
        self.target_asset = CONFIG["TARGET_ASSET"]
        self.market_id = f"{self.base_asset}_{self.target_asset}"
        self.base_amount = CONFIG["BASE_AMOUNT"]
        self.target_amount = CONFIG["TARGET_AMOUNT"]
        self.limit = int(CONFIG["LIMIT"])
        self.order_level = int(CONFIG["ORDER_LEVEL"])
        self.spread = float(CONFIG["SPREAD"])
        self.multiplier = float(CONFIG["MULTIPLIER"])
        self.actual_cancel_threshold = float(CONFIG["ACTUAL_CANCEL_THRESHOLD"])
        self.hedge_cancel_threshold = float(CONFIG["HEDGE_CANCEL_THRESHOLD"])
        self.std = float(CONFIG["STD"])

        logger.info(" STRATEGY CONFIGURATION:")
        logger.info(f" > base_asset         : {self.base_asset}")
        logger.info(f" > target_asset       : {self.target_asset}")
        logger.info(f" > market             : {self.market_id}")
        logger.info(f" > base_amount        : {self.base_amount}")
        logger.info(f" > target_amount      : {self.target_amount}")
        logger.info(f" > limit              : {self.limit}")
        logger.info(f" > order_level        : {self.order_level}")
        logger.info(f" > spread             : {self.spread}")
        logger.info(f" > multiplier         : {self.multiplier}")
        logger.info(f" > actual_cancel_threshold: {self.actual_cancel_threshold}")
        logger.info(f" > hedge_cancel_threshold : {self.hedge_cancel_threshold}")
        logger.info(f" > std          : {self.std}")

    def process_orders(
        self,
        client: Api,
        logger: Logger,
        market_price: float,
        order_type: str,
        side: str,
    ) -> None:
        # Process orders logic
        logger.info(f" > ✨ Processing NEW {order_type.upper()} {side.upper()} ORDER...")

        if order_type == "actual" and side == "buy":
            self.offer_amount[order_type][side] = int(self.base_amount)

            self.price[order_type][side] = market_price * (1 - self.std * self.multiplier)

            # carry over surplus hedge sell
            if self.total["hedge"]["sell"] < 0:
                self.offer_amount[order_type][side] += abs(int(math.floor(self.total["hedge"]["sell"]*self.price[order_type][side])))
                self.total["hedge"]["sell"] = 0
                self.deficit["hedge"]["sell"] = 0

            price_amount = int(math.floor(self.offer_amount[order_type][side] / self.price[order_type][side]))
            self.surplus["hedge"]["sell"] = price_amount

            logger.info(
                f" > 🛒 {order_type.upper()} {side.upper()} ORDER: {self.market_id} {side.upper()} {price_amount} @ {self.price[order_type][side]} "
            )

            self.place_orders(
                client=client,
                logger=logger,
                offer_amount=f"{self.offer_amount[order_type][side]}",
                offer_token=self.base_asset,
                price_token=self.target_asset,
                price_amount=f"{price_amount}",
                order_type="actual",
                side="buy"
            )

        if order_type == "actual" and side == "sell":
            self.offer_amount[order_type][side] = int(self.target_amount)

            self.price[order_type][side] = market_price * (1 + self.std * self.multiplier)

            # carry over surplus hedge buy
            if self.total["hedge"]["buy"] < 0:
                self.offer_amount[order_type][side] += int(abs(math.floor(self.total["hedge"]["buy"] / self.price[order_type][side])))
                self.total["hedge"]["buy"] = 0
                self.deficit["hedge"]["buy"] = 0

            price_amount = int(math.floor(self.offer_amount[order_type][side] * self.price[order_type][side]))
            self.surplus["hedge"]["buy"] = price_amount

            logger.info(
                f" > 💰 {order_type.upper()} {side.upper()} ORDER: {self.market_id} {side.upper()} {price_amount} @ {self.price[order_type][side]} "
            )

            self.place_orders(
                client=client,
                logger=logger,
                offer_amount=f"{self.offer_amount[order_type][side]}",
                offer_token=self.target_asset,
                price_token=self.base_asset,
                price_amount=f"{price_amount}",
                order_type="actual",
                side="sell"
            )

        if order_type == "hedge" and side == "buy":
            self.price[order_type][side] = self.price["actual"]["sell"]*(1 - self.spread)
            offer_amount = int(math.floor(self.offer_amount["actual"]["sell"] * self.price[order_type][side]))
            self.surplus["hedge"]["buy"] -= offer_amount

            logger.info(
                f" > 🛒 {order_type.upper()} {side.upper()} ORDER: {self.market_id} {side.upper()} {offer_amount} @ {self.price[order_type][side]} "
            )

            self.place_orders(
                client=client,
                logger=logger,
                offer_amount=f"{offer_amount}",
                offer_token=self.base_asset,
                price_token=self.target_asset,
                price_amount=f"{self.offer_amount['actual']['sell']}",
                order_type="hedge",
                side="buy"
            )

        if order_type == "hedge" and side == "sell":
            self.price[order_type][side] = self.price["actual"]["buy"]*(1 + self.spread)
            offer_amount = int(math.floor(self.offer_amount["actual"]["buy"] / self.price[order_type][side]))
            self.surplus["hedge"]["sell"] -= offer_amount

            logger.info(
                f" > 💰 {order_type.upper()} {side.upper()} ORDER: {self.market_id} {side.upper()} {offer_amount} @ {self.price[order_type][side]} "
            )

            self.place_orders(
                client=client,
                logger=logger,
                offer_amount=f"{offer_amount}",
                offer_token=self.target_asset,
                price_token=self.base_asset,
                price_amount=f"{self.offer_amount['actual']['buy']}",
                order_type="hedge",
                side="sell"
            )

    def place_orders(
        self,
        client: Api,
        logger: Logger,
        offer_amount: str,
        offer_token: str,
        price_token: str,
        price_amount: str,
        order_type: str,
        side: str,
    ) -> None:
        # Place orders logic
        logger.info(f" > ⚙️ Placing {order_type.upper()} {side.upper()} order...")
        try:
            order = client.place_order(
                offered_amount=offer_amount,
                offered_token=offer_token,
                price_token=price_token,
                price_amount=price_amount
            )

            self.nft_token[order_type][side] = order.nft_token
            logger.info(f" > ✅ [OK] Placed {order_type.upper()} {side.upper()} order: {order.order_ref}")
        except ApiException as e:
            logger.error(f" > ⚠️ [FAILED] Couldn't place {order_type.upper()} {side.upper()} order ⚠️")
            logger.exception(f" > ❌ API Exception: HTTP {e.status_code}: response={e.response}")

    def cancel_orders(
        self,
        client: Api,
        logger: Logger,
        side: str,
        order_type: str,
        nft_token: str,
        order_ref: str,
    ) -> None:

        # Cancel orders logic
        logger.info(f" > ⚙️ Canceling {order_type.upper()} {side.upper()} order")
        logger.info(f" > nft token: {nft_token} order reference: {order_ref}")
        try:
            client.cancel_order(order_reference=order_ref)
            logger.info(f" > ✅ [OK] Canceled {order_type.upper()} {side.upper()} nft token: {nft_token} order: {order_ref}")
            self.nft_token[order_type][side] = None
        except ApiException as e:
            logger.error(f" > ⚠️ [FAILED] Couldn't cancel {order_type.upper()} {side.upper()} order ⚠️")
            logger.exception(f" > ❌ API Exception: HTTP {e.status_code}: response={e.response}")

    def check_orders(
        self,
        client: Api,
        logger: Logger,
        market_price: float
    ) -> None:
        # Check if orders are yet to be place, open, partially-filled, filled or need to cancel
        own_orders = client.get_own_orders(self.market_id)

        for order in own_orders.bids:
            logger.info(f" > 🛒 BID > Amount: {order.offer_amount}, Price: {order.price}, output_ref: {order.output_reference}, nft_token: {order.nft_token}")

        for order in own_orders.asks:
            logger.info(f" > 💰 ASK > Amount: {order.offer_amount}, Price: {order.price}, output_ref: {order.output_reference}, nft_token: {order.nft_token}")

        asks_nft_tokens = [str(order.nft_token) for order in own_orders.asks]
        bids_nft_tokens = [str(order.nft_token) for order in own_orders.bids]

        if not asks_nft_tokens and not bids_nft_tokens and not self.nft_token["actual"]["sell"] and not self.nft_token["actual"]["buy"]:
            # place orders
            self.process_orders(
                client=client,
                logger=logger,
                market_price=market_price,
                order_type="actual",
                side="buy"
            )
            self.process_orders(
                client=client,
                logger=logger,
                market_price=market_price,
                order_type="actual",
                side="sell"
            )
            return

        ask_params = [(str(order.nft_token), str(order.output_reference), float(order.offer_amount)) for order in own_orders.asks]
        bid_params = [(str(order.nft_token), str(order.output_reference), float(order.offer_amount)) for order in own_orders.bids]


        if self.nft_token["actual"]["sell"] and self.nft_token["actual"]["sell"] not in asks_nft_tokens:
            # place hedge buy
            self.nft_token["actual"]["sell"] = None
            self.process_orders(
                client=client,
                logger=logger,
                market_price=market_price,
                order_type="hedge",
                side="buy"
            )

        if self.nft_token["actual"]["buy"] and self.nft_token["actual"]["buy"] not in bids_nft_tokens:
            # place hedge sell
            self.nft_token["actual"]["buy"] = None
            self.process_orders(
                client=client,
                logger=logger,
                market_price=market_price,
                order_type="hedge",
                side="sell"
            )

        for (nft_token, order_reference, offer_amount) in ask_params:
            if self.nft_token["actual"]["sell"] == nft_token:
                # actual sell order open - check for cancellation
                logger.info(f" > 💰 ACTUAL SELL order OPEN: {nft_token}")
                upper_bound = self.price["actual"]["sell"]*(1 + self.actual_cancel_threshold)
                lower_bound = self.price["actual"]["sell"]*(1 - self.actual_cancel_threshold)

                logger.info(f" > Upper: {upper_bound}, Current: {market_price}, Lower: {lower_bound}")

                if market_price > upper_bound or market_price < lower_bound:
                    # cancel actual sell order
                    self.cancel_orders(
                        client=client,
                        logger=logger,
                        side="sell",
                        order_type="actual",
                        nft_token=nft_token,
                        order_ref=order_reference
                    )
                else:
                    logger.info(f" > ⚙️ No need to cancel ACTUAL SELL order: {nft_token}")

            elif self.nft_token["hedge"]["sell"] == nft_token:
                # hedge sell order open - check for cancellation
                logger.info(f" > 💰 HEDGE SELL order OPEN: {nft_token}")
                upper_bound = self.price["hedge"]["sell"]*(1 + self.hedge_cancel_threshold)
                lower_bound = self.price["hedge"]["sell"]*(1 - self.hedge_cancel_threshold)

                logger.info(f" > Upper: {upper_bound}, Current: {market_price}, Lower: {lower_bound}")

                if market_price > upper_bound or market_price < lower_bound:
                    # cancel hedge sell order
                    self.deficit["hedge"]["sell"] = int(math.floor(offer_amount))
                    logger.info(f" > 📉 Deficit amount: {self.deficit['hedge']['sell']}")
                    logger.info(f" > 📈 Surplus amount: {self.surplus['hedge']['sell']}")
                    self.total["hedge"]["sell"] = self.surplus["hedge"]["sell"] - self.deficit["hedge"]["sell"]
                    self.cancel_orders(
                        client=client,
                        logger=logger,
                        side="sell",
                        order_type="hedge",
                        nft_token=nft_token,
                        order_ref=order_reference
                    )
                else:
                    logger.info(f" > ⚙️ No need to cancel HEDGE SELL order: {nft_token}")

        for (nft_token, order_reference, offer_amount) in bid_params:
            if self.nft_token["actual"]["buy"] == nft_token:
                # actual buy order open - check for cancellation
                logger.info(f" > 🛒 ACTUAL BUY order OPEN: {nft_token}")
                upper_bound = self.price["actual"]["buy"]*(1 + self.actual_cancel_threshold)
                lower_bound = self.price["actual"]["buy"]*(1 - self.actual_cancel_threshold)

                logger.info(f" > Upper: {upper_bound}, Current: {market_price}, Lower: {lower_bound}")

                if market_price > upper_bound or market_price < lower_bound:
                    # cancel actual buy order
                    self.cancel_orders(
                        client=client,
                        logger=logger,
                        side="buy",
                        order_type="actual",
                        nft_token=nft_token,
                        order_ref=order_reference
                    )
                else:
                    logger.info(f" > ⚙️ No need to cancel ACTUAL BUY order: {nft_token}")
            elif self.nft_token["hedge"]["buy"] == nft_token:
                # hedge buy order open - check for cancellation
                logger.info(f" > 🛒 HEDGE BUY order OPEN: {nft_token}")
                upper_bound = self.price["hedge"]["buy"]*(1 + self.hedge_cancel_threshold)
                lower_bound = self.price["hedge"]["buy"]*(1 - self.hedge_cancel_threshold)

                logger.info(f" > Upper: {upper_bound}, Current: {market_price}, Lower: {lower_bound}")

                if market_price > upper_bound or market_price < lower_bound:
                    # cancel hedge buy order
                    self.deficit["hedge"]["buy"] = int(math.floor(offer_amount)*self.price["hedge"]["buy"])
                    logger.info(f" > 📉 Deficit amount: {self.deficit['hedge']['buy']}")
                    logger.info(f" > 📈 Surplus amount: {self.surplus['hedge']['buy']}")

                    self.total["hedge"]["buy"] = self.surplus["hedge"]["buy"] - self.deficit["hedge"]["buy"]

                    self.cancel_orders(
                        client=client,
                        logger=logger,
                        side="buy",
                        order_type="hedge",
                        nft_token=nft_token,
                        order_ref=order_reference
                    )
                else:
                    logger.info(f" > ⚙️ No need to cancel HEDGE BUY order: {nft_token}")

    def execute(
        self,
        client: Api,
        CONFIG: dict[str, str],
        logger: Logger
    ) -> None:
        # Execution logic
        current_time = datetime.now()

        try:
            markets = client.get_markets()
            market_ids = [market.market_id for market in markets]
            if self.market_id not in market_ids:
                logger.info(f" > ❌ [INVALID] market id: {self.market_id}")
                return

        except ApiException as e:
            logger.error(f" > ⚠️ [FAILED] Couldn't get markets.")
            logger.exception(f" > ❌ API Exception: HTTP {e.status_code}: response={e.response}")

        try:
            get_market_price = client.get_market_price(self.market_id)
            if not (isinstance(get_market_price, list) and len(get_market_price) > 0):
                logger.info(f" > ⚠️ No market price found.")
                return
        except ApiException as e:
            logger.error(f" > ⚠️ [FAILED] Couldn't get market price.")
            logger.exception(f" > ❌ API Exception: HTTP {e.status_code}: response={e.response}")

        if self.last_execution_time is None:
            logger.info("Executing for the first time!")

            try:
                own_orders = client.get_own_orders(market_id=self.market_id)
                for order in own_orders.asks:
                    logger.info(f" > ⏳ Canceling EXISTING SELL order...")
                    self.cancel_orders(
                        client=client,
                        logger=logger,
                        order_type="actual",
                        side="sell",
                        nft_token=str(order.nft_token),
                        order_ref=str(order.output_reference)
                    )

                for order in own_orders.bids:
                    logger.info(f" > ⏳ Canceling EXISTING BUY order...")
                    self.cancel_orders(
                        client=client,
                        logger=logger,
                        order_type="actual",
                        side="buy",
                        nft_token=str(order.nft_token),
                        order_ref=str(order.output_reference)
                    )
            except ApiException as e:
                logger.error(f" > ⚠️ [FAILED] Couldn't fetch OWN orders")
                logger.exception(f" > ❌ API Exception: HTTP {e.status_code}: response={e.response}")

            market_price = float(get_market_price[0].base_close)
            logger.info(f" > Current Market Price: {market_price}")

            self.check_orders(client=client, logger=logger, market_price=market_price)
        else:
            time_since_last_execution = (current_time - self.last_execution_time).total_seconds()
            logger.info(f"Last executed: {self.last_execution_time}")
            logger.info(f"Seconds since last execution: {time_since_last_execution} seconds")

        self.last_execution_time = current_time  # Update last execution time
        self.initialized = True

        self.counter += 1
        logger.info(f" > Counter: {self.counter}")

        try:
            market_price = float(get_market_price[0].base_close)
            logger.info(f" > Current Market Price: {market_price}")
            self.check_orders(client=client, logger=logger, market_price=market_price)
            logger.info(
                f" > 📉 DEFICIT: 🛒 BUY: {self.deficit['hedge']['buy']} , 💰 SELL: {self.deficit['hedge']['sell']}"
            )
            logger.info(
                f" > 📈 SURPLUS: 🛒 BUY: {self.surplus['hedge']['buy']} , 💰 SELL: {self.surplus['hedge']['sell']}"
            )
            logger.info(
                f" > 📊 TOTAL: 🛒 BUY: {self.total['hedge']['buy']} , 💰 SELL: {self.total['hedge']['sell']}"
            )
        except:
            logger.error(f" > ⚠️ [FAILED] could not check orders ⚠️")
            logger.exception(f" > Exception!")

        logger.info(" > ✅ DONE ✅")