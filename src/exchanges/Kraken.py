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
