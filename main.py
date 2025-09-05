import os
import yaml
import ccxt
from pathlib import Path

from src.db.database import Base, engine
from src.models.config import Config
from src.bots.bot import TradingBot
from src.strategies.trading_strategies import TestStrategy
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
    strategy = TestStrategy(window=8)
    trading_bot = TradingBot(exchange, strategy, config)

    BotExecutor(trading_bot).run()

    # Base.metadata.create_all(engine)

    # # parameters
    # ticker = environ['ticker']
    # margin = float(environ['margin'])
    # api_key = environ['kraken-api-key']
    # secret = environ['kraken-secret']
    # time_out = int(environ['time-out'])

    # # Exchange
    # exchange = ccxt.kraken({'apiKey': api_key, 'secret': secret, 'timeout': time_out})

    # # Trading strategy
    # volatility_strategy = VolatilityTradingStrategy(margin=margin, bounce_back=0.7)

    # # Initialize trading bot
    # trading_bot = VolatilityTrader(exchange=exchange, trading_strategy=volatility_strategy)

    # # Trading bot starts trading
    # trading_bot.trade(ticker)


if __name__ == "__main__":
    main()
