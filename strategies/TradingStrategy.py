from typing import Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass


class TradingStrategy(ABC):
    """Trading strategy that determines how trading is done"""

    @abstractmethod
    def buy_signal(self, token_data: Dict) -> bool:
        """Buy signal of trading strategy"""

    @abstractmethod
    def sell_signal(self, token_data: Dict) -> bool:
        """Sell signal of trading strategy"""


@dataclass
class VolatilityTradingStrategy(TradingStrategy):
    margin: float = 0.1
    bounce_back: float = 1

    def buy_signal(self, token_data: Dict) -> bool:
        return token_data['ask'] <= (1 - self.margin) * token_data['high']

    def sell_signal(self, token_data: Dict) -> bool:
        return token_data['bid'] >= (1 + (self.margin * self.bounce_back)) * token_data['low']


@dataclass
class MinMaxTradingStrategy(TradingStrategy):
    min_price: float
    max_price: float

    def buy_signal(self, token_data: Dict) -> bool:
        return token_data['ask'] >= self.max_price

    def sell_signal(self, token_data: Dict) -> bool:
        return token_data['bid'] <= self.min_price
