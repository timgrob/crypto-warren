import pytest
import pandas as pd

from models.config import Config
from models.trading import Trend
from strategies.momentum_strategies import EMATrendStrategy, SavgolTrendStrategy


@pytest.fixture
def config():
    symbols = ["SUI/USDC:USDC"]
    rate = "1h"
    timeframe = "1h"
    leverage = 5
    position_notional_value = 10
    atr_stop_loss = 1.5
    enable_trading = False
    params = {
        "ema_window": 8,
        "smooth_window": 11,
        "polyorder": 5,
    }

    config = Config(
        symbols=symbols,
        rate=rate,
        timeframe=timeframe,
        leverage=leverage,
        position_notional_value=position_notional_value,
        atr_stop_loss=atr_stop_loss,
        enable_trading=enable_trading,
        params=params,
    )
    return config


def test_ema_trend_strategy_up(config):
    strategy = EMATrendStrategy(config)
    prices = pd.Series([180.0, 181.0, 183.0, 186.0])
    trend = strategy.current_trend(prices)
    assert trend == Trend.UP


def test_ema_trend_strategy_down(config):
    strategy = EMATrendStrategy(config)
    ewms = pd.Series([180.0, 183.0, 186.0, 181.0])
    trend = strategy.current_trend(ewms)
    assert trend == Trend.DOWN


def test_ema_trend_strategy_not_enough_entries(config):
    strategy = EMATrendStrategy(config)
    ewms = pd.Series([180.0])
    trend = strategy.current_trend(ewms)
    assert trend == Trend.NONE


def test_ema_smoothing_trend_strategy_up(config):
    strategy = SavgolTrendStrategy(config)
    prices = pd.Series(
        [
            180.6,
            179.7,
            179.2,
            178.8,
            177.5,
            176.7,
            176.3,
            176.4,
            177.2,
            178.1,
            179.1,
            179.8,
            180.2,
            180.6,
            180.6,
            180.7,
            180.9,
            180.5,
            181.8,
            183.8,
            186.0,
            187.9,
            189.1,
            190.6,
        ]
    )
    trend = strategy.current_trend(prices)
    assert trend == Trend.UP


def test_ema_smoothing_trend_strategy_down(config):
    strategy = SavgolTrendStrategy(config)
    ewms = pd.Series(
        [
            180.6,
            179.7,
            179.2,
            178.8,
            177.5,
            176.7,
            176.3,
            176.4,
            177.2,
            178.1,
            179.1,
            179.8,
            180.2,
            180.6,
            180.6,
            180.7,
            179.9,
            179.5,
        ]
    )
    trend = strategy.current_trend(ewms)
    assert trend == Trend.DOWN


def test_ema_smoothing_trend_strategy_not_enough_entries(config):
    strategy = SavgolTrendStrategy(config)
    ewms = pd.Series([180.550675])
    trend = strategy.current_trend(ewms)
    assert trend == Trend.NONE
