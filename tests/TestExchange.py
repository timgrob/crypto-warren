from os import environ
import unittest
import ccxt
from distutils import util
from unittest.mock import patch
from exchanges.Exchange import Exchange
from exchanges.Bitstamp import Bitstamp
from exchanges.Kraken import Kraken


class TestExchange(unittest.TestCase):

    @patch.dict(environ, {'bitstamp-api-key': 'bistamp_api_key',
                          'bitstamp-secret': 'bitstamp_secret',
                          'kraken-api-key': 'kraken_api_key',
                          'kraken-secret': 'kraken_test_secret',
                          'time-out': '4000',
                          'enable-rate-limit': 'False'})
    def setUp(self) -> None:
        self.bitstamp_api_key = environ['bitstamp-api-key']
        self.bitstamp_secret = environ['bitstamp-secret']
        self.kraken_api_key = environ['kraken-api-key']
        self.kraken_secret = environ['kraken-secret']
        self.time_out = int(environ['time-out'])
        self.enable_rate_limit = bool(util.strtobool(environ['enable-rate-limit']))

    def test_exchange_init(self):
        exchange_bitstamp = Bitstamp(self.bitstamp_api_key, self.bitstamp_secret)
        exchange_kraken = Kraken(self.kraken_api_key, self.kraken_secret)

        self.assertIsInstance(exchange_bitstamp, Exchange)
        self.assertIsNone(exchange_bitstamp.exchange)
        self.assertEqual(exchange_bitstamp.api_key, self.bitstamp_api_key)
        self.assertEqual(exchange_bitstamp.secret, self.bitstamp_secret)
        self.assertIsInstance(exchange_kraken, Exchange)
        self.assertIsNone(exchange_kraken.exchange)
        self.assertEqual(exchange_kraken.api_key, self.kraken_api_key)
        self.assertEqual(exchange_kraken.secret, self.kraken_secret)

    def test_exchange_init_with_params(self):
        exchange_bitstamp = Bitstamp(self.kraken_api_key, self.kraken_secret, self.time_out, self.enable_rate_limit)
        exchange_karken = Kraken(self.kraken_api_key, self.kraken_secret, self.time_out, self.enable_rate_limit)

        self.assertEqual(exchange_bitstamp.time_out, 4000)
        self.assertEqual(exchange_bitstamp.enable_rate_limit, False)
        self.assertEqual(exchange_karken.time_out, 4000)
        self.assertEqual(exchange_karken.enable_rate_limit, False)

    def test_exchange_connect(self):
        exchange_bitstamp = Bitstamp(self.bitstamp_api_key, self.bitstamp_secret)
        exchange_bitstamp.connect()
        exchange_kraken = Kraken(self.kraken_api_key, self.kraken_secret)
        exchange_kraken.connect()

        self.assertIsInstance(exchange_bitstamp.exchange, ccxt.bitstamp)
        self.assertIsInstance(exchange_kraken.exchange, ccxt.kraken)
