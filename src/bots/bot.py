from abc import ABC, abstractmethod
from ccxt import Exchange

from src.strategies.strategy import Strategy


class Bot(ABC):
    def __init__(self, exchange: Exchange, strategy: Strategy) -> None:
        self.exchange = exchange
        self.strategy = strategy
        self.config = strategy.get_config()

    @abstractmethod
    async def on_start(self) -> None:
        """method will be called at startup"""

    @abstractmethod
    async def on_stop(self) -> None:
        """method will be called on shutdown"""

    @abstractmethod
    async def trade(self) -> None:
        """method will be called at time interval"""
