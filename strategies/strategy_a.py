from datetime import datetime
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
    except ValueError:
        # In case of a ValueError, the input was not valid hexadecimal
        readable_string = f"Invalid hexadecimal: {hex_asset_name}"
    except UnicodeDecodeError:
        # If bytes cannot be decoded to UTF-8, return the original hexadecimal
        readable_string = f"Non-UTF-8 data: {hex_asset_name}"
    
    return readable_string

class strategy_a:
    def __init__(self, api_client, CONFIG, logger):
        self.start_time = datetime.now()
        self.counter = 0
        self.last_execution_time = None
        self.last_order_ref=None
        logger.info(" > init: strategy_a instance created.")
        response = api_client.get_settings()
        
        logger.info("==============================================")
        logger.info("Settings: ")
        if response.status_code == 200:
            settings = response.parsed
            logger.info(f" > Version: {settings.version}")
            logger.info(f" > Backend: {settings.backend}")
            logger.info(f" > Revision: {settings.revision}")
            logger.info(f" > Address: {settings.address}")
        else:
            logger.info(f" [FAILURE] Could not load settings. (HTTP {response.status_code})")

        logger.info("==============================================")
        response = api_client.get_markets()
        logger.info("Markets: ")
        if response.status_code == 200:
            settings = response.parsed
            for market in response.parsed:
                logger.info(f" > Market: {render_cardano_asset_name_with_policy(market.base_asset)} / {render_cardano_asset_name_with_policy(market.target_asset)}")
        else:
            logger.info(f" [FAILURE] Could not load markets. (HTTP {response.status_code})")
        
        logger.info("==============================================")
        tGENS="c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53"
        response = api_client.get_asset(tGENS)
        if response.status_code == 200:
            tgens_asset = response.parsed
            logger.info(f" Asset Details - tGENS:")
            logger.info(f" > Ticker: {tgens_asset.asset_ticker}")
            logger.info(f" > Decimals: {tgens_asset.asset_decimals}")
        else:
            logger.info(f" [FAILURE] Could not load asset details. (HTTP {response.status_code})")
        


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
            response = api_client.place_order(
                         offered_amount="1",
                         offered_token="lovelace",
                         price_token="66a524d7f34d954a3ad30b4e2d08023c950dfcd53bbe3c2314995da6.744d454c44",
                         price_amount="1"
            )
            logger.info(f" > RESPONSE STATUS CODE: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"order_ref: {response.parsed.order_ref}")
                self.last_order_ref=response.parsed.order_ref
            
        else:
            # An order has already been placed -> cancel it.
            ref = self.last_order_ref
            shortened_ref = f"{ref[:8]}...{ref[-8:]}" if len(ref) > 16 else ref
            logger.info(f" > CANCELING {shortened_ref}")
            response = api_client.cancel_order(order_reference=self.last_order_ref)
            logger.info(f" > RESPONSE STATUS CODE: {response.status_code}")
            if response.status_code == 200:
                logger.info(f" > [OK] cancelled: {shortened_ref}")
            else:
                logger.info(f" > [FAILED] could not cancel: {shortened_ref} ❌")
            
            # Reset the reference, so we place a new order.
            self.last_order_ref=None
        
        logger.info(f" > DONE.")
