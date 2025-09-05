import pandas as pd
from loguru import logger
from ccxt import Exchange

from src.strategies.trading_strategies import Strategy
from src.models.config import Config
from src.models.trading import Trend
from src.models.exchange import MarginMode, Market, Limit, Precision


class TradingBot:
    def __init__(self, exchange: Exchange, strategy: Strategy, config: Config) -> None:
        self.exchange = exchange
        self.strategy = strategy
        self.config = config
        self.markets: dict[str, Market] = {}
        self.trends: dict[str, Trend] = {}
        self.margin_mode = MarginMode.CROSS

        # Unpack config params
        self.symbols = config.symbols
        self.leverage = config.leverage
        self.timeframe = config.timeframe.lower()
        self.stop_loss = config.stop_loss

    async def on_start(self) -> None:
        logger.info(f"Trading symbols: {', '.join(self.symbols)}")
        logger.info(f"Trading at timeframe {self.timeframe}")
        logger.info(f"Leverage set to {self.leverage}x")
        logger.info(f"MarginType set to '{self.margin_mode}'")

        # for symbol in self.symbols:
        #     # Set leverage and margin-mode
        #     try:
        #         await self.exchange.set_leverage(self.leverage, symbol)
        #         await self.exchange.set_margin_mode(self.margin_mode, symbol)
        #     except Exception as e:
        #         raise e

        #     limits = self.exchange.markets[symbol]["limnits"]
        #     precisions = self.exchange.markets[symbol]["precision"]
        #     limit = Limit(**limits)
        #     precision = Precision(**precisions)
        #     market = Market(symbol, limit, precision)
        #     self.markets[symbol] = market
        #     self.trends[symbol] = Trend.NONE

        logger.info("Startup completed")

    async def on_stop(self) -> None:
        logger.info("Shutdown completed")

    async def trade(self) -> None:
        logger.info("Trading bot trades ...")

        # for symbol in self.symbols:
        #     logger.info(f"Trade {symbol=}")
        #     timeframe = self.config.timeframe

        #     try:
        #         logger.error(f"Fetch OHLCV for {symbol=}")
        #         ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)
        #     except Exception as e:
        #         logger.error(f"OHLCV data could not be fetched for {symbol=}: {e}")

        #     columns = ["timestamp", "open", "high", "low", "close", "volume"]
        #     df_ohlcv = pd.DataFrame(ohlcv, columns=columns)
        #     df_ohlcv["datetime"] = pd.to_datetime(df_ohlcv["timestamp"], unit="ms")

        #     if self.strategy.buy_signal():
        #         pass

        #     if self.strategy.sell_signal():
        #         pass

        if self.config.enable_trading:
            logger.info("Trading is enabled")
