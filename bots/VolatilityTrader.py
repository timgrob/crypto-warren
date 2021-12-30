import time
import random
import logging
from queue import LifoQueue
from datetime import datetime, timedelta
from strategies.Trade import Trade
from bots.TradingBot import TradingBot
from exchanges.Exchange import Exchange


class VolatilityTrader(TradingBot):

    def __init__(self, exchange: Exchange, margin: float = 0.1, max_number_investment: int = 4) -> None:
        super().__init__(exchange)
        self.margin = margin
        self.trades = LifoQueue(max_number_investment)
        self.max_number_investment = max_number_investment

    def trade(self, token: str) -> None:
        # initialize logger
        logging.basicConfig(filename='logfile.log', level=logging.INFO)
        logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start Program")

        currencies = token.split('/')
        balance = self.exchange.fetch_balance()
        total_cash = balance[currencies[1]]['total']
        invest_cash_amount = total_cash/self.max_number_investment
        last_buy_trade = Trade((datetime.now() - timedelta(hours=24)), token, 0, 0.0)

        while True:
            token_data = self.exchange.fetch_token_data(token)
            passed_24h = True if (datetime.now() - timedelta(hours=24)) > last_buy_trade.timestamp else False

            if token_data['bid'] >= (1 + self.margin) * token_data['low'] and not self.trades.empty() and token_data['bid'] > last_buy_trade.price:
                last_trade = self.trades.get()
                sell_order = self.exchange.create_limit_sell_order(token_data['symbol'], last_trade.qty, token_data['bid'])

                # log sell trade
                logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "
                             f"{sell_order['side']} {sell_order['symbol']} - "
                             f"{sell_order['amount']} @ {sell_order['price']}")

            elif token_data['ask'] <= (1 - self.margin) * token_data['high'] and not self.trades.full() and passed_24h:
                amount = invest_cash_amount/token_data['ask']
                buy_order = self.exchange.create_limit_buy_order(token_data['symbol'], amount, token_data['ask'])
                last_buy_trade = Trade(datetime.strptime(buy_order['datetime'].split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                                       buy_order['symbol'],
                                       buy_order['amount'],
                                       buy_order['price']
                                       )
                self.trades.put(last_buy_trade)

                # log buy trade
                logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "
                             f"{buy_order['side']} {buy_order['symbol']} - "
                             f"{buy_order['amount']} @ {buy_order['price']}")
            else:
                continue

            time.sleep(random.randint(30, 120))
