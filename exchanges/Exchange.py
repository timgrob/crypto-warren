from abc import ABC, abstractmethod
import json


class Exchange(ABC):
    """This is the blueprint for an exchange"""

    def __init__(self, api_key: str, secret: str, time_out: int = 3000, enable_rate_limit: bool = True):
        self.api_key = api_key
        self.secret = secret
        self.time_out = time_out
        self.enable_rate_limit = enable_rate_limit
        self.exchange = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to exchange"""
