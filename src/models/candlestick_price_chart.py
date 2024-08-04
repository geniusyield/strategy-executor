from typing import Dict, List, Optional, Tuple

from src.models.candlestick import Candlestick


class CandlestickPriceChart:
    """
    A class representing a candlestick price chart.

    This class processes a list of candlestick price data and creates a chart
    of valid candlesticks.

    Attributes:
        candlesticks (List[Candlestick]): A list of valid Candlestick objects.
    """

    CHART_WIDTH_MULTIPLIER = 2
    CHART_WIDTH_OFFSET = 1

    def __init__(self, candlestick_price_chart_data: List[Dict[str, float]]):
        """
        Initialize the CandlestickPriceChart with the given price chart data.

        Args:
            candlestick_price_chart_data (List[Dict[str, float]]): A list of dictionaries
                containing candlestick price data.

        Raises:
            ValueError: If the input data is empty or invalid.
        """
        if not candlestick_price_chart_data:
            raise ValueError("Input data cannot be empty")

        self.candlesticks = [Candlestick.create_if_valid(cpc) for cpc in candlestick_price_chart_data]
        self.candlesticks = [cs for cs in self.candlesticks if cs is not None]

        if not self.candlesticks:
            raise ValueError("No valid candlesticks could be created from the input data")

    @property
    def chart_height(self) -> int:
        """
        Get the height of the chart.

        Returns:
            int: The number of candlesticks in the chart.
        """
        return len(self.candlesticks)

    @property
    def chart_width(self) -> int:
        """
        Get the width of the chart.

        Returns:
            int: The width of the chart, calculated as twice the number of
                 candlesticks plus one.
        """
        return len(self.candlesticks) * self.CHART_WIDTH_MULTIPLIER + self.CHART_WIDTH_OFFSET

    def get_price_range(self) -> Tuple[float, float]:
        """
        Get the price range of the chart.

        Returns:
            Tuple[float, float]: A tuple containing the minimum and maximum prices in the chart.
        """
        min_price = min(c.low for c in self.candlesticks)
        max_price = max(c.high for c in self.candlesticks)
        return min_price, max_price

    def get_candlestick_at_index(self, index: int) -> Optional[Candlestick]:
        """
        Get the candlestick at a specific index.

        Args:
            index (int): The index of the candlestick to retrieve.

        Returns:
            Optional[Candlestick]: The Candlestick object at the given index, or None if the index is out of range.
        """
        if 0 <= index < len(self.candlesticks):
            return self.candlesticks[index]
        return None

    def get_average_price(self) -> float:
        """
        Calculate the average price across all candlesticks.

        Returns:
            float: The average price.
        """
        total_price = sum((c.open + c.close) / 2 for c in self.candlesticks)
        return total_price / len(self.candlesticks)

    def is_uptrend(self) -> bool:
        """
        Determine if the chart shows an uptrend.

        Returns:
            bool: True if the closing price of the last candlestick is higher than the opening price of the first,
                  False otherwise.
        """
        if len(self.candlesticks) < 2:
            return False
        return self.candlesticks[-1].close > self.candlesticks[0].open
