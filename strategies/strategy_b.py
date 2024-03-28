from datetime import datetime, timedelta

class strategy_b:
    def __init__(self, client, CONFIG, logger):
        self.first_execution_time = None
        self.client = client
        self.CONFIG = CONFIG
        self.logger = logger
        print("Strategy B instance created")

    def execute(self, client, CONFIG, logger):
        current_time = datetime.now()
        if self.first_execution_time is None:
            self.first_execution_time = current_time

        # Calculate the time difference in seconds
        time_since_first_execution = (current_time - self.first_execution_time).total_seconds()

        # Toggle behavior every 30 seconds
        if int(time_since_first_execution // 30) % 2 == 0:
            self.behavior_a()
        else:
            self.behavior_b()

    def behavior_a(self):
        self.logger.info("Executing Strategy B: Behavior A 🍎")

    def behavior_b(self):
        self.logger.info("Executing Strategy B: Behavior B 🍌")
