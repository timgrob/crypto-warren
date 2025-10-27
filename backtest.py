#!/usr/bin/env python3
"""
Backtest script for crypto-warren trading strategies.

This script fetches historical data and runs backtests using Backtrader.

Usage:
    python backtest.py --symbol SOL/USDC:USDC --days 90 --initial-cash 100 --plot
"""

import os
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.backtesting.data_fetcher import fetch_historical_data
from src.backtesting.backtest_runner import run_backtest
from src.backtesting.strategies import BacktraderEMASmoothingStrategy, BacktraderEMAStrategy
from loguru import logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Backtest crypto trading strategies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Data parameters
    parser.add_argument(
        "--symbol",
        type=str,
        default="SOL/USDC:USDC",
        help="Trading pair symbol (e.g., SOL/USDC:USDC, BTC/USDT:USDT)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default="1h",
        choices=["1m", "5m", "15m", "1h", "4h", "1d"],
        help="Candle timeframe",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days of historical data to fetch",
    )

    # Backtest parameters
    parser.add_argument(
        "--initial-cash",
        type=float,
        default=100.0,
        help="Initial capital in USDC",
    )
    parser.add_argument(
        "--commission",
        type=float,
        default=0.001,
        help="Trading commission (0.001 = 0.1%%)",
    )
    parser.add_argument(
        "--leverage",
        type=float,
        default=3.0,
        help="Leverage multiplier",
    )

    # Strategy parameters
    parser.add_argument(
        "--strategy",
        type=str,
        default="ema_smoothing",
        choices=["ema", "ema_smoothing"],
        help="Strategy to backtest",
    )
    parser.add_argument(
        "--ema-window",
        type=int,
        default=8,
        help="EMA window size",
    )
    parser.add_argument(
        "--smooth-window",
        type=int,
        default=12,
        help="Savitzky-Golay smoothing window (for ema_smoothing strategy)",
    )
    parser.add_argument(
        "--polyorder",
        type=int,
        default=5,
        help="Polynomial order for smoothing (for ema_smoothing strategy)",
    )
    parser.add_argument(
        "--atr-stop-loss",
        type=float,
        default=1.4,
        help="ATR multiplier for stop loss",
    )
    parser.add_argument(
        "--position-notional-value",
        type=float,
        default=10.0,
        help="Notional value per position in USDC",
    )

    # Output options
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot backtest results",
    )
    parser.add_argument(
        "--save-data",
        type=str,
        default=None,
        help="Save fetched data to CSV file",
    )
    parser.add_argument(
        "--load-data",
        type=str,
        default=None,
        help="Load data from CSV file instead of fetching",
    )

    return parser.parse_args()


async def main():
    """Main function to run backtest."""
    args = parse_args()

    logger.info("=" * 60)
    logger.info("CRYPTO WARREN - BACKTEST")
    logger.info("=" * 60)

    # Fetch or load historical data
    if args.load_data:
        logger.info(f"Loading data from {args.load_data}")
        import pandas as pd

        df = pd.read_csv(args.load_data)
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
    else:
        logger.info(f"Fetching {args.days} days of {args.timeframe} data for {args.symbol}...")
        df = await fetch_historical_data(
            symbol=args.symbol, timeframe=args.timeframe, days=args.days, exchange_id="binance"
        )

        # Save data if requested
        if args.save_data:
            df.to_csv(args.save_data, index=False)
            logger.info(f"Data saved to {args.save_data}")

    logger.info(f"Data loaded: {len(df)} candles from {df['datetime'].min()} to {df['datetime'].max()}")

    # Select strategy
    if args.strategy == "ema_smoothing":
        strategy_class = BacktraderEMASmoothingStrategy
        strategy_params = {
            "ema_window": args.ema_window,
            "smooth_window": args.smooth_window,
            "polyorder": args.polyorder,
            "atr_stop_loss": args.atr_stop_loss,
            "position_notional_value": args.position_notional_value,
            "leverage": args.leverage,
            "printlog": False,  # Disable verbose logging
        }
    else:  # ema
        strategy_class = BacktraderEMAStrategy
        strategy_params = {
            "ema_window": args.ema_window,
            "atr_stop_loss": args.atr_stop_loss,
            "position_notional_value": args.position_notional_value,
            "leverage": args.leverage,
            "printlog": False,
        }

    logger.info(f"Strategy: {args.strategy}")
    logger.info(f"Parameters: {strategy_params}")

    # Run backtest
    metrics = run_backtest(
        df=df,
        strategy_class=strategy_class,
        strategy_params=strategy_params,
        initial_cash=args.initial_cash,
        commission=args.commission,
        leverage=args.leverage,
        plot=args.plot,
    )

    logger.info("Backtest completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
