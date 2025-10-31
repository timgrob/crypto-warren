import yaml
import asyncio
import pandas as pd
from pathlib import Path

from src.models.config import Config
from src.bots.trading_bot import TradingBot
from src.strategies.momentum_strategies import (
    EMATrendStrategy,
    SavgolTrendStrategy,
    KalmanTrendStrategy,
)
from tests.mock_exchange import MockExchange
from tests.test_executor import TestExecutor

PROJECT_DIR = Path.cwd()
TEST_DIR = PROJECT_DIR / "tests"
CONFIGS_DIR = TEST_DIR / "configs"
DATA_DIR = TEST_DIR / "data"


def main():
    with (CONFIGS_DIR / "test_config.yaml").open() as f:
        cfg = yaml.safe_load(f)

    config = Config(**cfg)

    # filename = ""
    ohlcv = pd.read_csv(DATA_DIR / "ohlcv-1h-sol-usdc-usdc.csv")

    exchange = MockExchange()
    strategy = KalmanTrendStrategy(config)
    trading_bot = TradingBot(exchange, strategy)

    asyncio.run(TestExecutor(trading_bot, ohlcv).run())


if __name__ == "__main__":
    main()
