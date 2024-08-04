import logging
from typing import List, Optional

from src.models.candlestick import Candlestick
from src.models.candlestick_price_chart import CandlestickPriceChart


class CandlestickPriceChartView:
    """
    A class for visualizing a candlestick price chart.

    This class takes a CandlestickPriceChart and creates an ASCII representation
    of the candlestick chart.

    Attributes:
        model (CandlestickPriceChart): The model containing the chart data.
        logger (Optional[logging.Logger]): A logger for output messages.
    """

    def __init__(self, model: CandlestickPriceChart, logger: Optional[logging.Logger] = None):
        """
        Initialize the CandlestickPriceChartView.

        Args:
            model (CandlestickPriceChart): The model containing the chart data.
            logger (Optional[logging.Logger]): A logger for output messages. If None, print to console.
        """
        self.model = model
        self.logger = logger

    def plot(self) -> None:
        """
        Plot the candlestick chart.

        This method creates an ASCII representation of the candlestick chart
        and outputs it using the logger or print function.
        """
        if not self.model.candlesticks:
            self._log("No data to plot.")
            return

        min_price, max_price = self.model.get_price_range()
        price_range = max_price - min_price
        chart_height = self.model.chart_height
        chart_width = self.model.chart_width

        chart = [[" " for _ in range(chart_width)] for _ in range(chart_height)]

        for i, candle in enumerate(self.model.candlesticks):
            x = i * 2 + 1
            self._plot_candle(chart, candle, x, min_price, price_range, chart_height)

        self._add_axes(chart, min_price, max_price, chart_height, chart_width)
        self._print_chart(chart)

    def _plot_candle(self, chart: List[List[str]], candle: Candlestick, x: int,
                     min_price: float, price_range: float, chart_height: int) -> None:
        """
        Plot a single candlestick on the chart.

        Args:
            chart (List[List[str]]): The 2D list representing the chart.
            candle (Candlestick): The candlestick to plot.
            x (int): The x-coordinate of the candlestick on the chart.
            min_price (float): The minimum price in the chart.
            price_range (float): The range of prices in the chart.
            chart_height (int): The height of the chart.
        """
        def price_to_y(price: float) -> int:
            return chart_height - 1 - int((price - min_price) / price_range * (chart_height - 1))

        y_high = price_to_y(candle.high)
        y_low = price_to_y(candle.low)
        y_open = price_to_y(candle.open)
        y_close = price_to_y(candle.close)

        for y in range(y_high, y_low + 1):
            if y == y_high or y == y_low:
                chart[y][x] = "─"
            elif y_open < y_close:  # Bullish
                chart[y][x] = "│" if y_open <= y <= y_close else "│"
            elif y_open > y_close:  # Bearish
                chart[y][x] = "█" if y_close <= y <= y_open else "│"
            else:  # Doji
                chart[y][x] = "─"

    def _add_axes(self, chart: List[List[str]], min_price: float, max_price: float,
                  chart_height: int, chart_width: int) -> None:
        """
        Add axes and price labels to the chart.

        Args:
            chart (List[List[str]]): The 2D list representing the chart.
            min_price (float): The minimum price in the chart.
            max_price (float): The maximum price in the chart.
            chart_height (int): The height of the chart.
            chart_width (int): The width of the chart.
        """
        for y in range(chart_height):
            chart[y][0] = "│"
        for x in range(chart_width):
            chart[-1][x] = "─"
        chart[-1][0] = "└"

        # Add price labels
        for i in range(5):
            price = min_price + (max_price - min_price) * i / 4
            y = chart_height - 1 - int(i * (chart_height - 1) / 4)
            price_str = f"{price:.2f}"
            for j, char in enumerate(price_str):
                if j < len(chart[y]) - 1:
                    chart[y][j + 1] = char

    def _print_chart(self, chart: List[List[str]]) -> None:
        """
        Print the chart using the logger or print function.

        Args:
            chart (List[List[str]]): The 2D list representing the chart.
        """
        for row in chart:
            self._log("".join(row))

    def _log(self, message: str) -> None:
        """
        Log a message using the logger if available, otherwise print to console.

        Args:
            message (str): The message to log or print.
        """
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
