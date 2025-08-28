from abc import ABC, abstractmethod


class Strategy:
    def __init__(self):
        """Trading strategy that determines when to buy and when to sell"""

    @abstractmethod
    def buy_signal(self, token_data: dict) -> bool:
        """Buy signal of trading strategy"""

    @abstractmethod
    def sell_signal(self, token_data: dict) -> bool:
        """Sell signal of trading strategy"""