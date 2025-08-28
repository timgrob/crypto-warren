from dataclasses import dataclass


@dataclass
class Config:
    symbols: list[str]
    enable_trading: bool
    rate: str
    
