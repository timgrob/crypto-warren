from Trade import Trade
from TradingStrategy import TradingStrategy


class VolatilityTradingStrategy(TradingStrategy):
    """Trading strategy that performs trades based on the volatility of the market"""

    def __init__(self):
        self.last_high = None
        self.last_low = None
        self.margin = 0.1

    def trading(self, token_data):
        if not self.last_high and not self.last_low:
            self.last_high = token_data['high']
            self.last_low = token_data['low']

        # TODO: implement the volatility trading
        if token_data['last'] >= (1 + self.margin) * self.last_low:
            sell_order = self.exchange.create_limit_sell_order(token_data[''], 10, token_data['bid'], {'type': 'limit'})
            self.last_low = token_data['bid']
            return Trade(sell_order['datetime'], sell_order['amount'], sell_order['price'])
        elif token_data['last'] <= (1 - self.margin) * self.last_high:
            buy_order = self.exchange.create_limit_buy_order(token_data[''], 10, token_data['ask'], {'type': 'limit'})
            self.last_high = buy_order['ask']
            return Trade(buy_order['datatime'], buy_order['amount'], buy_order['price'])
        else:
            return None
