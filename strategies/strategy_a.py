class strategy_a():
    def execute(client, CONFIG):
        print("Executing Strategy A")
        api_response = client["settings"].v0_settings_get()
        print(f"Version: {api_response.version}")
        print(f"setting_1: {CONFIG['setting_1']}")
        print(f"setting_2: {CONFIG['setting_2']}")
