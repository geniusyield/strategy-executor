from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests


class GeniusYieldAPIScraper:
    """
    A class to interact with the GeniusYield API for fetching and parsing kline data.

    Attributes:
        base_url (str): The base URL for the GeniusYield API.
        asset_pair (str): The asset pair for which to fetch data.
        params (Dict[str, str]): Parameters for the API request.
    """

    base_url: str = "https://api.geniusyield.co"

    def __init__(self, asset_pair: str, start_time: str, end_time: str, bin_interval: str):
        """
        Initialize the GeniusYieldAPI instance.

        Args:
            asset_pair (str): The asset pair for which to fetch data.
            start_time (str): The start time for the data range.
            end_time (str): The end time for the data range.
            bin_interval (str): The interval for data binning.
        """
        self.asset_pair: str = asset_pair
        self.params: Dict[str, str] = {
            'startTime': start_time,
            'endTime': end_time,
            'binInterval': bin_interval
        }

    def fetch_data(self) -> Optional[List[Dict[str, str]]]:
        """
        Fetch kline data from the GeniusYield API.

        Returns:
            Optional[List[Dict[str, str]]]: A list of kline data points if successful, None otherwise.

        Raises:
            requests.exceptions.RequestException: If there's an error during the API request.
        """
        url: str = f"{self.base_url}/market/by-asset-pair/{self.asset_pair}/kline"
        try:
            response: requests.Response = requests.get(url, params=self.params, timeout=15)
            response.raise_for_status()  # Check if the request was successful
            data: Dict[str, List[Dict[str, str]]] = response.json()
            return data.get('data')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def parse_data(self, data: List[Dict[str, str]]) -> List[Dict[str, float]]:
        """
        Parse the kline data received from the API.

        Args:
            data (List[Dict[str, str]]): The raw kline data from the API.

        Returns:
            List[Dict[str, float]]: A list of parsed kline data points.
        """
        parsed_data: List[Dict[str, float]] = []
        for item in data:
            end_timestamp: str = item.get('time', '')
            timestamp_dt: datetime = datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            new_timestamp_dt: datetime = timestamp_dt + timedelta(days=1)
            new_timestamp_str: str = new_timestamp_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            kline: Dict[str, float] = {
                'start_timestamp': end_timestamp,
                'end_timestamp': new_timestamp_str,
                'open': float(item.get('open', 0)),
                'high': float(item.get('high', 0)),
                'low': float(item.get('low', 0)),
                'close': float(item.get('close', 0))
            }
            parsed_data.append(kline)
        return parsed_data

    def get_kline_data(self) -> Optional[List[Dict[str, float]]]:
        """
        Fetch and parse kline data from the GeniusYield API.

        Returns:
            Optional[List[Dict[str, float]]]: A list of parsed kline data points if successful, None otherwise.
        """
        raw_data: Optional[List[Dict[str, str]]] = self.fetch_data()
        if raw_data:
            return self.parse_data(raw_data)
        return None
