import unittest
from strategies.TradingStrategy import TradingStrategy, VolatilityTradingStrategy, MinMaxTradingStrategy


class TestTradingStrategy(unittest.TestCase):

    def test_volatility_trading_strategy_buy(self):
        token_data_buy_true = {
            'symbol': 'XLM/USD',
            'timestamp': 1641640989261,
            'datetime': '2022-01-08T11:23:09.261Z',
            'high': 0.33,
            'low': 0.25,
            'bid': 0.26,
            'bidVolume': None,
            'ask': 0.26,
            'askVolume': None,
            'vwap': 0.25915793,
            'open': 0.25727,
            'close': 0.260238,
            'last': 0.260238,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': 5613141.40130624,
            'quoteVolume': 1454690.1063598243
        }

        vola_strategy_true = VolatilityTradingStrategy(margin=0.1)
        signal_true = vola_strategy_true.buy_signal(token_data_buy_true)
        self.assertIsInstance(vola_strategy_true, TradingStrategy)
        self.assertTrue(signal_true)

        token_data_buy_false = {
            'symbol': 'XLM/USD',
            'timestamp': 1641640989261,
            'datetime': '2022-01-08T11:23:09.261Z',
            'high': 0.3,
            'low': 0.2,
            'bid': 0.2,
            'bidVolume': None,
            'ask': 0.28,
            'askVolume': None,
            'vwap': 0.25915793,
            'open': 0.25727,
            'close': 0.260238,
            'last': 0.260238,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': 5613141.40130624,
            'quoteVolume': 1454690.1063598243
        }

        vola_strategy_false = VolatilityTradingStrategy(margin=0.1)
        signal_false = vola_strategy_false.buy_signal(token_data_buy_false)
        self.assertIsInstance(vola_strategy_false, TradingStrategy)
        self.assertFalse(signal_false)

    def test_volatility_trading_strategy_sell(self):
        token_data_sell_true = {
            'symbol': 'XLM/USD',
            'timestamp': 1641640989261,
            'datetime': '2022-01-08T11:23:09.261Z',
            'high': 0.26,
            'low': 0.2,
            'bid': 0.22,
            'bidVolume': None,
            'ask': 0.26,
            'askVolume': None,
            'vwap': 0.25915793,
            'open': 0.25727,
            'close': 0.260238,
            'last': 0.260238,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': 5613141.40130624,
            'quoteVolume': 1454690.1063598243
        }

        vola_strategy_true = VolatilityTradingStrategy(margin=0.05)
        signal_true = vola_strategy_true.sell_signal(token_data_sell_true)
        self.assertIsInstance(vola_strategy_true, TradingStrategy)
        self.assertTrue(signal_true)

        token_data_sell_false = {
            'symbol': 'XLM/USD',
            'timestamp': 1641640989261,
            'datetime': '2022-01-08T11:23:09.261Z',
            'high': 0.26,
            'low': 0.2,
            'bid': 0.21,
            'bidVolume': None,
            'ask': 0.26,
            'askVolume': None,
            'vwap': 0.25915793,
            'open': 0.25727,
            'close': 0.260238,
            'last': 0.260238,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': 5613141.40130624,
            'quoteVolume': 1454690.1063598243
        }

        vola_strategy_false = VolatilityTradingStrategy(margin=0.05)
        signal_false = vola_strategy_false.sell_signal(token_data_sell_false)
        self.assertIsInstance(vola_strategy_false, TradingStrategy)
        self.assertFalse(signal_false)

    def test_min_max_trading_strategy(self):
        token_data = {
            'symbol': 'XLM/USD',
            'timestamp': 1641640989261,
            'datetime': '2022-01-08T11:23:09.261Z',
            'high': 0.26,
            'low': 0.2,
            'bid': 0.21,
            'bidVolume': None,
            'ask': 0.3,
            'askVolume': None,
            'vwap': 0.25915793,
            'open': 0.25727,
            'close': 0.260238,
            'last': 0.260238,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': 5613141.40130624,
            'quoteVolume': 1454690.1063598243
        }

        min_max_strategy_1 = MinMaxTradingStrategy(min_price=0.2, max_price=0.3)
        signal_true = min_max_strategy_1.buy_signal(token_data)
        signal_false = min_max_strategy_1.sell_signal(token_data)
        self.assertIsInstance(min_max_strategy_1, TradingStrategy)
        self.assertTrue(signal_true)
        self.assertFalse(signal_false)

        min_max_strategy_2 = MinMaxTradingStrategy(min_price=0.3, max_price=0.4)
        signal_false = min_max_strategy_2.buy_signal(token_data)
        signal_true = min_max_strategy_2.sell_signal(token_data)
        self.assertIsInstance(min_max_strategy_2, TradingStrategy)
        self.assertFalse(signal_false)
        self.assertTrue(signal_true)
