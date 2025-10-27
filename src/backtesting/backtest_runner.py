import backtrader as bt
import pandas as pd
from datetime import datetime
from loguru import logger
from typing import Optional, Dict, Any

from src.backtesting.strategies import BacktraderEMASmoothingStrategy, BacktraderEMAStrategy


class BacktestRunner:
    """
    Runner for backtesting trading strategies using Backtrader.
    """

    def __init__(
        self,
        initial_cash: float = 100.0,
        commission: float = 0.001,  # 0.1% commission
        leverage: float = 3.0,
    ):
        """
        Initialize the backtest runner.

        Args:
            initial_cash: Starting capital in USDC
            commission: Trading commission (0.001 = 0.1%)
            leverage: Leverage multiplier
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.leverage = leverage
        self.cerebro = None
        self.results = None

    def prepare_data(self, df: pd.DataFrame) -> bt.feeds.PandasData:
        """
        Prepare pandas DataFrame for Backtrader.

        Args:
            df: DataFrame with columns: datetime, open, high, low, close, volume

        Returns:
            Backtrader PandasData feed
        """
        # Ensure datetime column is datetime type and set as index
        if "datetime" in df.columns:
            df = df.set_index("datetime")
        elif "timestamp" in df.columns:
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("datetime")

        # Ensure required columns exist
        required_columns = ["open", "high", "low", "close", "volume"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Create Backtrader data feed
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # Use index
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            openinterest=-1,  # No open interest for crypto
        )

        return data

    def setup_cerebro(
        self,
        data: bt.feeds.PandasData,
        strategy_class: type = BacktraderEMASmoothingStrategy,
        strategy_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Setup Backtrader Cerebro engine with strategy and analyzers.

        Args:
            data: Backtrader data feed
            strategy_class: Strategy class to use
            strategy_params: Parameters to pass to the strategy
        """
        self.cerebro = bt.Cerebro()

        # Add data feed
        self.cerebro.adddata(data)

        # Add strategy with parameters
        if strategy_params:
            self.cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            self.cerebro.addstrategy(strategy_class)

        # Set initial cash
        self.cerebro.broker.setcash(self.initial_cash)

        # Set commission
        self.cerebro.broker.setcommission(commission=self.commission)

        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe", riskfreerate=0.0)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        self.cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")  # System Quality Number
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")

        logger.info(f"Cerebro setup complete - Initial Cash: ${self.initial_cash:.2f}")

    def run(self) -> Dict[str, Any]:
        """
        Run the backtest and return performance metrics.

        Returns:
            Dictionary containing performance metrics
        """
        if not self.cerebro:
            raise RuntimeError("Cerebro not setup. Call setup_cerebro() first.")

        logger.info("Starting backtest...")
        starting_value = self.cerebro.broker.getvalue()

        # Run backtest
        self.results = self.cerebro.run()
        strat = self.results[0]

        # Get final portfolio value
        ending_value = self.cerebro.broker.getvalue()
        total_return = ((ending_value - starting_value) / starting_value) * 100

        # Extract analyzer results
        sharpe_ratio = strat.analyzers.sharpe.get_analysis().get("sharperatio", None)
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        sqn = strat.analyzers.sqn.get_analysis().get("sqn", None)

        # Compile performance metrics
        metrics = {
            "starting_value": starting_value,
            "ending_value": ending_value,
            "total_return_pct": total_return,
            "total_return": ending_value - starting_value,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_pct": drawdown.get("max", {}).get("drawdown", 0),
            "max_drawdown_money": drawdown.get("max", {}).get("moneydown", 0),
            "sqn": sqn,
            "total_trades": trades.get("total", {}).get("total", 0),
            "won_trades": trades.get("won", {}).get("total", 0),
            "lost_trades": trades.get("lost", {}).get("total", 0),
            "win_rate_pct": (
                (trades.get("won", {}).get("total", 0) / trades.get("total", {}).get("total", 1)) * 100
                if trades.get("total", {}).get("total", 0) > 0
                else 0
            ),
            "avg_win": trades.get("won", {}).get("pnl", {}).get("average", 0),
            "avg_loss": trades.get("lost", {}).get("pnl", {}).get("average", 0),
            "largest_win": trades.get("won", {}).get("pnl", {}).get("max", 0),
            "largest_loss": trades.get("lost", {}).get("pnl", {}).get("max", 0),
        }

        logger.info("Backtest complete!")
        return metrics

    def plot(self, **kwargs):
        """
        Plot backtest results.

        Args:
            **kwargs: Additional arguments to pass to cerebro.plot()
        """
        if not self.cerebro:
            raise RuntimeError("No backtest results to plot. Run backtest first.")

        logger.info("Generating plot...")
        self.cerebro.plot(**kwargs)

    def print_performance(self, metrics: Dict[str, Any]):
        """
        Print performance metrics in a formatted way.

        Args:
            metrics: Dictionary of performance metrics
        """
        print("\n" + "=" * 60)
        print("BACKTEST PERFORMANCE REPORT")
        print("=" * 60)

        print("\n--- Portfolio Performance ---")
        print(f"Starting Value:        ${metrics['starting_value']:.2f}")
        print(f"Ending Value:          ${metrics['ending_value']:.2f}")
        print(f"Total Return:          ${metrics['total_return']:.2f} ({metrics['total_return_pct']:.2f}%)")
        print(f"Max Drawdown:          {metrics['max_drawdown_pct']:.2f}% (${metrics['max_drawdown_money']:.2f})")

        print("\n--- Risk Metrics ---")
        if metrics['sharpe_ratio']:
            print(f"Sharpe Ratio:          {metrics['sharpe_ratio']:.4f}")
        else:
            print("Sharpe Ratio:          N/A")

        if metrics['sqn']:
            print(f"SQN (Quality):         {metrics['sqn']:.2f}")
        else:
            print("SQN (Quality):         N/A")

        print("\n--- Trade Statistics ---")
        print(f"Total Trades:          {metrics['total_trades']}")
        print(f"Winning Trades:        {metrics['won_trades']}")
        print(f"Losing Trades:         {metrics['lost_trades']}")
        print(f"Win Rate:              {metrics['win_rate_pct']:.2f}%")

        if metrics['avg_win'] > 0:
            print(f"Average Win:           ${metrics['avg_win']:.2f}")
            print(f"Largest Win:           ${metrics['largest_win']:.2f}")

        if metrics['avg_loss'] < 0:
            print(f"Average Loss:          ${metrics['avg_loss']:.2f}")
            print(f"Largest Loss:          ${metrics['largest_loss']:.2f}")

        if metrics['avg_win'] > 0 and metrics['avg_loss'] < 0:
            profit_factor = abs(metrics['avg_win'] / metrics['avg_loss'])
            print(f"Profit Factor:         {profit_factor:.2f}")

        print("\n" + "=" * 60 + "\n")


def run_backtest(
    df: pd.DataFrame,
    strategy_class: type = BacktraderEMASmoothingStrategy,
    strategy_params: Optional[Dict[str, Any]] = None,
    initial_cash: float = 100.0,
    commission: float = 0.001,
    leverage: float = 3.0,
    plot: bool = False,
) -> Dict[str, Any]:
    """
    Convenience function to run a complete backtest.

    Args:
        df: DataFrame with OHLCV data
        strategy_class: Strategy class to use
        strategy_params: Strategy parameters
        initial_cash: Starting capital
        commission: Trading commission
        leverage: Leverage multiplier
        plot: Whether to plot results

    Returns:
        Dictionary of performance metrics
    """
    runner = BacktestRunner(initial_cash=initial_cash, commission=commission, leverage=leverage)

    # Prepare data
    data = runner.prepare_data(df)

    # Setup cerebro
    runner.setup_cerebro(data, strategy_class, strategy_params)

    # Run backtest
    metrics = runner.run()

    # Print performance
    runner.print_performance(metrics)

    # Plot if requested
    if plot:
        runner.plot()

    return metrics
