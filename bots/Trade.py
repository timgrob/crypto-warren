from datetime import datetime
from dataclasses import dataclass


@dataclass
class Trade:
    """Class for storing a single trade"""
    timestamp: datetime
    symbol: str
    qty: float
    price: float
