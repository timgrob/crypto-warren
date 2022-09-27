from database.model import Trade
from database.database_connection import Session
from database.DatabaseConnector import DatabaseConnector


class PostgresDatabase(DatabaseConnector):

    def __init__(self, url: str):
        self.url = url

    def fetch_all_trades(self):
        session = Session()
        trades = session.query(Trade).all()
        return trades

    def persist_trade(self, trade: Trade):
        session = Session()
        session.add(Trade)
        return Trade

    def delete_trade(self, trade: Trade):
        session = Session()
        session.delete(Trade)
        return True

    def delete_trade_with_id(self, trade_id: int):
        session = Session()
        session.query(Trade).filter_by(id=trade_id).delete()
