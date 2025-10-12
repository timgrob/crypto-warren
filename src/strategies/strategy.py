from abc import ABC, abstractmethod
import pandas as pd

from models.trading import Trend
from models.config import Config


class Strategy(ABC):
    def __init__(self, config: Config):
        self.config = config

    def get_config(self) -> Config:
        return self.config

    @abstractmethod
    def buy_signal(self, ohlcv: pd.DataFrame) -> bool:
        """Check if sell signal occurs based on the OHLCV data"""

    @abstractmethod
    def sell_signal(self, ohlcv: pd.DataFrame) -> bool:
        """Check if buy signal occurs based on the OHLCV data"""

    @abstractmethod
    def current_trend(self, values: pd.Series) -> Trend:
        """Determine the current trend based on the OHLCV data"""
