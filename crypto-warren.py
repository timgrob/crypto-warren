import ccxt
import json
from os import environ
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

    # Exchange
    exchange = ccxt.kraken({'apiKey': api_key, 'secret': secret, 'timeout': time_out})

    # Trading strategy
    volatility_strategy = VolatilityTradingStrategy(margin=margin)

    # Trading bot starts trading
    trading_bot = VolatilityTrader(exchange=exchange, trading_strategy=volatility_strategy)
    trading_bot.trade(ticker)

def main_json():
    import json

    data = {
        'employees': [
            {
                'name': 'John Doe',
                'department': 'Marketing',
                'place': 'Remote'
            }
        ]
    }

    json_string = json.dumps(data)

    # Using a JSON string
    with open('json_data.json', 'w') as outfile:
        outfile.write(json_string)

if __name__ == "__main__":
    main()
