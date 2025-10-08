import os
import yaml
import ccxt.async_support as ccxt
from pathlib import Path

from src.db.database import Base, engine
from src.models.config import Config
from src.bots.trading_bot import TradingBot
from src.strategies.momentum_strategies import (
    EMATrendStrategy,
    EMASmoothingTrendStrategy,
)
from src.executions.execution import BotExecutor


PROJECT_DIR = Path.cwd()
SRC_DIR = PROJECT_DIR / "src"
CONFIGS_DIR = SRC_DIR / "configs"

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


def main() -> None:
    Base.metadata.create_all(engine)

    with (CONFIGS_DIR / "bot_config.yaml").open() as f:
        cfg = yaml.safe_load(f)

    config = Config(**cfg)
    exchange = ccxt.binance({"apiKey": API_KEY, "secret": API_SECRET})
    strategy = EMASmoothingTrendStrategy(config)
    trading_bot = TradingBot(exchange, strategy)

    BotExecutor(trading_bot).run()


if __name__ == "__main__":
    main()
