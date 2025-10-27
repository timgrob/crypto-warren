# Crypto Warren

A cryptocurrency trading bot with backtesting capabilities for automated trading on Binance.

## Features

- **Automated Trading**: Execute trades based on EMA trend-following strategies
- **Backtesting Framework**: Test strategies against historical data using Backtrader
- **Risk Management**: ATR-based trailing stop-losses and position sizing
- **Leveraged Trading**: Support for leveraged futures positions
- **Multiple Strategies**:
  - EMA Trend Strategy
  - EMA with Savitzky-Golay Smoothing (default)
- **Scheduled Execution**: Automated trading using APScheduler
- **Database Integration**: Track trades and performance using SQLAlchemy

## Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd crypto-warren

# Install dependencies using uv
uv sync

# Install with dev dependencies (required for backtesting visualization)
uv sync --all-groups
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your Binance API credentials to `.env`:
```bash
# Exchange API credentials
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret

# Set to "true" to use Binance Testnet (https://testnet.binancefuture.com)
# Set to "false" or remove for live trading
USE_TESTNET=false

# Database configuration (optional - defaults to SQLite)
POSTGRES_USER=database-user
POSTGRES_PASSWORD=database-password
POSTGRES_DB=database-name
POSTGRES_HOST=database-host
POSTGRES_PORT=database-port

# Database URL (for SQLite, use: sqlite:///${POSTGRES_DB}.db)
DB_URL=sqlite:///${POSTGRES_DB}.db
```

3. Configure your trading parameters in [src/configs/bot_config.yaml](src/configs/bot_config.yaml):
```yaml
symbols:
  - SOL/USDC:USDC
rate: "0 * * * *"  # Cron schedule (every hour)
timeframe: "1h"
leverage: 3
position_notional_value: 10.0
atr_stop_loss: 1.4
enable_trading: true
params:
  ema_window: 8
  smooth_window: 12
  polyorder: 5
```

### Running the Bot

```bash
python main.py
```

## Backtesting

Before trading with real money, **backtest your strategy** to evaluate its performance:

```bash
# Basic backtest with default parameters
python backtest.py

# Backtest with custom parameters
python backtest.py \
  --symbol SOL/USDC:USDC \
  --timeframe 1h \
  --days 90 \
  --initial-cash 100 \
  --plot

# Parameter optimization
python examples/parameter_optimization.py
```

For more backtest options, run `python backtest.py --help`.

## Project Structure

```
crypto-warren/
├── main.py                      # Main entry point for live trading
├── backtest.py                  # Backtesting script
├── check_balance.py             # Utility to check account balance
├── .env.example                 # Environment variables template
├── docker-compose.yaml          # Docker configuration
├── src/
│   ├── bots/
│   │   ├── __init__.py
│   │   ├── bot.py               # Base bot class
│   │   └── trading_bot.py       # Trading bot implementation
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── strategy.py          # Base strategy class
│   │   └── momentum_strategies.py  # EMA-based strategies
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py      # Historical data fetcher
│   │   ├── strategies.py        # Backtrader strategy adapters
│   │   ├── backtest_runner.py   # Backtest execution engine
│   │   └── visualizer.py        # Performance visualization
│   ├── configs/
│   │   ├── bot_config.yaml      # Bot configuration
│   │   └── strategy_config.yaml # Strategy configuration
│   ├── db/
│   │   └── database.py          # Database models
│   ├── executions/
│   │   ├── execution.py         # Bot executor
│   │   └── schedule.py          # Scheduling logic
│   └── models/
│       ├── config.py            # Configuration models
│       ├── exchange.py          # Exchange data models
│       └── trading.py           # Trading models
├── examples/
│   ├── __init__.py
│   ├── parameter_optimization.py  # Parameter optimization
│   └── compare_strategies.py    # Strategy comparison
└── tests/
    └── __init__.py              # Test suite
```

## Trading Strategy

### EMA Smoothing Strategy

The default strategy uses:
1. **EMA (Exponential Moving Average)** to track price trends
2. **Savitzky-Golay Filter** to smooth the EMA and reduce noise
3. **Trend Detection** by analyzing EMA gradient
4. **Position Management**:
   - Long positions when trend changes to UP
   - Short positions when trend changes to DOWN
   - Close positions when trend reverses
5. **Risk Management**:
   - ATR-based trailing stop-loss
   - Fixed position sizing

### Strategy Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ema_window` | 8 | EMA calculation period |
| `smooth_window` | 12 | Savitzky-Golay smoothing window |
| `polyorder` | 5 | Polynomial order for smoothing |
| `atr_stop_loss` | 1.4 | ATR multiplier for stop-loss |
| `position_notional_value` | 10.0 | Position size in USDC |
| `leverage` | 3 | Leverage multiplier |

## Utilities

### Check Balance

Check your Binance account balance:

```bash
python check_balance.py
```

## Safety Features

- **Testnet Support**: Set `USE_TESTNET=true` in `.env` to use Binance Testnet for safe testing
- **Paper Trading**: Set `enable_trading: false` in config to run in dry-run mode
- **Risk Limits**: Position sizing and stop-losses to limit downside
- **Error Handling**: Comprehensive error handling and logging
- **Database Tracking**: All trades logged to database

## Important Notes

⚠️ **Risk Warning**: Cryptocurrency trading carries significant risk. Never trade with money you cannot afford to lose.

- **Start Small**: Begin with small position sizes
- **Backtest First**: Always backtest strategies before live trading
- **Paper Trade**: Test with `enable_trading: false` first
- **Monitor Closely**: Watch your bot's performance regularly
- **Understand Fees**: Account for trading fees in your strategy
- **Manage Risk**: Use appropriate position sizing and stop-losses

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff check .
ruff format .
```

## Dependencies

- `ccxt`: Cryptocurrency exchange integration
- `backtrader`: Backtesting framework
- `pandas`: Data manipulation
- `ta`: Technical analysis indicators
- `scipy`: Signal processing (Savitzky-Golay filter)
- `sqlalchemy`: Database ORM
- `apscheduler`: Task scheduling
- `loguru`: Logging

## License

This project is for educational purposes. Use at your own risk.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.

---

**Disclaimer**: This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.
