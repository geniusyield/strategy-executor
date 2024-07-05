from datetime import datetime, timedelta

import requests


class GeniusYieldAPI:

    base_url = "https://api.geniusyield.co"

    def __init__(self, asset_pair, start_time, end_time, bin_interval):
        self.asset_pair = asset_pair
        self.params = {
            'startTime': start_time,
            'endTime': end_time,
            'binInterval': bin_interval
        }

    def fetch_data(self):
        url = f"{self.base_url}/market/by-asset-pair/{self.asset_pair}/kline"
        try:
            response = requests.get(url, params=self.params, timeout=15)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            return data.get('data')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def parse_data(self, data):
        # Assuming the data contains a list of kline data points
        parsed_data = []
        for item in data:
            end_timestamp = item.get('time')
            timestamp_dt = datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            new_timestamp_dt = timestamp_dt + timedelta(days=1)
            new_timestamp_str = new_timestamp_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            kline = {
                'start_timestamp': item.get('time'),
                'end_timestamp': new_timestamp_str,
                'open': float(item.get('open')),
                'high': float(item.get('high')),
                'low': float(item.get('low')),
                'close': float(item.get('close'))
            }
            parsed_data.append(kline)
        return parsed_data
