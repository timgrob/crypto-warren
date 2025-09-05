from enum import Enum, auto


class Trend(Enum):
    UP = auto()
    DOWN = auto()
    NONE = auto


class Side(Enum):
    BUY = auto()
    SELL = auto()
