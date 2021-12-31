from exchanges.Bitstamp import Bitstamp
from exchanges.Kraken import Kraken
from os import environ
from bots.VolatilityTrader import VolatilityTrader


def main() -> None:
    """Main code for algorithmic trading"""

    # parameters
    ticker = environ['ticker']
    margin = float(environ['margin'])
    api_key = environ['kraken-api-key']
    secret = environ['kraken-secret']
    time_out = int(environ['time-out'])
    enable_rate_limit = bool(environ['enable-rate-limit'])

    # Exchange
    exchange = Kraken(api_key, secret, time_out, enable_rate_limit)
    exchange.connect()

    # Trading bot starts trading
    trading_bot = VolatilityTrader(exchange=exchange, margin=margin)
    trading_bot.trade(ticker)


if __name__ == "__main__":
    main()
