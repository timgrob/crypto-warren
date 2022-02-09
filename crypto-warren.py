import ccxt
from os import environ
from database.DatabaseConnectors import PostgresDatabase
from bots.VolatilityTrader import VolatilityTrader
from strategies.TradingStrategy import VolatilityTradingStrategy


def main() -> None:
    """Main code for algorithmic trading"""

    # parameters
    ticker = environ['ticker']
    margin = float(environ['margin'])
    api_key = environ['kraken-api-key']
    secret = environ['kraken-secret']
    time_out = int(environ['time-out'])
    database_url = environ['database_url']

    # Database
    postgres = PostgresDatabase(database_url)

    # Exchange
    exchange = ccxt.kraken({'apiKey': api_key, 'secret': secret, 'timeout': time_out})

    # Trading strategy
    volatility_strategy = VolatilityTradingStrategy(margin=margin)

    # Trading bot starts trading
    trading_bot = VolatilityTrader(exchange=exchange, trading_strategy=volatility_strategy, database_connection=postgres)
    trading_bot.trade(ticker)


if __name__ == "__main__":
    main()
