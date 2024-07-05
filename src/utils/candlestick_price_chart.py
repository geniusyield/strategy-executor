from typing import Dict, List

from src.models.candlestick import Candlestick


class CandlestickPriceChart:
    def __init__(self, candlestick_price_chart_data: List[Dict[str, float]]):
        self.candlesticks = [Candlestick.create_if_valid(cpc) for cpc in candlestick_price_chart_data]
        self.candlesticks = [cs for cs in self.candlesticks if cs is not None]
        self.chart_height = len(self.candlesticks)
        self.chart_width = len(self.candlesticks) * 2 + 1

    def plot(self):
        if not self.candlesticks:
            print("No data to plot.")
            return

        min_price = min(c.low for c in self.candlesticks)
        max_price = max(c.high for c in self.candlesticks)
        price_range = max_price - min_price

        chart = [
            [" " for _ in range(self.chart_width)] for _ in range(self.chart_height)
        ]

        for i, candle in enumerate(self.candlesticks):
            x = i * 2 + 1
            self._plot_candle(chart, candle, x, min_price, price_range)

        self._add_axes(chart, min_price, max_price)
        self._print_chart(chart)

    def _plot_candle(self, chart, candle, x, min_price, price_range):
        def price_to_y(price):
            return (
                self.chart_height
                - 1
                - int((price - min_price) / price_range * (self.chart_height - 1))
            )

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

    def _add_axes(self, chart, min_price, max_price):
        for y in range(self.chart_height):
            chart[y][0] = "│"
        for x in range(self.chart_width):
            chart[-1][x] = "─"
        chart[-1][0] = "└"

        # Add price labels
        for i in range(5):
            price = min_price + (max_price - min_price) * i / 4
            y = self.chart_height - 1 - int(i * (self.chart_height - 1) / 4)
            price_str = f"{price:.2f}"
            for j, char in enumerate(price_str):
                if j < len(chart[y]) - 1:
                    chart[y][j + 1] = char

    def _print_chart(self, chart):
        for row in chart:
            print("".join(row))
