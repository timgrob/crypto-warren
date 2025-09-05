from dataclasses import dataclass
from enum import StrEnum


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
    base: float
    quote: float


@dataclass(frozen=True)
class Market:
    symbol: str
    limit: Limit
    precision: Precision


class MarginMode(StrEnum):
    CROSS = "cross"
    ISOLATED = "isolated"
