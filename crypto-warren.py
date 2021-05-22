import random
import logging
import time
import ccxt
from datetime import datetime
from urllib.error import HTTPError
from os import environ


if __name__ == '__main__':

    while True:
        app_time = datetime.now()
        print('Running')
        time.sleep(3000)

    # logging.basicConfig(filename='logfile.log', level=logging.INFO)
    # print('{}: Start Program'.format(app_time.strftime('%Y-%m-%d %H:%M:%S')))
    # logging.info('{}: Start Program'.format(app_time.strftime('%Y-%m-%d %H:%M:%S')))
    #
    # # parameters
    # ticker = environ['ticker']
    # margin = float(environ['margin'])
    # api_key = environ['bitstamp-api-key']
    # secret = environ['bitstamp-secret']
    # time_out = int(environ['time-out'])
    # enable_rate_limit = bool(environ['enable-rate-limit'])
    #
    # print(type(margin))
    # print(type(enable_rate_limit))
    # print(type(api_key))
    # print(enable_rate_limit)
    #
    # # Get exchange
    # exchange = ccxt.bitstamp({
    #     'apiKey': api_key,
    #     'secret': secret,
    #     'timeout': time_out,
    #     'enableRateLimit': enable_rate_limit
    # })
    #
    # have_bought_in_the_last_24h = False
    # buy_time = None
    #
    # while True:
    #     print('hello Heroku')
    #
    #     try:
    #         # fetch current portfolio balance
    #         # TODO: Get portfolio value
    #
    #         # fetch current price
    #         current_ticker = exchange.fetch_ticker(ticker)
    #
    #         # check for price movement
    #         if current_ticker['bid'] >= current_ticker['low'] * (1 + margin) and have_bought_in_the_last_24h:
    #             sell_order = exchange.create_limit_sell_order(ticker, 10, current_ticker['bid'], {'type': 'limit'})
    #             have_bought_in_the_last_24h = False
    #
    #             logging.info('{}: {} {} - {} @ {}'.format(
    #                 sell_order['datetime'],
    #                 sell_order['side'],
    #                 sell_order['status'],
    #                 sell_order['amount'],
    #                 sell_order['price']))
    #
    #         elif current_ticker['ask'] <= current_ticker['high'] * (1 - margin) and not have_bought_in_the_last_24h:
    #             amount = 0.5 * exchange.fetch_balance()['total']['USDT'] / current_ticker['ask']
    #             if amount < 1:
    #                 logging.info('Insufficient fund')
    #             else:
    #                 buy_order = exchange.create_limit_buy_order(ticker, amount, current_ticker['ask'], {'type': 'limit'})
    #                 have_bought_in_the_last_24h = True
    #                 buy_time = datetime.strptime(buy_order['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    #
    #                 logging.info('{}: {} {} - {} @ {}'.format(
    #                     buy_order['datetime'],
    #                     buy_order['side'],
    #                     buy_order['status'],
    #                     buy_order['amount'],
    #                     buy_order['price']))
    #         else:
    #             time_delta = datetime.now() - app_time
    #             if time_delta.seconds >= 900:
    #                 logging.info('{}: Code running'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    #                 app_time = datetime.now()
    #
    #             time.sleep(random.randint(30, 120))
    #             continue
    #
    #     except HTTPError as e:
    #         logging.exception('Error Code: {} - Reason: {}'.format(e.code, e.reason))
    #     except Exception as e:
    #         logging.exception('Exception: {}'.format(e))
    #
    #     # Reset have_bought_in_the_last_24h to False if
    #     if have_bought_in_the_last_24h and buy_time is not None:
    #         time_delta = datetime.now() - buy_time
    #         have_bought_in_the_last_24h = False if time_delta.days >= 1 else have_bought_in_the_last_24h

    #    time.sleep(random.randint(30, 120))
