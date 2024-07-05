
from api import Api
from src.utils.market_maker import MarketMaker
from src.web_scrapers.fear_greed_index_scraper import FearGreedIndexScraper


# pylint: disable=invalid-name
class fear_and_greed_index_strategy:
    def __init__(self, api_client, config, logger):
        logger.info(" > init: fear_and_greed_index_strategy instance created.")

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

        # # Internal state:
        self.api_client = api_client
        self.logger = logger

        # Strategy Configuration:
        self.fear_and_greed_index_threshold = int(config["FEAR_AND_GREED_INDEX_THRESHOLD"])
        self.base_asset = config["BASE_ASSET"]
        self.target_asset = config["TARGET_ASSET"]
        self.market = f"{self.base_asset}_{self.target_asset}"

        self.market_maker = MarketMaker(api_client, config, logger)

        self.fgis = FearGreedIndexScraper(self.logger)

    # pylint: disable=unused-argument
    def execute(self, api_client : Api, config, logger):
        try:
            self.logger.info("Executing Strategy...")
            index_value = self.fgis.get_index_value()
            if index_value:
                # pylint: disable=line-too-long
                get_market_price = self.api_client.get_market_price(self.market)[0]

                if index_value > self.fear_and_greed_index_threshold:
                    self.logger.info(" -> Greed? -> BUY ALTCOINS !  🛒 🛒 🛒 ")
                    self.market_maker.cancel_sell_orders()
                    if len(self.market_maker.get_buy_orders()) > 0:
                        self.logger.info(" > Already placed BUY order. Nothing to do.")
                    else:
                        self.market_maker.place_buy_order(get_market_price.base_close)
                else:
                    self.logger.info(" -> Fear? -> SELL ALTCOINS!  💲 💲 💲 ")
                    self.market_maker.cancel_buy_orders()
                    if len(self.market_maker.get_sell_orders()) > 0:
                        self.logger.info(" > Already placed SELL order. Nothing to do.")
                    else:
                        self.market_maker.place_sell_order(get_market_price.base_close)

                self.market_maker.log_orders()
            else:
                self.logger.info('Failed to retrieve the Fear and Greed Index.')
        # pylint: disable=bare-except
        except:
            self.logger.error(" > ⚠️ [FAILED] could not process candle ⚠️")
            self.logger.exception(" > Exception! ")
