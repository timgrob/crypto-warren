from ta.trend import EMAIndicator
from pykalman import KalmanFilter
from scipy.signal import savgol_filter
from loguru import logger
import pandas as pd

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
        if len(prices) < self.window:
            return Trend.NONE

        ema_indicator = EMAIndicator(prices, self.window, fillna=True)
        emas = ema_indicator.ema_indicator()

        # Find latest gradient of emas
        diff = emas.diff()
        delta = float(diff.iloc[-1])

        if delta == 0:
            trend = Trend.NONE
        else:
            trend = Trend.UP if delta > 0 else Trend.DOWN

        return trend


class SavgolTrendStrategy(Strategy):
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
        if len(prices) < self.window:
            return Trend.NONE

        ema_indicator = EMAIndicator(prices, self.window, fillna=True)
        emas = ema_indicator.ema_indicator()

        # Apply Savitzky–Golay filter on emas
        savgol_emas = savgol_filter(emas.values, self.smooth_window, self.polyorder)
        smoothed_emas = pd.Series(savgol_emas)

        # Find latest gradient of smoothed emas
        diff = smoothed_emas.diff()
        delta = float(diff.iloc[-1])

        logger.debug(f"Savgol: {', '.join([str(round(v, 3)) for v in diff.tail()])}")

        if delta == 0:
            trend = Trend.NONE
        else:
            trend = Trend.UP if delta > 0 else Trend.DOWN

        return trend


class KalmanTrendStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.kf = KalmanFilter()

    def buy_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.UP

    def sell_signal(self, ohlcv):
        trend = self.current_trend(ohlcv)
        return trend == Trend.DOWN

    def current_trend(self, prices: pd.Series):
        kf = self.kf.em(prices)
        smoothed, _ = kf.smooth(prices.values)
        smoothed_prices = pd.Series(list(map(lambda x: x[0], smoothed)))

        # Find latest gradient of smoothed prices
        diff = smoothed_prices.diff()
        delta = float(diff.iloc[-1])

        logger.debug(f"Kalman: {', '.join([str(round(v, 3)) for v in diff.tail()])}")

        # A too small delta, is not considered as a trend
        if -0.1 <= delta <= 0.1:
            trend = Trend.NONE
        else:
            trend = Trend.UP if delta > 0 else Trend.DOWN

        return trend
