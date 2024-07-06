from datetime import datetime
from typing import ClassVar, Dict, Optional


class Candlestick:
    """
    Represents a single candlestick in a financial chart.

    This class encapsulates the data for a candlestick, including timestamps,
    open, high, low, and close prices.

    Attributes:
        start_timestamp (str): The start time of the candlestick period.
        end_timestamp (str): The end time of the candlestick period.
        open (float): The opening price of the candlestick.
        high (float): The highest price during the candlestick period.
        low (float): The lowest price during the candlestick period.
        close (float): The closing price of the candlestick.
    """

    TIMESTAMP_FORMAT: ClassVar[str] = '%Y-%m-%dT%H:%M:%S.%fZ'
    REQUIRED_FIELDS: ClassVar[list] = ['start_timestamp', 'end_timestamp', 'open', 'high', 'low', 'close']

    def __init__(self, candlestick_data: Dict[str, float]):
        """
        Initialize a Candlestick instance.

        Args:
            candlestick_data (Dict[str, float]): A dictionary containing the candlestick data.

        Raises:
            ValueError: If the input data is invalid or missing required fields.
        """
        if not isinstance(candlestick_data, dict):
            raise ValueError("data must be a dictionary")

        for field in self.REQUIRED_FIELDS:
            if field not in candlestick_data:
                raise ValueError(f"Missing required field: {field}")

        self.start_timestamp: str = candlestick_data['start_timestamp']
        self.end_timestamp: str = candlestick_data['end_timestamp']
        self.open: float = candlestick_data['open']
        self.high: float = candlestick_data['high']
        self.low: float = candlestick_data['low']
        self.close: float = candlestick_data['close']

        self._validate_data()

    def _validate_data(self) -> None:
        """
        Validate the candlestick data.

        Raises:
            ValueError: If any of the data validations fail.
        """
        # Validate timestamps
        try:
            start_dt = datetime.strptime(self.start_timestamp, self.TIMESTAMP_FORMAT)
            end_dt = datetime.strptime(self.end_timestamp, self.TIMESTAMP_FORMAT)
        except ValueError as exc:
            raise ValueError(f"Timestamps must be in the format '{self.TIMESTAMP_FORMAT}'") from exc

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
    def create_if_valid(cls, cpc: Dict[str, float]) -> Optional['Candlestick']:
        """
        Create a Candlestick instance if the data is valid.

        Args:
            cpc (Dict[str, float]): A dictionary containing the candlestick data.

        Returns:
            Optional[Candlestick]: A Candlestick instance if the data is valid, None otherwise.
        """
        try:
            return cls(cpc)
        except ValueError:
            return None

    def get_duration(self) -> float:
        """
        Calculate the duration of the candlestick period.

        Returns:
            float: The duration in seconds.
        """
        start_dt = datetime.strptime(self.start_timestamp, self.TIMESTAMP_FORMAT)
        end_dt = datetime.strptime(self.end_timestamp, self.TIMESTAMP_FORMAT)
        return (end_dt - start_dt).total_seconds()

    def get_midpoint(self) -> float:
        """
        Calculate the midpoint price of the candlestick.

        Returns:
            float: The midpoint between the high and low prices.
        """
        return (self.high + self.low) / 2

    def is_bullish(self) -> bool:
        """
        Determine if the candlestick is bullish (closing price higher than opening price).

        Returns:
            bool: True if bullish, False otherwise.
        """
        return self.close > self.open

    def get_price_range(self) -> float:
        """
        Calculate the price range of the candlestick.

        Returns:
            float: The difference between the high and low prices.
        """
        return self.high - self.low

    def __repr__(self) -> str:
        """
        Return a string representation of the Candlestick.

        Returns:
            str: A string representation of the Candlestick instance.
        """
        return (f"Candlestick(start={self.start_timestamp}, end={self.end_timestamp}, "
                f"open={self.open}, high={self.high}, low={self.low}, close={self.close})")
