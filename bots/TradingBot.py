from abc import ABC, abstractmethod
from exchanges import Exchange


class TradingBot(ABC):
    """This is a blueprint for different trading bots"""

    def __init__(self, exchange: Exchange) -> None:
        self.exchange = exchange

    @abstractmethod
    def trade(self, token: str) -> None:
        """Implementation of the trading logic"""
