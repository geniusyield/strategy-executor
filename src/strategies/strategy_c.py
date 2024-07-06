from api import Api
from src.data_extraction.genius_yield_api_scraper import GeniusYieldAPIScraper
from src.models.candlestick_price_chart import CandlestickPriceChart
from src.utils.logger_utils import LoggerUtils
from src.views.candlestick_price_chart_view import CandlestickPriceChartView


# pylint: disable=invalid-name
class strategy_c:

    # pylint: disable=unused-argument
    def __init__(self, api_client, config, logger):
        logger.info(" > init: strategy_c instance created.")
        LoggerUtils.log_warning(logger)

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
        api = GeniusYieldAPIScraper(self.asset_pair, self.start_time, self.end_time, self.bin_interval)

        data = api.fetch_data()

        if data:
            parsed_data = api.parse_data(data)
            candlestickPriceChart = CandlestickPriceChart(parsed_data)
            view = CandlestickPriceChartView(candlestickPriceChart)
            view.plot()
        else:
            self.logger.info("🤔")
