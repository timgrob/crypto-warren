from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    symbols: list[str]
    rate: str
    timeframe: str
    leverage: int
    position_notional_value: float
    stop_loss: float
    enable_trading: bool
    params: dict
