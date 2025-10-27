import backtrader as bt
import pandas as pd
import scipy.signal
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange
from loguru import logger

from src.models.trading import Trend


class BacktraderEMASmoothingStrategy(bt.Strategy):
    """
    Backtrader adapter for EMASmoothingTrendStrategy.

    This strategy uses EMA with Savitzky-Golay smoothing to detect trends
    and trades based on trend changes with ATR-based trailing stop losses.
    """

    params = (
        ("ema_window", 8),
        ("smooth_window", 12),
        ("polyorder", 5),
        ("atr_stop_loss", 1.4),
        ("position_notional_value", 10.0),
        ("leverage", 3),
        ("printlog", True),
    )

    def __init__(self):
        """Initialize the strategy."""
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.current_trend = Trend.NONE

        # Track trades for logging
        self.trade_count = 0

    def log(self, txt, dt=None, do_print=None):
        """Logging function for the strategy."""
        if do_print is None:
            do_print = self.params.printlog

        if do_print:
            dt = dt or self.datas[0].datetime.date(0)
            logger.info(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        """Notification of order status."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED, Price: {order.executed.price:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}"
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f"SELL EXECUTED, Price: {order.executed.price:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}"
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"Order Canceled/Margin/Rejected: {order.status}")

        self.order = None

    def notify_trade(self, trade):
        """Notification of trade close."""
        if not trade.isclosed:
            return

        self.trade_count += 1
        self.log(
            f"TRADE #{self.trade_count} CLOSED - Profit: Gross ${trade.pnl:.2f}, Net ${trade.pnlcomm:.2f}"
        )

    def _calculate_trend(self, prices: pd.Series) -> Trend:
        """
        Calculate the current trend using EMA with Savitzky-Golay smoothing.

        Args:
            prices: Series of closing prices

        Returns:
            Current trend (UP, DOWN, or NONE)
        """
        if len(prices) < max(self.params.ema_window, self.params.smooth_window):
            return Trend.NONE

        # Calculate EMA
        ema_indicator = EMAIndicator(prices, self.params.ema_window, fillna=True)
        emas = ema_indicator.ema_indicator()

        # Apply Savitzky-Golay smoothing
        if len(emas) >= self.params.smooth_window:
            emas_smooth = scipy.signal.savgol_filter(
                emas.values,
                self.params.smooth_window,
                self.params.polyorder
            )
            emas = pd.Series(emas_smooth, index=emas.index)

        if len(emas) < 2:
            return Trend.NONE

        # Calculate trend from gradient
        diff = emas.diff()
        delta = float(diff.iloc[-1])

        if delta == 0:
            return Trend.NONE
        else:
            return Trend.UP if delta > 0 else Trend.DOWN

    def _calculate_stop_loss(self) -> float:
        """
        Calculate trailing stop-loss percentage based on ATR.

        Returns:
            Stop loss percentage (0-100)
        """
        # Get recent price data
        window = self.params.ema_window
        if len(self.datas[0]) < window:
            return 1.0  # Default 1% stop loss

        # Extract recent OHLC data
        highs = [self.datahigh[-i] for i in range(window, 0, -1)]
        lows = [self.datalow[-i] for i in range(window, 0, -1)]
        closes = [self.dataclose[-i] for i in range(window, 0, -1)]

        highs_series = pd.Series(highs)
        lows_series = pd.Series(lows)
        closes_series = pd.Series(closes)

        # Calculate ATR
        atr_indicator = AverageTrueRange(highs_series, lows_series, closes_series)
        atrs = atr_indicator.average_true_range()

        # Calculate stop loss
        atrs_mean = atrs.tail(window).mean()
        current_price = self.dataclose[0]
        stop_loss = self.params.atr_stop_loss * atrs_mean / current_price

        # Ensure stop loss is between 0.1% and 10%
        callback_rate = min(max(stop_loss * 100, 0.1), 10.0)

        return callback_rate

    def next(self):
        """Execute on each new bar."""
        # Get enough data for trend calculation
        window_required = max(200, self.params.smooth_window * 2)

        if len(self.datas[0]) < window_required:
            return

        # Calculate current trend
        prices = pd.Series([self.dataclose[-i] for i in range(window_required, 0, -1)])
        new_trend = self._calculate_trend(prices)

        # Determine position trend
        if self.position:
            position_trend = Trend.UP if self.position.size > 0 else Trend.DOWN
        else:
            position_trend = Trend.NONE

        # Log trend information
        self.log(
            f"Close: {self.dataclose[0]:.2f}, Position Trend: {position_trend}, "
            f"Market Trend: {new_trend}, Position Size: {self.position.size if self.position else 0}",
            do_print=False
        )

        # Check if there's a pending order
        if self.order:
            return

        # No strong trend detected
        if new_trend == Trend.NONE:
            return

        # Trend hasn't changed
        if new_trend == position_trend:
            return

        # Trend has changed - execute trade
        current_price = self.dataclose[0]
        position_size = self.params.position_notional_value / current_price

        # Close existing position if any
        if self.position:
            self.log(f"Closing position: {self.position.size:.4f} @ {current_price:.2f}")
            self.order = self.close()
            return

        # Open new position based on trend
        if new_trend == Trend.UP:
            self.log(f"BUY CREATE: {position_size:.4f} @ {current_price:.2f}")
            self.order = self.buy(size=position_size)
            self.current_trend = Trend.UP

        elif new_trend == Trend.DOWN:
            self.log(f"SELL CREATE: {position_size:.4f} @ {current_price:.2f}")
            self.order = self.sell(size=position_size)
            self.current_trend = Trend.DOWN

    def stop(self):
        """Called when backtesting ends."""
        self.log(
            f"Ending Value: ${self.broker.getvalue():.2f}, "
            f"Total Trades: {self.trade_count}",
            do_print=True
        )


class BacktraderEMAStrategy(bt.Strategy):
    """
    Backtrader adapter for simple EMATrendStrategy (without smoothing).
    """

    params = (
        ("ema_window", 8),
        ("atr_stop_loss", 1.4),
        ("position_notional_value", 10.0),
        ("leverage", 3),
        ("printlog", True),
    )

    def __init__(self):
        """Initialize the strategy."""
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

        self.order = None
        self.current_trend = Trend.NONE
        self.trade_count = 0

    def log(self, txt, dt=None, do_print=None):
        """Logging function for the strategy."""
        if do_print is None:
            do_print = self.params.printlog

        if do_print:
            dt = dt or self.datas[0].datetime.date(0)
            logger.info(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        """Notification of order status."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order.executed.price:.2f}")
            else:
                self.log(f"SELL EXECUTED, Price: {order.executed.price:.2f}")

        self.order = None

    def notify_trade(self, trade):
        """Notification of trade close."""
        if not trade.isclosed:
            return

        self.trade_count += 1
        self.log(f"TRADE #{self.trade_count} CLOSED - Profit: ${trade.pnlcomm:.2f}")

    def _calculate_trend(self, prices: pd.Series) -> Trend:
        """Calculate trend using simple EMA."""
        if len(prices) < self.params.ema_window:
            return Trend.NONE

        ema_indicator = EMAIndicator(prices, self.params.ema_window, fillna=True)
        emas = ema_indicator.ema_indicator()

        if len(emas) < 2:
            return Trend.NONE

        diff = emas.diff()
        delta = float(diff.iloc[-1])

        if delta == 0:
            return Trend.NONE
        else:
            return Trend.UP if delta > 0 else Trend.DOWN

    def next(self):
        """Execute on each new bar."""
        window_required = max(200, self.params.ema_window * 2)

        if len(self.datas[0]) < window_required:
            return

        prices = pd.Series([self.dataclose[-i] for i in range(window_required, 0, -1)])
        new_trend = self._calculate_trend(prices)

        if self.position:
            position_trend = Trend.UP if self.position.size > 0 else Trend.DOWN
        else:
            position_trend = Trend.NONE

        if self.order or new_trend == Trend.NONE or new_trend == position_trend:
            return

        current_price = self.dataclose[0]
        position_size = self.params.position_notional_value / current_price

        if self.position:
            self.order = self.close()
            return

        if new_trend == Trend.UP:
            self.order = self.buy(size=position_size)
        elif new_trend == Trend.DOWN:
            self.order = self.sell(size=position_size)

    def stop(self):
        """Called when backtesting ends."""
        self.log(f"Ending Value: ${self.broker.getvalue():.2f}", do_print=True)
