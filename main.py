import os
import ccxt
import asyncio
# from src.bots.VolatilityTrader import VolatilityTrader
# from src.strategies.TradingStrategies import VolatilityTradingStrategy

from src.db.database import Base, engine

from src.executions.execution import BotExecutor
from src.bots.bot import TradingBot
from src.strategies.strategy import Strategy


def main() -> None:
    Base.metadata.create_all(engine)

    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    exchange = ccxt.kraken({'apiKey': API_KEY, 'secret': API_SECRET})
    strategy = Strategy()
    trading_bot = TradingBot(exchange, strategy)

    BotExecutor(trading_bot).start()

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
