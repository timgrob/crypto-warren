from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    symbols: list[str]
    timeframe: str
    leverage: int
    position_size: float
    stop_loss: float
    rate: str
    enable_trading: bool
