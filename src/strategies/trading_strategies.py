from abc import ABC, abstractmethod
from ta.trend import EMAIndicator
import pandas as pd

from src.models.trading import Trend


class Strategy(ABC):
    def __init__(self):
        """Trading strategy that determines when to buy and when to sell"""

    @abstractmethod
    def buy_signal(self, ohlcv: pd.DataFrame) -> bool:
        """Determine the current trend based on the OHLCV data"""

    @abstractmethod
    def sell_signal(self, ohlcv: pd.DataFrame) -> bool:
        """Determine the current trend based on the OHLCV data"""


class TestStrategy(Strategy):
    def __init__(self, window: int):
        super().__init__()
        self.window = window

    def buy_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.UP

    def sell_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.DOWN

    def current_trend(self, ohlcv):
        ema_indicator = EMAIndicator(ohlcv["close"], int(self.window), fillna=True)
        emas = ema_indicator.ema_indicator()

        if len(emas) < 2:
            return Trend.NONE

        # Find latest gradient
        diff = emas.diff()
        delta = float(diff.iloc[-1])

        if delta == 0:
            trend = Trend.NONE
        else:
            trend = Trend.UP if delta > 0 else Trend.DOWN

        return trend
