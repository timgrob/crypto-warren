from sqlalchemy import Column, Integer, Float, String, Sequence, DateTime
from sqlalchemy.orm import declarative_base
from database.database_connection import engine

Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, Sequence('trades_id_seq'), primary_key=True)
    timestamp = Column(DateTime)
    symbol = Column(String)
    qty = Column(Float)
    price = Column(Float)

    def __repr__(self):
        return f"<Trade(TimeStamp={self.timestamp}, symbol={self.symbol}, quantity={self.qty}, price={self.price})>"


Base.metadata.create_all(engine)
