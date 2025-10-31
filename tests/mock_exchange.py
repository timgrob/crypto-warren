from dataclasses import dataclass, field, asdict
from collections import defaultdict
from datetime import datetime
from loguru import logger
import pandas as pd

from src.models.exchange import OrderType, Side


@dataclass
class TestOrder:
    symbol: str
    type: str
    side: str
    amount: float
    price: float | None = None
    params: dict = field(default_factory=dict)
    timestamp: datetime | None = None
    filled: bool = False


@dataclass
class TestPosition:
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float
    exit_price: float | None = None


class MockExchange:
    def __init__(self):
        self.positions: dict[str, TestPosition] = {}
        self.open_orders: dict[str, list[TestOrder]] = defaultdict(list)
        self.ohlcv_map: dict[str, pd.DataFrame] = {}

        # Track history
        self.trade_history: list[TestPosition] = []
        # self.position_history: list[dict] = []
        # self.equity_history: list[dict] = []

    def set_ohlcv(self, symbol: str, ohlcv_data: pd.DataFrame):
        self.ohlcv_map[symbol] = ohlcv_data

    def current_price(self, symbol: str, col="close") -> float:
        ohlcv = self.ohlcv_map.get(symbol)
        if ohlcv is None:
            raise ValueError(f"No OHLCV data for {symbol}")

        return ohlcv[col].iloc[-1]

    async def load_markets(self):
        logger.info("Load markets")
        pass

    async def set_leverage(self, leverage: int, symbol: str):
        logger.info(f"Backtest: Set leverage {leverage}x for {symbol}")

    async def set_margin_mode(self, margin_mode, symbol: str):
        logger.info(f"Backtest: Set margin mode {margin_mode} for {symbol}")

    async def fetch_ticker(self, symbol: str) -> dict:
        price = self.current_price(symbol)
        return {"symbol": symbol, "last": price}

    async def fetch_positions(self) -> list[dict]:
        return [
            {
                "symbol": symbol,
                "side": pos.side,
                "contracts": pos.size,
                "entryPrice": pos.entry_price,
                "markPrice": pos.mark_price,
            }
            for symbol, pos in self.positions.items()
        ]

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 200) -> list:
        df_ohlcv = self.ohlcv_map.get(symbol)
        if df_ohlcv is None:
            raise ValueError(f"No OHLCV data for {symbol}")

        ohlcv = df_ohlcv.reset_index(drop=True)
        return ohlcv[
            ["timestamp", "open", "high", "low", "close", "volume"]
        ].values.tolist()

    def amount_to_precision(self, symbol: str, amount: float) -> float:
        return round(amount, 3)

    async def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: dict | None = None,
    ) -> dict:
        params = params or {}

        # Check if this is a stop loss order
        if params.get("reduceOnly"):
            order = TestOrder(
                symbol=symbol,
                type=type,
                side=side,
                amount=amount,
                price=price,
                filled=False,
                params=params,
            )
            self.open_orders[symbol].append(order)
            logger.debug(
                f"Created {side} trailing stop order {amount} @ {price} for {symbol}"
            )
        else:
            if position := self.positions.get(symbol):
                if position.size != amount:
                    logger.error("Position has not the same amount to close.")
                    return {}

                position.exit_price = self.current_price(symbol)
                self.trade_history.append(position)
                del self.positions[symbol]  # delete positions as if it got executed
                logger.debug(
                    f"Close {position.side} position {position.size} @ {position.exit_price} for {symbol}"
                )
            else:
                current_price = self.current_price(symbol)
                pos_side = "long" if side == "buy" else "short"
                position = TestPosition(
                    symbol=symbol,
                    side=pos_side,
                    size=amount,
                    entry_price=current_price,
                    mark_price=current_price,
                )
                self.positions[symbol] = position
                logger.debug(
                    f"Created {pos_side} position {amount} @ {current_price} for {symbol}"
                )

        return {"id": f"stop_{symbol}", "info": {}}

    async def cancel_all_orders(self, symbol: str):
        if orders := self.open_orders.get(symbol):
            count = len(orders)
            self.open_orders[symbol] = []
            logger.debug(f"Cancelled {count} orders for {symbol}")

    # def _calculate_pnl(self, position: TestPosition, exit_price: float) -> float:
    #     """Calculate PnL for a position"""
    #     price_diff = exit_price - position.entry_price
    #     multiplier = 1 if position.side == "long" else -1
    #     return price_diff * position.size * multiplier

    # def _is_closing_order(self, position: TestPosition, order_side: str) -> bool:
    #     """Check if order closes the position"""
    #     return (position.side == "long" and order_side == Side.SELL) or (
    #         position.side == "short" and order_side == Side.BUY
    #     )

    # async def _execute_order(self, order: TestOrder, execution_price: float):
    #     """Execute an order at given price"""
    #     symbol = order.symbol

    #     # Check if closing existing position
    #     if (pos := self.positions.get(symbol)) and self._is_closing_order(
    #         pos, order.side
    #     ):
    #         pnl = self._calculate_pnl(pos, execution_price)
    #         self.balance += pnl

    #         # Record trade
    #         self.trade_history.append(
    #             {
    #                 "symbol": symbol,
    #                 "side": pos.side,
    #                 "entry_price": pos.entry_price,
    #                 "exit_price": execution_price,
    #                 "size": pos.size,
    #                 "pnl": pnl,
    #                 "pnl_pct": (pnl / (pos.entry_price * pos.size)) * 100,
    #             }
    #         )

    #         logger.info(
    #             f"Backtest: Closed {pos.side} position on {symbol} - PnL: ${pnl:.2f}"
    #         )
    #         del self.positions[symbol]
    #         return

    #     # Opening new position
    #     side_str = "long" if order.side == Side.BUY else "short"
    #     self.positions[symbol] = TestPosition(
    #         symbol=symbol,
    #         side=side_str,
    #         size=order.amount,
    #         entry_price=execution_price,
    #         entry_time=self.current_timestamp,
    #         stop_loss_callback_rate=order.params.get("callbackRate"),
    #         highest_price=execution_price if side_str == "long" else None,
    #         lowest_price=execution_price if side_str == "short" else None,
    #     )

    #     logger.info(
    #         f"Backtest: Opened {side_str} position on {symbol} at ${execution_price:.2f}"
    #     )
    #     order.filled = True

    # def _check_trailing_stop(self, symbol: str, position: TestPosition, price: float):
    #     """Check and trigger trailing stop loss if needed"""
    #     if not position.stop_loss_callback_rate:
    #         return

    #     if position.side == "long":
    #         position.highest_price = max(position.highest_price or price, price)
    #         trigger_price = position.highest_price * (
    #             1 - position.stop_loss_callback_rate / 100
    #         )

    #         if price <= trigger_price:
    #             logger.info(
    #                 f"Backtest: Trailing stop triggered for {symbol} at ${price:.2f}"
    #             )
    #             asyncio.create_task(self._execute_stop_loss(symbol, price))

    #     else:  # short position
    #         position.lowest_price = min(position.lowest_price or price, price)
    #         trigger_price = position.lowest_price * (
    #             1 + position.stop_loss_callback_rate / 100
    #         )

    #         if price >= trigger_price:
    #             logger.info(
    #                 f"Backtest: Trailing stop triggered for {symbol} at ${price:.2f}"
    #             )
    #             asyncio.create_task(self._execute_stop_loss(symbol, price))

    # def update_prices(self, symbol: str, price: float, timestamp: datetime):
    #     """Update current price and check stop losses"""
    #     self.current_prices[symbol] = price
    #     self.current_timestamp = timestamp

    #     # Check trailing stop losses
    #     if pos := self.positions.get(symbol):
    #         self._check_trailing_stop(symbol, pos, price)

    #     # Record equity
    #     self.equity_history.append(
    #         {
    #             "timestamp": timestamp,
    #             "balance": self.balance,
    #             "equity": self.calculate_equity(),
    #         }
    #     )

    # async def _execute_stop_loss(self, symbol: str, price: float):
    #     """Execute stop loss order"""
    #     if not (pos := self.positions.get(symbol)):
    #         return

    #     side = Side.SELL if pos.side == "long" else Side.BUY
    #     order = TestOrder(
    #         symbol=symbol,
    #         type=OrderType.MARKET,
    #         side=side,
    #         amount=pos.size,
    #         timestamp=self.current_timestamp,
    #     )

    #     await self._execute_order(order, price)
    #     await self.cancel_all_orders(symbol)

    # def calculate_equity(self) -> float:
    #     """Calculate total equity including unrealized PnL"""
    #     return self.balance + sum(
    #         self._calculate_unrealized_pnl(pos) for pos in self.positions.values()
    #     )

    # def _calculate_unrealized_pnl(self, position: TestPosition) -> float:
    #     """Calculate unrealized PnL for a position"""
    #     current_price = self.current_prices.get(position.symbol, position.entry_price)
    #     return self._calculate_pnl(position, current_price)
