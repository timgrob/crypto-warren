import os
import time
import random
import ccxt
import logging
from queue import LifoQueue
from datetime import datetime, timedelta
from database.database_connection import Session
from database.model import Trade
from bots.bot import TradingBot
from strategies.TradingStrategies import TradingStrategy


class VolatilityTrader(TradingBot):

    def __init__(self, exchange: ccxt.Exchange, trading_strategy: TradingStrategy) -> None:
        super().__init__(exchange, trading_strategy)
        self.max_number_investment = 4
        self.trades = LifoQueue(self.max_number_investment)
        with Session() as session:
            with session.begin():
                trades = session.query(Trade).all()

            for tr in trades:
                trade = Trade(timestamp=tr.timestamp, symbol=tr.symbol, qty=tr.qty, price=tr.price)
                self.trades.put(trade)

    def trade(self, token: str, running: bool = True) -> None:
        """This is the trading function for the volatility trader"""

        # initialize logger
        logfile_path = os.path.join(os.path.dirname(__file__), os.pardir)
        logging.basicConfig(filename=os.path.join(logfile_path, 'logfile.log'), level=logging.INFO)

        currencies = token.split('/')
        balance = self.exchange.fetch_balance()
        total_cash = balance[currencies[1]]['total']
        if total_cash != 0 and self.trades.qsize() < 4:
            invest_cash_amount = total_cash/(self.max_number_investment-self.trades.qsize())

        # get last buy trade if there are any
        if self.trades.empty():
            last_buy_trade = Trade(timestamp=datetime.now() - timedelta(hours=24), symbol=token, qty=0, price=0.0)
        else:
            last_buy_trade = self.trades.get()
            self.trades.put(last_buy_trade)

        info_txt = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: " \
                   f"Trading {token} - {self.trading_strategy} with {invest_cash_amount} {currencies[1]}"
        logging.info(info_txt)
        print(info_txt)

        while running:
            token_data = self.exchange.fetch_ticker(token)
            passed_24h = True if (datetime.now() - timedelta(hours=24)) > last_buy_trade.timestamp else False

            if self.trading_strategy.sell_signal(token_data) and not self.trades.empty() and token_data['bid'] > last_buy_trade.price:
                last_buy_trade = self.trades.get()
                sell_order = self.exchange.create_limit_sell_order(token_data['symbol'], last_buy_trade.qty, token_data['bid'])
                with Session() as session:
                    with session.begin():
                        session.delete(last_buy_trade)

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

            elif self.trading_strategy.buy_signal(token_data) and not self.trades.full() and passed_24h:
                amount = round(invest_cash_amount/token_data['ask'], 4)
                buy_order = self.exchange.create_limit_buy_order(token_data['symbol'], amount, token_data['ask'])

                # not all exchanges return a datetime value, because the trade may not have instantly been executed
                if buy_order['datetime']:
                    buy_oder_datetime = datetime.strptime(buy_order['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                else:
                    buy_oder_datetime = datetime.now()

                last_buy_trade = Trade(timestamp=buy_oder_datetime,
                                       symbol=buy_order['symbol'],
                                       qty=buy_order['amount'],
                                       price=buy_order['price']
                                       )
                self.trades.put(last_buy_trade)

                # write buy trade to database
                with Session() as session:
                    with session.begin():
                        session.add(last_buy_trade)

                # log buy trade
                info_txt_buy = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "\
                               f"{buy_order['side']} {buy_order['symbol']} - "\
                               f"{buy_order['amount']} @ {buy_order['price']}"
                logging.info(info_txt_buy)
                print(info_txt_buy)
            else:
                time.sleep(random.randint(60*15, 60*30))  # sleep for 15-30min
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: continue")
                continue
