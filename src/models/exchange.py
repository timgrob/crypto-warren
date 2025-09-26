from dataclasses import dataclass
from enum import StrEnum
import ccxt


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    LIMIT = "limit"
    MARKET = "market"


class MarginMode(StrEnum):
    CROSS = "cross"
    ISOLATED = "isolated"


@dataclass(frozen=True)
class MinMax:
    min: float
    max: float


@dataclass(frozen=True)
class Limit:
    amount: MinMax
    price: MinMax
    cost: MinMax
    leverage: MinMax
    market: MinMax


@dataclass(frozen=True)
class Precision:
    amount: float
    price: float
    cost: float
    base: float
    quote: float


@dataclass(frozen=True)
class Market:
    symbol: str
    limit: Limit
    precision: Precision


@dataclass(frozen=True)
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float | None = None
    action: str | None = None
    id: int | None = None

    @property
    def long(self) -> bool:
        return self.side == "long"

    @property
    def short(self) -> bool:
        return self.side == "short"


class Exchange(ccxt.Exchange):
    async def close_position(self, position: Position, params=...):
        try:
            order = {
                "symbol": position.symbol,
                "type": OrderType.MARKET,
                "side": Side.SELL if position.long else Side.BUY,
                "amount": position.size,
                "params": params,
            }
            placed_order = await self.create_order(**order)
        except TimeoutError:
            self.logger.error(f"Position not close before timeout was reached")
        except Exception as e:
            self.logger.error(str(e))
