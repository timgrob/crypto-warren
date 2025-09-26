from ta.trend import EMAIndicator
import pandas as pd
import scipy.signal
import scipy

from src.strategies.strategy import Strategy
from src.models.trading import Trend


class EMATrendStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.window = 8
        self.smooth_window = 15
        self.polyorder = 4

    def buy_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.UP

    def sell_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.DOWN

    def current_trend(self, ohlcv, col_name: str = "close"):
        prices = ohlcv[col_name]
        ema_indicator = EMAIndicator(prices, self.window, fillna=True)
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

    def _apply_smoothing(self, emas: pd.Series) -> pd.Series:
        # Spline smoothing
        window, poly = self.smooth_window, self.polyorder
        emas_savgol = scipy.signal.savgol_filter(emas.values, window, poly)
        return pd.Series(emas_savgol)
