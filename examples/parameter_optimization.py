#!/usr/bin/env python3
"""
Parameter optimization example for crypto-warren strategies.

This script runs multiple backtests with different parameter combinations
to find optimal settings for your strategy.

Usage:
    python examples/parameter_optimization.py
"""

import asyncio
import pandas as pd
from itertools import product
from loguru import logger

from src.backtesting.data_fetcher import fetch_historical_data
from src.backtesting.backtest_runner import run_backtest
from src.backtesting.strategies import BacktraderEMASmoothingStrategy


async def optimize_parameters():
    """Run parameter optimization for EMA Smoothing Strategy."""
    logger.info("=" * 80)
    logger.info("PARAMETER OPTIMIZATION")
    logger.info("=" * 80)

    # Fetch historical data once
    logger.info("Fetching historical data...")
    df = await fetch_historical_data(
        symbol="SOL/USDC:USDC",
        timeframe="1h",
        days=90,
        exchange_id="binance"
    )
    logger.info(f"Fetched {len(df)} candles")

    # Define parameter ranges to test
    ema_windows = [5, 8, 12, 20]
    smooth_windows = [8, 12, 16, 20]
    polyorders = [3, 5, 7]
    atr_multipliers = [1.0, 1.4, 2.0]

    # Generate all combinations
    param_combinations = list(product(ema_windows, smooth_windows, polyorders, atr_multipliers))

    # Filter invalid combinations (smooth_window must be > polyorder and > ema_window)
    valid_combinations = [
        (ema, smooth, poly, atr)
        for ema, smooth, poly, atr in param_combinations
        if smooth > poly and smooth > ema
    ]

    logger.info(f"Testing {len(valid_combinations)} parameter combinations...")

    results = []

    for i, (ema_window, smooth_window, polyorder, atr_stop_loss) in enumerate(valid_combinations, 1):
        logger.info(f"\n--- Test {i}/{len(valid_combinations)} ---")
        logger.info(
            f"Parameters: ema={ema_window}, smooth={smooth_window}, "
            f"poly={polyorder}, atr={atr_stop_loss}"
        )

        # Setup strategy parameters
        strategy_params = {
            "ema_window": ema_window,
            "smooth_window": smooth_window,
            "polyorder": polyorder,
            "atr_stop_loss": atr_stop_loss,
            "position_notional_value": 10.0,
            "leverage": 3.0,
            "printlog": False,  # Disable verbose logging
        }

        try:
            # Run backtest
            metrics = run_backtest(
                df=df,
                strategy_class=BacktraderEMASmoothingStrategy,
                strategy_params=strategy_params,
                initial_cash=100.0,
                commission=0.001,
                plot=False,
            )

            # Store results
            results.append({
                "ema_window": ema_window,
                "smooth_window": smooth_window,
                "polyorder": polyorder,
                "atr_stop_loss": atr_stop_loss,
                "total_return_pct": metrics["total_return_pct"],
                "sharpe_ratio": metrics["sharpe_ratio"] if metrics["sharpe_ratio"] else 0,
                "max_drawdown_pct": metrics["max_drawdown_pct"],
                "total_trades": metrics["total_trades"],
                "win_rate_pct": metrics["win_rate_pct"],
                "sqn": metrics["sqn"] if metrics["sqn"] else 0,
            })

            logger.info(
                f"Return: {metrics['total_return_pct']:.2f}%, "
                f"Sharpe: {metrics['sharpe_ratio']:.3f if metrics['sharpe_ratio'] else 'N/A'}, "
                f"Trades: {metrics['total_trades']}"
            )

        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            continue

    # Create results DataFrame
    results_df = pd.DataFrame(results)

    # Sort by different metrics
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)

    print("\n--- Top 10 by Total Return ---")
    top_return = results_df.nlargest(10, "total_return_pct")
    print(top_return.to_string(index=False))

    print("\n--- Top 10 by Sharpe Ratio ---")
    top_sharpe = results_df[results_df["sharpe_ratio"] > 0].nlargest(10, "sharpe_ratio")
    print(top_sharpe.to_string(index=False))

    print("\n--- Top 10 by SQN (System Quality) ---")
    top_sqn = results_df[results_df["sqn"] > 0].nlargest(10, "sqn")
    print(top_sqn.to_string(index=False))

    # Find balanced best performer
    # Score = return * sharpe - max_drawdown
    results_df["score"] = (
        results_df["total_return_pct"] * results_df["sharpe_ratio"] - results_df["max_drawdown_pct"]
    )
    best = results_df.nlargest(1, "score").iloc[0]

    print("\n--- Best Overall (Balanced Score) ---")
    print(f"EMA Window:          {best['ema_window']:.0f}")
    print(f"Smooth Window:       {best['smooth_window']:.0f}")
    print(f"Poly Order:          {best['polyorder']:.0f}")
    print(f"ATR Stop Loss:       {best['atr_stop_loss']:.2f}")
    print(f"Total Return:        {best['total_return_pct']:.2f}%")
    print(f"Sharpe Ratio:        {best['sharpe_ratio']:.3f}")
    print(f"Max Drawdown:        {best['max_drawdown_pct']:.2f}%")
    print(f"Win Rate:            {best['win_rate_pct']:.2f}%")
    print(f"Total Trades:        {best['total_trades']:.0f}")
    print(f"SQN:                 {best['sqn']:.2f}")

    # Save results to CSV
    output_file = "optimization_results.csv"
    results_df.to_csv(output_file, index=False)
    logger.info(f"\nResults saved to {output_file}")

    return results_df


if __name__ == "__main__":
    asyncio.run(optimize_parameters())
