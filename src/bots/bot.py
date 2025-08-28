import asyncio
from loguru import logger
from ccxt import Exchange
from src.strategies.strategy import Strategy
from src.models.config import Config


class TradingBot:
    def __init__(self, exchange: Exchange, strategy: Strategy, config: Config) -> None:
        self.exchange = exchange
        self.strategy = strategy
        self.config = config

    async def run(self) -> None:
        """Run the trading bot"""
        while True:
            logger.info("Bot is running")
            self.exchange.creat

            if self.config.enable_trading:
                logger.info("Trading is enabled")

            await self.strategy.execute(self.exchange)
            await asyncio.sleep(self.config.rate)