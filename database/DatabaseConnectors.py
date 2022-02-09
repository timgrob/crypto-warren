from strategies.Trade import Trade
from DatabaseConextManagers import postgres_manager
from DatabaseConnector import DatabaseConnector


class PostgresDatabase(DatabaseConnector):

    def __init__(self, url: str):
        self.url = url

    def fetch_all_trades(self):
        with postgres_manager(self.url) as cursor:
            cursor.execute('SELECT * FROM trades')
            trades = cursor.fetchall()
            return trades

    def persist_trade(self, trade: Trade):
        with postgres_manager(self.url) as cursor:
            insert_sql = """INSERT INTO trades(symbol, qty, price) VALUES(%s, %s, %s) RETURNING id;"""
            cursor.execute(insert_sql, (trade.symbol, trade.qty, trade.price))

    def delete_trade_with_id(self, id: int):
        with postgres_manager(self.url) as cursor:
            cursor.execute('DELETE FROM trades WHERE id = %s', id)
