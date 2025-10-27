#!/usr/bin/env python3
"""
Strategy comparison example for crypto-warren.

This script compares different strategies side-by-side on the same dataset.

Usage:
    python examples/compare_strategies.py
"""

import asyncio
import pandas as pd
from loguru import logger

from src.backtesting.data_fetcher import fetch_historical_data
from src.backtesting.backtest_runner import run_backtest
from src.backtesting.strategies import BacktraderEMASmoothingStrategy, BacktraderEMAStrategy


async def compare_strategies():
    """Compare EMA and EMA Smoothing strategies."""
    logger.info("=" * 80)
    logger.info("STRATEGY COMPARISON")
    logger.info("=" * 80)

    # Fetch historical data once
    logger.info("Fetching historical data...")
    df = await fetch_historical_data(
        symbol="SOL/USDC:USDC",
        timeframe="1h",
        days=90,
        exchange_id="binance"
    )
    logger.info(f"Fetched {len(df)} candles from {df['datetime'].min()} to {df['datetime'].max()}")

    # Common parameters
    initial_cash = 100.0
    commission = 0.001
    leverage = 3.0

    # Strategy configurations
    strategies = [
        {
            "name": "Simple EMA",
            "class": BacktraderEMAStrategy,
            "params": {
                "ema_window": 8,
                "atr_stop_loss": 1.4,
                "position_notional_value": 10.0,
                "leverage": leverage,
                "printlog": False,
            }
        },
        {
            "name": "EMA + Savitzky-Golay Smoothing",
            "class": BacktraderEMASmoothingStrategy,
            "params": {
                "ema_window": 8,
                "smooth_window": 12,
                "polyorder": 5,
                "atr_stop_loss": 1.4,
                "position_notional_value": 10.0,
                "leverage": leverage,
                "printlog": False,
            }
        },
        {
            "name": "EMA Smoothing (Conservative)",
            "class": BacktraderEMASmoothingStrategy,
            "params": {
                "ema_window": 12,
                "smooth_window": 16,
                "polyorder": 5,
                "atr_stop_loss": 2.0,  # Wider stop-loss
                "position_notional_value": 10.0,
                "leverage": leverage,
                "printlog": False,
            }
        },
        {
            "name": "EMA Smoothing (Aggressive)",
            "class": BacktraderEMASmoothingStrategy,
            "params": {
                "ema_window": 5,
                "smooth_window": 8,
                "polyorder": 3,
                "atr_stop_loss": 1.0,  # Tighter stop-loss
                "position_notional_value": 10.0,
                "leverage": leverage,
                "printlog": False,
            }
        },
    ]

    results = []

    # Run backtests
    for strategy_config in strategies:
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing: {strategy_config['name']}")
        logger.info(f"{'='*80}")

        try:
            metrics = run_backtest(
                df=df,
                strategy_class=strategy_config["class"],
                strategy_params=strategy_config["params"],
                initial_cash=initial_cash,
                commission=commission,
                leverage=leverage,
                plot=False,
            )

            # Store results with strategy name
            metrics["strategy_name"] = strategy_config["name"]
            results.append(metrics)

        except Exception as e:
            logger.error(f"Backtest failed for {strategy_config['name']}: {e}")
            continue

    # Create comparison DataFrame
    comparison_df = pd.DataFrame([
        {
            "Strategy": r["strategy_name"],
            "Return (%)": r["total_return_pct"],
            "Return ($)": r["total_return"],
            "Sharpe": r["sharpe_ratio"] if r["sharpe_ratio"] else 0,
            "Max DD (%)": r["max_drawdown_pct"],
            "Trades": r["total_trades"],
            "Win Rate (%)": r["win_rate_pct"],
            "SQN": r["sqn"] if r["sqn"] else 0,
        }
        for r in results
    ])

    # Print comparison table
    print("\n" + "=" * 120)
    print("STRATEGY COMPARISON RESULTS")
    print("=" * 120)
    print(comparison_df.to_string(index=False))
    print("=" * 120)

    # Highlight best performers
    print("\n--- Best Performers ---")
    print(f"Highest Return:      {comparison_df.loc[comparison_df['Return (%)'].idxmax(), 'Strategy']}")
    print(f"Best Sharpe Ratio:   {comparison_df.loc[comparison_df['Sharpe'].idxmax(), 'Strategy']}")
    print(f"Lowest Drawdown:     {comparison_df.loc[comparison_df['Max DD (%)'].idxmin(), 'Strategy']}")
    print(f"Best Win Rate:       {comparison_df.loc[comparison_df['Win Rate (%)'].idxmax(), 'Strategy']}")
    print(f"Best SQN:            {comparison_df.loc[comparison_df['SQN'].idxmax(), 'Strategy']}")

    # Calculate composite score
    # Normalize metrics and create weighted score
    comparison_df["Score"] = (
        (comparison_df["Return (%)"] / comparison_df["Return (%)"].max()) * 0.3 +
        (comparison_df["Sharpe"] / comparison_df["Sharpe"].max()) * 0.25 +
        ((comparison_df["Max DD (%)"].max() - comparison_df["Max DD (%)"]) / comparison_df["Max DD (%)"].max()) * 0.25 +
        (comparison_df["Win Rate (%)"] / comparison_df["Win Rate (%)"].max()) * 0.1 +
        (comparison_df["SQN"] / comparison_df["SQN"].max()) * 0.1
    )

    best_overall = comparison_df.loc[comparison_df["Score"].idxmax()]
    print(f"\nBest Overall (Composite Score): {best_overall['Strategy']}")
    print(f"  - Composite Score: {best_overall['Score']:.3f}")
    print(f"  - Return: {best_overall['Return (%)']:.2f}%")
    print(f"  - Sharpe: {best_overall['Sharpe']:.3f}")
    print(f"  - Max Drawdown: {best_overall['Max DD (%)']:.2f}%")

    # Save results
    output_file = "strategy_comparison_results.csv"
    comparison_df.to_csv(output_file, index=False)
    logger.info(f"\nResults saved to {output_file}")

    # Calculate buy-and-hold return for comparison
    buy_hold_return = ((df.iloc[-1]["close"] - df.iloc[0]["close"]) / df.iloc[0]["close"]) * 100
    print(f"\nBuy & Hold Return: {buy_hold_return:.2f}%")

    return comparison_df


if __name__ == "__main__":
    asyncio.run(compare_strategies())
