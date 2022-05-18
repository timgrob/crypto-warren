from abc import ABC, abstractmethod
from bots.Trade import Trade


class DatabaseConnector(ABC):

    @abstractmethod
    def fetch_all_trades(self):
        """Fetch all trades that are saved in the database"""

    @abstractmethod
    def persist_trade(self, trade: Trade):
        """Persist one single trade"""

    @abstractmethod
    def delete_trade_with_id(self, id: int):
        """Delete a single trade"""
