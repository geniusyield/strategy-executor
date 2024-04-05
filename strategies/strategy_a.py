from datetime import datetime

class strategy_a:
    def __init__(self, api_client, CONFIG, logger):
        self.start_time = datetime.now()
        self.counter = 0
        self.last_execution_time = None
        self.last_order_ref=None
        logger.info(" > init: strategy_a instance created.")

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
