class strategy_a():
    def execute(client, CONFIG, logger):
        logger.info("Executing Strategy A")
        api_response = client["settings"].v0_settings_get()
        logger.info(f"Version: {api_response.version}")
        logger.info(f"setting_1: {CONFIG['setting_1']}")
        logger.info(f"setting_2: {CONFIG['setting_2']}")
