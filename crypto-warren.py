import ccxt
from os import environ
from bots.VolatilityTrader import VolatilityTrader
from strategies.TradingStrategies import VolatilityTradingStrategy


def main() -> None:
    """Main code for algorithmic trading"""

    # parameters
    ticker = environ['ticker']
    margin = float(environ['margin'])
    api_key = environ['kraken-api-key']
    secret = environ['kraken-secret']
    time_out = int(environ['time-out'])
    database_url = environ['DATABASE_URL']

    # Exchange
    exchange = ccxt.kraken({'apiKey': api_key, 'secret': secret, 'timeout': time_out})

    # Trading strategy
    volatility_strategy = VolatilityTradingStrategy(margin=margin, bounce_back=0.7)

    # Initialize trading bot
    trading_bot = VolatilityTrader(exchange=exchange, trading_strategy=volatility_strategy)

    # Trading bot starts trading
    trading_bot.trade(ticker)


if __name__ == "__main__":
    main()
