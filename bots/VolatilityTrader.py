import os
import time
import random
import ccxt
import logging
from queue import LifoQueue
from datetime import datetime, timedelta
from strategies.Trade import Trade
from bots.TradingBot import TradingBot
from strategies.TradingStrategy import TradingStrategy


class VolatilityTrader(TradingBot):

    def __init__(self, exchange: ccxt.Exchange, trading_strategy: TradingStrategy, max_number_investment: int = 4) -> None:
        super().__init__(exchange, trading_strategy)
        self.trades = LifoQueue(max_number_investment)
        self.max_number_investment = max_number_investment
        self.RUNNING = True

    def trade(self, token: str) -> None:
        """This is the trading function for the volatility trader"""

        # initialize logger
        logfile_path = os.path.join(os.path.dirname(__file__), os.pardir)
        logging.basicConfig(filename=os.path.join(logfile_path, 'logfile.log'), level=logging.INFO)

        currencies = token.split('/')
        balance = self.exchange.fetch_balance()
        total_cash = balance[currencies[1]]['total']
        invest_cash_amount = total_cash/self.max_number_investment
        last_buy_trade = Trade((datetime.now() - timedelta(hours=24)), token, 0, 0.0)

        info_txt = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: " \
                   f"Trading {token} - {self.trading_strategy} with {invest_cash_amount}{currencies[1]}"
        logging.info(info_txt)
        print(info_txt)

        while self.RUNNING:
            token_data = self.exchange.fetch_ticker(token)
            passed_12h = True if (datetime.now() - timedelta(hours=12)) > last_buy_trade.timestamp else False

            if self.trading_strategy.sell_signal(token_data) and not self.trades.empty() and token_data['bid'] > last_buy_trade.price:
                last_buy_trade = self.trades.get()
                sell_order = self.exchange.create_limit_sell_order(token_data['symbol'], last_buy_trade.qty, token_data['bid'])

                # update last buy trade, yet remember to put the element back into the queue
                if not self.trades.empty():
                    last_buy_trade = self.trades.get()
                    self.trades.put(last_buy_trade)

                # log sell trade
                info_txt_sell = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "\
                                f"{sell_order['side']} {sell_order['symbol']} - "\
                                f"{sell_order['amount']} @ {sell_order['price']}"
                logging.info(info_txt_sell)
                print(info_txt_sell)

            elif self.trading_strategy.buy_signal(token_data) and not self.trades.full() and passed_12h:
                amount = round(invest_cash_amount/token_data['ask'], 4)
                buy_order = self.exchange.create_limit_buy_order(token_data['symbol'], amount, token_data['ask'])

                # not all exchanges return a datetime value, because the trade may not have instantly been executed
                if buy_order['datetime']:
                    buy_oder_datetime = datetime.strptime(buy_order['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                else:
                    buy_oder_datetime = datetime.now()

                last_buy_trade = Trade(buy_oder_datetime,
                                       buy_order['symbol'],
                                       buy_order['amount'],
                                       buy_order['price']
                                       )
                self.trades.put(last_buy_trade)

                # log buy trade
                info_txt_buy = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "\
                               f"{buy_order['side']} {buy_order['symbol']} - "\
                               f"{buy_order['amount']} @ {buy_order['price']}"
                logging.info(info_txt_buy)
                print(info_txt_buy)
            else:
                time.sleep(random.randint(60*15, 60*30))
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: continue")
                continue
