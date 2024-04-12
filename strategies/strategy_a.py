from datetime import datetime
import math
from api import ApiException

def render_cardano_asset_name_with_policy(policy_asset_string):
    if 'lovelace' in policy_asset_string.lower():
        return "ADA"
    
    # Split the input string by the period to separate the policy ID and the asset name
    parts = policy_asset_string.split('.')
    if len(parts) != 2:
        return "Invalid input format. Expected format: <policy_id>.<asset_name>"
    
    # Extract the asset name part
    hex_asset_name = parts[1]
    
    try:
        # Attempt to decode from hexadecimal to bytes, then decode bytes to a UTF-8 string
        readable_string = bytes.fromhex(hex_asset_name).decode('utf-8')
    except UnicodeDecodeError:
        # If bytes cannot be decoded to UTF-8, return the original hexadecimal
        readable_string = f"Non-UTF-8 data: {hex_asset_name}"
    except ValueError:
        # In case of a ValueError, the input was not valid hexadecimal
        readable_string = f"Invalid hexadecimal: {hex_asset_name}"
    
    return readable_string

class strategy_a:
    def __init__(self, api_client, CONFIG, logger):
        self.start_time = datetime.now()
        self.counter = 0
        self.last_execution_time = None
        self.last_order_ref=None
        logger.info(" > init: strategy_a instance created.")
        
        logger.info("==============================================")
        logger.info("                   SETTINGS                   ")
        logger.info("==============================================")
        logger.info("Settings: ")
        try:
            settings = api_client.get_settings()
            logger.info(f" > Version: {settings.version}")
            logger.info(f" > Backend: {settings.backend}")
            logger.info(f" > Revision: {settings.revision}")
            logger.info(f" > Address: {settings.address}")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")

        logger.info("==============================================")
        logger.info("                     MARKETS                  ")
        logger.info("==============================================")
        logger.info("Markets: ")
        try:
            markets = api_client.get_markets()
            for market in markets:
                logger.info(f" > Market: {render_cardano_asset_name_with_policy(market.base_asset)} / {render_cardano_asset_name_with_policy(market.target_asset)}")
                logger.debug(f" > {market.market_id}")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")
        
        logger.info("==============================================")
        logger.info("             tGENS ASSET DETAILS              ")
        logger.info("==============================================")
        tGENS="c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53"
        try:
            tgens_asset = api_client.get_asset(tGENS)
            logger.info(f" Asset Details - tGENS:")
            logger.info(f" > Ticker: {tgens_asset.asset_ticker}")
            logger.info(f" > Decimals: {tgens_asset.asset_decimals}")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")
        
        logger.info("==============================================")
        logger.info("                 WALLET BALANCE               ")
        logger.info("==============================================")
        try:
            balances = api_client.get_balances()
            logger.info(f" Balances:")
            logger.info(f" > Balances: {balances}")
            logger.info(f" > ADA balance: {math.floor(balances.get('lovelace', 0) / 1_000_000)} ₳")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")
        
        logger.info("==============================================")
        logger.info("              TRADING FEES                    ")
        logger.info("==============================================")
        try:
            fees = api_client.get_trading_fees()
            logger.info(f" Trading Fees:")
            logger.info(f" > Maker Fee: {int(fees.flat_maker_fee) / 1_000_000 } ₳ + {fees.percentage_maker_fee}%")
            logger.info(f" > Taker Fee: {int(fees.flat_taker_fee) / 1_000_000 } ₳ + {fees.percentage_taker_fee}%")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")
            
        logger.info("==============================================")
        gens_ada_market_id="lovelace_c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53"
        try:
            order_book_response = api_client.get_order_book(gens_ada_market_id)
            logger.info(f" ADA/GENS Order Book:")
            
            logger.info(f" > ASKS:")
            for order in order_book_response.asks:
                logger.info(f" > ask > Amount: {order.offer_amount}, Price: {order.price}")

            logger.info(f" > BIDS:")
            for order in order_book_response.bids:
                logger.info(f" > bid > Amount: {order.offer_amount}, Price: {order.price}")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")
        
        logger.info("==============================================")
        logger.info("                 OWN ORDERS                   ")
        logger.info("==============================================")
        market_id="lovelace_c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53"
        
        try:
            response = api_client.get_own_orders(gens_ada_market_id)
            logger.info(f" Own orders:")
            
            for order in response.asks:
                logger.info(f" > ask > Amount: {order.offer_amount}, Price: {order.price}")

            for order in response.bids:
                logger.info(f" > bid > Amount: {order.offer_amount}, Price: {order.price}")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")
        
        logger.info("==============================================")
        logger.info("              GENS PRICE HISTORY              ")
        logger.info("==============================================")
        tgens_market_id="lovelace_c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53"
        gens_market_id="lovelace_dda5fdb1002f7389b33e036b6afee82a8189becb6cba852e8b79b4fb.0014df1047454e53"
        
        try:
            response = api_client.get_price_history(tgens_market_id, "1h", "2024-01-01", "2024-01-02")
            for candle in response:
                logger.info(f" > Closing price: {candle.base_close}")
        except ApiException as e:
            logger.exception(f"ApiException: HTTP {e.status_code}: {e.response}")

    def execute(self, api_client, CONFIG, logger):
        current_time = datetime.now()

        if self.last_execution_time is None:
            logger.info("Executing Strategy A for the first time")
        else:
            time_since_last_execution = (current_time - self.last_execution_time).total_seconds()
            logger.info(f"Last executed: {self.last_execution_time}")
            logger.info(f"Seconds since last execution: {time_since_last_execution} seconds")

        self.last_execution_time = current_time  # Update last execution time

        logger.info(f"Strategy A instantiated at: {self.start_time}")
        self.counter += 1
        logger.info(f" > Counter: {self.counter}")

        if self.last_order_ref == None:
            # No order was placed -> place order.
            logger.info(f" > PLACING ORDER....")
            try: 
                response = api_client.place_order(
                         offered_amount="1",
                         offered_token="lovelace",
                         price_token="c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53",
                         price_amount="1"
                )
                logger.info(f" > [OK] PLACED NEW ORDER")
                logger.info(f"order_ref: {response.order_ref}")
                self.last_order_ref = response.order_ref
            except:
                logger.exception(f" > [FAILED] could not place order. ❌")
            
        else:
            # An order has already been placed -> cancel it.
            ref = self.last_order_ref
            shortened_ref = f"{ref[:8]}...{ref[-8:]}" if len(ref) > 16 else ref
            logger.info(f" > CANCELING {shortened_ref}")
            try: 
                response = api_client.cancel_order(order_reference=self.last_order_ref)
                logger.info(f" > [OK] cancelled: {shortened_ref}")
            except:
                logger.exception(f" > [FAILED] could not cancel: {shortened_ref} ❌")
            
            # Reset the reference, so we place a new order.
            self.last_order_ref=None
        
        logger.info(f" > DONE.")
