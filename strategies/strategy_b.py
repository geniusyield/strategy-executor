class strategy_b():
    def execute(client, CONFIG, logger):
        logger.info("Executing Strategy B")
        api_response = client["settings"].v0_settings_get()
        logger.info(f"Backend: {api_response.backend}")
        logger.info(f"setting_1: {CONFIG['setting_1']}")
        logger.info(f"setting_2: {CONFIG['setting_2']}")
