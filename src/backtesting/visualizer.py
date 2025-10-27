"""
Visualization utilities for backtesting results.

This module provides custom plotting and reporting functions for backtest analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path


class BacktestVisualizer:
    """Visualizer for backtest results and performance metrics."""

    def __init__(self, figsize=(14, 10)):
        """
        Initialize the visualizer.

        Args:
            figsize: Figure size for plots (width, height)
        """
        self.figsize = figsize
        plt.style.use("seaborn-v0_8-darkgrid")

    def plot_equity_curve(
        self,
        dates: List,
        portfolio_values: List[float],
        trades: List[Dict[str, Any]] = None,
        benchmark_values: List[float] = None,
        save_path: str = None,
    ):
        """
        Plot equity curve with optional trade markers and benchmark.

        Args:
            dates: List of datetime objects
            portfolio_values: List of portfolio values over time
            trades: List of trade dictionaries with 'date', 'type', 'price'
            benchmark_values: List of benchmark values (e.g., buy-and-hold)
            save_path: Path to save the figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Plot equity curve
        ax.plot(dates, portfolio_values, label="Portfolio Value", linewidth=2, color="#2E86AB")

        # Plot benchmark if provided
        if benchmark_values:
            ax.plot(dates, benchmark_values, label="Buy & Hold", linewidth=2, color="#A23B72", alpha=0.7, linestyle="--")

        # Plot trade markers if provided
        if trades:
            buy_dates = [t["date"] for t in trades if t["type"] == "buy"]
            buy_values = [t["portfolio_value"] for t in trades if t["type"] == "buy"]
            sell_dates = [t["date"] for t in trades if t["type"] == "sell"]
            sell_values = [t["portfolio_value"] for t in trades if t["type"] == "sell"]

            if buy_dates:
                ax.scatter(buy_dates, buy_values, marker="^", color="green", s=100, alpha=0.7, label="Buy", zorder=5)

            if sell_dates:
                ax.scatter(sell_dates, sell_values, marker="v", color="red", s=100, alpha=0.7, label="Sell", zorder=5)

        # Formatting
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Portfolio Value ($)", fontsize=12)
        ax.set_title("Equity Curve", fontsize=16, fontweight="bold")
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Equity curve saved to {save_path}")

        plt.show()

    def plot_drawdown(
        self,
        dates: List,
        drawdowns: List[float],
        save_path: str = None,
    ):
        """
        Plot drawdown over time.

        Args:
            dates: List of datetime objects
            drawdowns: List of drawdown percentages
            save_path: Path to save the figure
        """
        fig, ax = plt.subplots(figsize=(14, 5))

        ax.fill_between(dates, drawdowns, 0, color="#E63946", alpha=0.5)
        ax.plot(dates, drawdowns, color="#E63946", linewidth=1.5)

        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Drawdown (%)", fontsize=12)
        ax.set_title("Drawdown Over Time", fontsize=16, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Drawdown plot saved to {save_path}")

        plt.show()

    def plot_returns_distribution(
        self,
        returns: List[float],
        save_path: str = None,
    ):
        """
        Plot distribution of trade returns.

        Args:
            returns: List of trade returns (percentage)
            save_path: Path to save the figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)

        # Histogram
        ax1.hist(returns, bins=30, color="#06A77D", alpha=0.7, edgecolor="black")
        ax1.axvline(x=0, color="red", linestyle="--", linewidth=2, label="Break-even")
        ax1.set_xlabel("Return (%)", fontsize=12)
        ax1.set_ylabel("Frequency", fontsize=12)
        ax1.set_title("Trade Returns Distribution", fontsize=14, fontweight="bold")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Box plot
        ax2.boxplot(returns, vert=True, patch_artist=True, boxprops=dict(facecolor="#06A77D", alpha=0.7))
        ax2.axhline(y=0, color="red", linestyle="--", linewidth=2)
        ax2.set_ylabel("Return (%)", fontsize=12)
        ax2.set_title("Returns Box Plot", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Returns distribution plot saved to {save_path}")

        plt.show()

    def plot_monthly_returns(
        self,
        dates: List,
        portfolio_values: List[float],
        save_path: str = None,
    ):
        """
        Plot monthly returns heatmap.

        Args:
            dates: List of datetime objects
            portfolio_values: List of portfolio values
            save_path: Path to save the figure
        """
        # Create DataFrame
        df = pd.DataFrame({"date": dates, "value": portfolio_values})
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        # Resample to monthly and calculate returns
        monthly = df.resample("M").last()
        monthly_returns = monthly.pct_change() * 100  # Percentage

        # Pivot for heatmap
        monthly_returns["year"] = monthly_returns.index.year
        monthly_returns["month"] = monthly_returns.index.month
        pivot = monthly_returns.pivot(index="year", columns="month", values="value")

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(12, 6))
        im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto", vmin=-10, vmax=10)

        # Set ticks
        ax.set_xticks(np.arange(12))
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        ax.set_yticklabels(pivot.index)

        # Annotate cells with values
        for i in range(len(pivot.index)):
            for j in range(12):
                value = pivot.values[i, j]
                if not np.isnan(value):
                    text = ax.text(j, i, f"{value:.1f}%", ha="center", va="center", color="black", fontsize=9)

        ax.set_title("Monthly Returns (%)", fontsize=16, fontweight="bold")
        plt.colorbar(im, ax=ax, label="Return (%)")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Monthly returns heatmap saved to {save_path}")

        plt.show()

    def create_performance_report(
        self,
        metrics: Dict[str, Any],
        save_path: str = None,
    ) -> str:
        """
        Create a detailed text performance report.

        Args:
            metrics: Dictionary of performance metrics
            save_path: Path to save the report as text file

        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 80,
            "BACKTEST PERFORMANCE REPORT",
            "=" * 80,
            "",
            "PORTFOLIO PERFORMANCE",
            "-" * 80,
            f"Starting Value:              ${metrics['starting_value']:>12,.2f}",
            f"Ending Value:                ${metrics['ending_value']:>12,.2f}",
            f"Total Return:                ${metrics['total_return']:>12,.2f}  ({metrics['total_return_pct']:>6.2f}%)",
            f"Max Drawdown:                {metrics['max_drawdown_pct']:>12.2f}%  (${metrics['max_drawdown_money']:>10,.2f})",
            "",
            "RISK METRICS",
            "-" * 80,
        ]

        if metrics["sharpe_ratio"] is not None:
            report_lines.append(f"Sharpe Ratio:                {metrics['sharpe_ratio']:>12.4f}")
        else:
            report_lines.append("Sharpe Ratio:                         N/A")

        if metrics["sqn"] is not None:
            report_lines.append(f"SQN (System Quality):        {metrics['sqn']:>12.2f}")
            # SQN interpretation
            if metrics["sqn"] >= 7.0:
                quality = "Superb"
            elif metrics["sqn"] >= 5.0:
                quality = "Excellent"
            elif metrics["sqn"] >= 3.0:
                quality = "Good"
            elif metrics["sqn"] >= 2.0:
                quality = "Average"
            elif metrics["sqn"] >= 1.0:
                quality = "Below Average"
            else:
                quality = "Poor"
            report_lines.append(f"SQN Quality Rating:          {quality:>20}")
        else:
            report_lines.append("SQN (System Quality):                 N/A")

        report_lines.extend(
            [
                "",
                "TRADE STATISTICS",
                "-" * 80,
                f"Total Trades:                {metrics['total_trades']:>12}",
                f"Winning Trades:              {metrics['won_trades']:>12}",
                f"Losing Trades:               {metrics['lost_trades']:>12}",
                f"Win Rate:                    {metrics['win_rate_pct']:>12.2f}%",
            ]
        )

        if metrics["avg_win"] > 0:
            report_lines.extend(
                [
                    f"Average Win:                 ${metrics['avg_win']:>12.2f}",
                    f"Largest Win:                 ${metrics['largest_win']:>12.2f}",
                ]
            )

        if metrics["avg_loss"] < 0:
            report_lines.extend(
                [
                    f"Average Loss:                ${metrics['avg_loss']:>12.2f}",
                    f"Largest Loss:                ${metrics['largest_loss']:>12.2f}",
                ]
            )

        if metrics["avg_win"] > 0 and metrics["avg_loss"] < 0:
            profit_factor = abs(metrics["avg_win"] / metrics["avg_loss"])
            report_lines.append(f"Profit Factor:               {profit_factor:>12.2f}")

        report_lines.extend(["", "=" * 80, ""])

        report = "\n".join(report_lines)

        if save_path:
            with open(save_path, "w") as f:
                f.write(report)
            print(f"Performance report saved to {save_path}")

        return report


def calculate_drawdown_series(portfolio_values: List[float]) -> List[float]:
    """
    Calculate drawdown series from portfolio values.

    Args:
        portfolio_values: List of portfolio values

    Returns:
        List of drawdown percentages
    """
    values = np.array(portfolio_values)
    running_max = np.maximum.accumulate(values)
    drawdown = ((values - running_max) / running_max) * 100
    return drawdown.tolist()
