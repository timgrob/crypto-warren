import unittest
from unittest.mock import Mock
from bots.bot import TradingBot
from bots.VolatilityTrader import VolatilityTrader
from strategies.trading_strategies_old import VolatilityTradingStrategy
from database.DatabaseConnectors import PostgresDatabase


class TestTraderBot(unittest.TestCase):
    """Test for trader bot"""

    def setUp(self) -> None:
        self.ticker = "XLM/USD"
        self.exchange = Mock()
        self.url = "postgresql://rpbfxloyfstnfm:14ebf390c87c2ac2aa88c516fec0aa7115f4a6794cd59a76b033f4f3fe02f89b@ec2-52-30-159-47.eu-west-1.compute.amazonaws.com:5432/d1s31eebs7ep6c"

    def test_bot_init(self):
        """test trader bot initialization"""
        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)
        self.assertIsInstance(volatility_trader, TradingBot)

    def test_bot_trade_buy_sell(self):
        """test trader bot buy signal"""

        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)

        self.exchange.fetch_balance.return_value = {
            "USD": {"free": None, "used": None, "total": 1000}
        }
        self.exchange.fetch_ticker.return_value = {
            "symbol": "XLM/USD",
            "timestamp": 1641903028764,
            "datetime": "2022-01-11T12:10:28.764Z",
            "high": 0.3,
            "low": 0.24,
            "bid": 0.25,
            "ask": 0.26,
        }
        self.exchange.create_limit_buy_order.return_value = {
            "id": "O3NPC3-UJWI2-GH4I23",
            "clientOrderId": None,
            "info": {
                "txid": ["O3NPC3-UJWI2-GH4I23"],
                "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
            },
            "timestamp": 1600977946935,
            "datetime": "2022-01-11T12:00:00.764Z",
            "symbol": "TRX/USD",
            "type": "limit",
            "side": "buy",
            "price": 0.26,
            "cost": None,
            "amount": 50.0,
            "filled": None,
            "fee": None,
            "trades": None,
            "fees": [],
        }

        self.exchange.create_limit_sell_order.return_value = {
            "id": "O4A7L7-X2PTZ-67PR7B",
            "clientOrderId": None,
            "info": {
                "txid": ["O4A7L7-X2PTZ-67PR7B"],
                "descr": {"order": "sell 50.00000000 TRXUSD @ limit 0.080000"},
            },
            "timestamp": 1600977946935,
            "datetime": "2022-01-11T12:00:00.764Z",
            "lastTradeTimestamp": None,
            "status": None,
            "symbol": "TRX/USD",
            "type": "limit",
            "timeInForce": None,
            "postOnly": None,
            "side": "sell",
            "price": 0.08,
            "stopPrice": None,
            "cost": None,
            "amount": 50.0,
            "filled": None,
            "average": None,
            "remaining": None,
            "fee": None,
            "trades": None,
            "fees": [],
        }
        volatility_trader.trade(self.ticker, False)
        # assert self.exchange.create_limit_buy_order.assert_called()
        # assert self.exchange.create_limit_sell_order.assert_called()

    def test_trader_bot_2x_buy(self):
        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)

        self.exchange.fetch_balance.return_value = {
            "USD": {"free": None, "used": None, "total": 1000}
        }
        self.exchange.fetch_ticker.side_effect = [
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T00:00:00.764Z",
                "high": 0.3,
                "low": 0.24,
                "bid": 0.25,
                "ask": 0.26,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.28,
                "low": 0.24,
                "bid": 0.24,
                "ask": 0.25,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.28,
                "low": 0.24,
                "bid": 0.25,
                "ask": 0.27,
            },
        ]

        self.exchange.create_limit_buy_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.26,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.25,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
        ]
        volatility_trader.trade(self.ticker)

    def test_trader_bot_2x_buy_1x_sell(self):
        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)

        self.exchange.fetch_balance.return_value = {
            "USD": {"free": None, "used": None, "total": 1000}
        }
        self.exchange.fetch_ticker.side_effect = [
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T00:00:00.764Z",
                "high": 0.30,
                "low": 0.240,
                "bid": 0.250,
                "ask": 0.261,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-10T12:00:00.764Z",
                "high": 0.290,
                "low": 0.250,
                "bid": 0.270,
                "ask": 0.260,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.280,
                "low": 0.240,
                "bid": 0.265,
                "ask": 0.260,
            },
        ]

        self.exchange.create_limit_buy_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.261,
                "cost": None,
                "amount": 957.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.26,
                "cost": None,
                "amount": 961.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
        ]

        self.exchange.create_limit_sell_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-14T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "sell",
                "price": 0.265,
                "cost": None,
                "amount": 961.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            }
        ]
        volatility_trader.trade(self.ticker)

    def test_trader_bot_2x_buy_2x_sell(self):
        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)

        self.exchange.fetch_balance.return_value = {
            "USD": {"free": None, "used": None, "total": 1000}
        }
        self.exchange.fetch_ticker.side_effect = [
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T00:00:00.764Z",
                "high": 0.3,
                "low": 0.24,
                "bid": 0.25,
                "ask": 0.26,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.28,
                "low": 0.24,
                "bid": 0.24,
                "ask": 0.25,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-10T12:00:00.764Z",
                "high": 0.275,
                "low": 0.25,
                "bid": 0.275,
                "ask": 0.273,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.276,
                "low": 0.25,
                "bid": 0.276,
                "ask": 0.274,
            },
        ]

        self.exchange.create_limit_buy_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.26,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.25,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
        ]

        self.exchange.create_limit_sell_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-14T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "sell",
                "price": 0.275,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-15T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "sell",
                "price": 0.276,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
        ]
        volatility_trader.trade(self.ticker)

    def test_trader_bot_1x_buy_1x_continue_1x_sell(self):
        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)

        self.exchange.fetch_balance.return_value = {
            "USD": {"free": None, "used": None, "total": 1000}
        }
        self.exchange.fetch_ticker.side_effect = [
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T00:00:00.764Z",
                "high": 0.3,
                "low": 0.24,
                "bid": 0.25,
                "ask": 0.26,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-10T12:00:00.764Z",
                "high": 0.27,
                "low": 0.25,
                "bid": 0.26,
                "ask": 0.25,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.27,
                "low": 0.24,
                "bid": 0.265,
                "ask": 0.25,
            },
        ]

        self.exchange.create_limit_buy_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.26,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            }
        ]

        self.exchange.create_limit_sell_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-14T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "sell",
                "price": 0.265,
                "cost": None,
                "amount": 50.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            }
        ]
        volatility_trader.trade(self.ticker)

    def test_trader_bot_1x_buy_2x_sell(self):
        volatility_strategy = VolatilityTradingStrategy()
        volatility_trader = VolatilityTrader(self.exchange, volatility_strategy)

        self.exchange.fetch_balance.return_value = {
            "USD": {"free": None, "used": None, "total": 1000}
        }
        self.exchange.fetch_ticker.side_effect = [
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T00:00:00.764Z",
                "high": 0.3,
                "low": 0.24,
                "bid": 0.25,
                "ask": 0.26,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-11T12:00:00.764Z",
                "high": 0.28,
                "low": 0.24,
                "bid": 0.265,
                "ask": 0.27,
            },
            {
                "symbol": "XLM/USD",
                "timestamp": 1641903028764,
                "datetime": "2022-01-12T12:00:00.764Z",
                "high": 0.29,
                "low": 0.26,
                "bid": 0.29,
                "ask": 0.27,
            },
        ]

        self.exchange.create_limit_buy_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-11T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "buy",
                "price": 0.26,
                "cost": None,
                "amount": 961.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            }
        ]

        self.exchange.create_limit_sell_order.side_effect = [
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-14T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "sell",
                "price": 0.265,
                "cost": None,
                "amount": 961.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
            {
                "id": "O3NPC3-UJWI2-GH4I23",
                "clientOrderId": None,
                "info": {
                    "txid": ["O3NPC3-UJWI2-GH4I23"],
                    "descr": {"order": "buy 50.00000000 TRXUSD @ limit 0.857166"},
                },
                "timestamp": 1600977946935,
                "datetime": "2022-01-15T12:00:00.764Z",
                "symbol": "TRX/USD",
                "type": "limit",
                "side": "sell",
                "price": 0.29,
                "cost": None,
                "amount": 100.0,
                "filled": None,
                "fee": None,
                "trades": None,
                "fees": [],
            },
        ]
        volatility_trader.trade(self.ticker)
