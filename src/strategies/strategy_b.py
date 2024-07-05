from datetime import datetime


# pylint: disable=invalid-name
class strategy_b:
    def __init__(self, client, config, logger):
        self.first_execution_time = None
        self.client = client
        self.config = config
        self.logger = logger
        logger.info("Strategy B instance created")

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

    # pylint: disable=unused-argument
    def execute(self, client, config, logger):
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
