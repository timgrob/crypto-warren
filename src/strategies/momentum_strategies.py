from ta.trend import EMAIndicator
import pandas as pd
import scipy.signal
import scipy

from src.strategies.strategy import Strategy
from src.models.trading import Trend


class EMATrendStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        if not "ema_window" in config.params:
            raise KeyError("config not properly defined: missing 'ema_window'")

        self.window = config.params["ema_window"]

    def buy_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.UP

    def sell_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.DOWN

    def current_trend(self, prices):
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


class EMASmoothingTrendStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        required_keys = ["ema_window", "smooth_window", "polyorder"]
        if not all(key in config.params for key in required_keys):
            raise KeyError(
                f"config not properly defined: missing one parameter {required_keys}"
            )

        self.window = config.params["ema_window"]
        self.smooth_window = config.params["smooth_window"]
        self.polyorder = config.params["polyorder"]

    def buy_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.UP

    def sell_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.DOWN

    def current_trend(self, prices):
        ema_indicator = EMAIndicator(prices, self.window, fillna=True)
        emas = ema_indicator.ema_indicator()
        emas = self._apply_smoothing(emas)

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
