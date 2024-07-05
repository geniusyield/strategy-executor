from datetime import datetime
from typing import Dict


class Candlestick:
    def __init__(self, candlestick_data: Dict[str, float]):
        if not isinstance(candlestick_data, dict):
            raise ValueError("data must be a dictionary")

        self.start_timestamp = candlestick_data.get("start_timestamp")
        self.end_timestamp = candlestick_data.get("end_timestamp")
        self.open = candlestick_data.get("open")
        self.high = candlestick_data.get("high")
        self.low = candlestick_data.get("low")
        self.close = candlestick_data.get("close")

        self._validate_data()

    def _validate_data(self):
        # Validate timestamps
        try:
            start_dt = datetime.strptime(self.start_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            end_dt = datetime.strptime(self.end_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError as exc:
            raise ValueError("Timestamps must be in the format '%Y-%m-%dT%H:%M:%S.%fZ'") from exc

        # Ensure start_timestamp is less than end_timestamp
        if start_dt >= end_dt:
            raise ValueError("start_timestamp must be less than end_timestamp")

        # Validate that other attributes are numbers
        for attr in ["open", "high", "low", "close"]:
            value = getattr(self, attr)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{attr} must be a number")

        # Ensure open, close values are within the high and low range
        if not (self.low <= self.open <= self.high and self.low <= self.close <= self.high):
            raise ValueError("Invalid values for open, high, low, or close")

    @classmethod
    def create_if_valid(cls, cpc):
        try:
            instance = cls(cpc)
            return instance
        except ValueError:
            return None

    def get_duration(self) -> float:
        return self.end_timestamp - self.start_timestamp

    def get_midpoint(self) -> float:
        return (self.high + self.low) / 2
