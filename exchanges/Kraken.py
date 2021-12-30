import ccxt
from exchanges.Exchange import Exchange


class Kraken(Exchange):

    def connect(self):
        self.exchange = ccxt.kraken({
            'apiKey': self.api_key,
            'secret': self.secret,
            'timeout': self.time_out,
            'enableRateLimit': self.enable_rate_limit
        })

    def fetch_balance(self):
        balance_data = self.exchange.fetch_balance()
        return balance_data

    def fetch_token_data(self, token: str):
        current_ticker = self.exchange.fetch_ticker(token)
        return current_ticker
