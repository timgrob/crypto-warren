from abc import ABC, abstractmethod
from exchanges import Exchange
from strategies.TradingStrategies import TradingStrategy


class TradingBot(ABC):
    """This is a blueprint for different trading bots"""

    def __init__(self, exchange: Exchange, trading_strategy: TradingStrategy) -> None:
        self.exchange = exchange
        self.trading_strategy = trading_strategy

    @abstractmethod
    def trade(self, token: str) -> None:
        """Implementation of the trading logic"""
