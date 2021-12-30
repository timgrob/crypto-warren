from Trade import Trade
from typing import Optional, Dict
from abc import ABC, abstractmethod


class TradingStrategy(ABC):
    """Trading strategy that determines how trading is done"""

    @abstractmethod
    def trading(self, token_data: Dict) -> Optional[Trade]:
        """Trade method of the trading strategy"""
