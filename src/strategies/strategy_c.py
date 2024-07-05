from api import Api
from src.utils.candlestick_price_chart import CandlestickPriceChart
from src.web_scrapers.genius_yield_api import GeniusYieldAPI


# pylint: disable=invalid-name
class strategy_c:

    # pylint: disable=unused-argument
    def __init__(self, api_client, config, logger):
        logger.info(" > init: strategy_c instance created.")

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

        # Internal state:
        self.first_execution_time = None
        self.logger = logger

        # Strategy Configuration:
        self.asset_pair = config["ASSET_PAIR"]
        self.start_time = config["START_TIME"]
        self.end_time = config["END_TIME"]
        self.bin_interval = config["BIN_INTERVAL"]

    # pylint: disable=unused-argument
    def execute(self, api_client : Api, config, logger):
        api = GeniusYieldAPI(self.asset_pair, self.start_time, self.end_time, self.bin_interval)

        data = api.fetch_data()

        if data:
            parsed_data = api.parse_data(data)
            candlestickPriceChart = CandlestickPriceChart(parsed_data)
            candlestickPriceChart.plot()
        else:
            self.logger.info("🤔")
