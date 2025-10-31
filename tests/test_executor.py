import pandas as pd
from loguru import logger

from src.bots.trading_bot import TradingBot
from tests.mock_exchange import MockExchange


class TestExecutor:
    def __init__(self, trading_bot: TradingBot, ohlcv: pd.DataFrame):
        self.trading_bot = trading_bot
        self.ohlcv = ohlcv

    async def run(self):
        start_index = 1400
        end_index = len(self.ohlcv)
        limit = 200
        symbols = self.trading_bot.config.symbols
        for symbol in symbols:
            for i in range(start_index, end_index):
                logger.debug(f"Iteration {i} ...")
                ohlcv_sub = self.ohlcv.iloc[i - limit : i]
                exchange: MockExchange = self.trading_bot.exchange
                exchange.set_ohlcv(symbol, ohlcv_sub)
                await self.trading_bot.trade()
                logger.debug("Iteration done")
                logger.debug(" ")

        logger.debug("Backtesting finished")
