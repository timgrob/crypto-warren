import asyncio
import pandas as pd
from ta.volatility import AverageTrueRange
from loguru import logger

from src.bots.bot import Bot
from src.models.trading import Trend
from src.models.exchange import (
    MarginMode,
    Market,
    Limit,
    Precision,
    Position,
    Side,
    OrderType,
)


class TradingBot(Bot):
    def __init__(self, exchange, strategy):
        super().__init__(exchange, strategy)
        self.symbols = self.config.symbols
        self.leverage = self.config.leverage
        self.timeframe = self.config.timeframe
        self.atr_stop_loss = self.config.atr_stop_loss
        self.window = self.config.params["ema_window"]
        self.position_notional_value = self.config.position_notional_value
        self.params = self.config.params

        self.markets: dict[str, Market] = {}
        self.trends: dict[str, Trend] = {}
        self.margin_mode = MarginMode.CROSS

    async def on_start(self):
        logger.info(f"Trading symbols: {', '.join(self.symbols)}")
        logger.info(f"Trading at timeframe {self.timeframe}")
        logger.info(f"Leverage set to {self.leverage}x")
        logger.info(f"MarginType set to '{self.margin_mode}'")

        for symbol in self.symbols:
            # Set leverage and margin-mode
            try:
                await self.exchange.set_leverage(self.leverage, symbol)
                await self.exchange.set_margin_mode(self.margin_mode, symbol)
            except Exception as e:
                raise e

            # Find limits and precision for symbol
            limits = self.exchange.markets[symbol]["limits"]
            precisions = self.exchange.markets[symbol]["precision"]
            limit = Limit(**limits)
            precision = Precision(**precisions)
            market = Market(symbol, limit, precision)
            self.markets[symbol] = market
            self.trends[symbol] = Trend.NONE

        await self.exchange.load_markets()

        logger.info("Startup completed")

    async def on_stop(self):
        logger.info("Shutdown completed")

    async def trade(self):
        logger.info("Trading bot trades ...")

        orders_open: list[dict] = []
        orders_close: list[dict] = []
        open_positions: list[dict] = await self.exchange.fetch_positions()
        open_positions_lookup: dict[str, Position] = {}

        # Trading logic for all symbols
        for open_position in open_positions:
            symbol = open_position["symbol"]
            side = open_position["side"]
            size = open_position["contracts"]
            entry_price = open_position["entryPrice"]
            mark_price = open_position["markPrice"]
            position = Position(symbol, side, size, entry_price, mark_price)
            open_positions_lookup[symbol] = position

        for symbol in self.symbols:
            logger.info(f"Trade {symbol=}")

            # Fetch current market price
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                current_price = ticker["last"]
            except Exception as e:
                logger.error(f"Ticker could not be fetched: {str(e)}")
                raise e

            # Fetch OHLCV
            try:
                limit = 200
                ohlcv = await self.exchange.fetch_ohlcv(
                    symbol, self.timeframe, limit=limit
                )
            except Exception as e:
                logger.error(f"OHLCV data could not be fetched: {str(e)}")
                raise e

            # Turn OHLCV into Pandas dataframe
            cols = ["timestamp", "open", "high", "low", "close", "volume"]
            df_ohlcv = pd.DataFrame(ohlcv, columns=cols)
            df_ohlcv["datetime"] = pd.to_datetime(df_ohlcv["timestamp"], unit="ms")

            if position := open_positions_lookup.get(symbol):
                position_trend = Trend.UP if position.long else Trend.DOWN
                logger.info(f"Open position is long: {position.long}")
            else:
                position_trend = Trend.NONE
                logger.info("No open position")

            # Determine current market trend
            current_trend = self.strategy.current_trend(df_ohlcv)
            logger.info(f"Position trend: {position_trend}")
            logger.info(f"Market trend: {current_trend}")
            logger.info(f"Trend progression: {position_trend} -> {current_trend}")

            # No strong trend could be detected
            if current_trend == Trend.NONE:
                logger.info(f"Continue: No market trend detected: {current_trend}")
                continue

            # If no change in trend is occuring, don't do anything
            if current_trend == position_trend:
                logger.info("Continue: Position trend in line with market trend")
                continue

            side = Side.BUY if current_trend == Trend.UP else Side.SELL
            size = self.position_notional_value / current_price
            amount = self.exchange.amount_to_precision(symbol, size)

            # New order
            new_order = {
                "symbol": symbol,
                "type": OrderType.MARKET,
                "side": side,
                "amount": amount,
            }
            orders_open.append(new_order)

            atr_indicator = AverageTrueRange(
                df_ohlcv["high"], df_ohlcv["low"], df_ohlcv["close"]
            )
            atrs = atr_indicator.average_true_range()
            atrs_mean = atrs.tail(self.window).mean()
            stop_loss = self.atr_stop_loss * atrs_mean / current_price
            call_back_rate = min(max(round(stop_loss * 100, 1), 0.1), 10)

            # Trailing stop-loss order
            stop_loss_order = {
                "symbol": symbol,
                "type": OrderType.MARKET,
                "side": Side.SELL if side == Side.BUY else Side.BUY,
                "amount": amount,
                "params": {
                    "callbackRate": call_back_rate,  # respect Binance callback limits
                    "reduceOnly": True,
                },
            }
            orders_open.append(stop_loss_order)

            # Add order for position which needs to be closed
            if position:
                close_order = {
                    "symbol": position.symbol,
                    "type": OrderType.MARKET,
                    "side": Side.SELL if position.long else Side.BUY,
                    "amount": position.size,
                }
                orders_close.append(close_order)

        if self.config.enable_trading:
            async with asyncio.TaskGroup() as tg:
                for order in orders_close:
                    tg.create_task(self.exchange.create_order(**order))

                for order in orders_open:
                    tg.create_task(self.exchange.create_order(**order))
