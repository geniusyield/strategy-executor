from datetime import datetime

class strategy_a:
    def __init__(self, client, CONFIG, logger):
        self.start_time = datetime.now()
        self.counter = 0
        self.last_execution_time = None
        print("Strategy A instance created")

    def execute(self, client, CONFIG, logger):
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

        api_response = client["settings"].v0_settings_get()

        logger.info(f"Version: {api_response.version}")
        logger.info(f"setting_1: {CONFIG['setting_1']}")
        logger.info(f"setting_2: {CONFIG['setting_2']}")