class Strategy_B():
    def execute(client, CONFIG):
        print("Executing Strategy B")
        api_response = client["settings"].v0_settings_get()
        print(f"Backend: api_response.backend")
        print(f"setting_1: {CONFIG['setting_1']}")
        print(f"setting_2: {CONFIG['setting_2']}")
