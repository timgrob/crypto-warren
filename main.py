import os
import yaml
import ccxt
from pathlib import Path

from src.db.database import Base, engine
from src.models.config import Config
from src.models.exchange import Exchange
from src.bots.trading_bot import TradingBot
from src.strategies.momentum_strategies import EMATrendStrategy
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
    exchange = ccxt.Exchange(
        {
            "apiKey": API_KEY,
            "secret": API_SECRET,
            "enableRateLimit": True,
            "options": {"defaultType": "future"},
        }
    )
    strategy = EMATrendStrategy(config)
    trading_bot = TradingBot(exchange, strategy)

    BotExecutor(trading_bot).run()


if __name__ == "__main__":
    main()
