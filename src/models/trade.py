from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import UUID, Float, String, DateTime, func
from database.database_connection import engine
from uuid import uuid4, UUID as uuid_type
from datetime import datetime


Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    id: Mapped[uuid_type] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    size: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"<Trade(TimeStamp={self.timestamp}, symbol={self.symbol}, side={self.side}, size={self.size}, price={self.price})>"


