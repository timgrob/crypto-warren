import asyncio
import pandas as pd
import ccxt.async_support as ccxt
from datetime import datetime, timedelta
from loguru import logger


class HistoricalDataFetcher:
    """Fetches historical OHLCV data from cryptocurrency exchanges."""

    def __init__(self, exchange_id: str = "binance", api_key: str = None, api_secret: str = None):
        """
        Initialize the data fetcher.

        Args:
            exchange_id: The exchange to fetch data from (default: binance)
            api_key: Optional API key for authenticated requests
            api_secret: Optional API secret for authenticated requests
        """
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = None

    async def __aenter__(self):
        """Async context manager entry."""
        if self.api_key and self.api_secret:
            self.exchange = getattr(ccxt, self.exchange_id)({
                "apiKey": self.api_key,
                "secret": self.api_secret
            })
        else:
            self.exchange = getattr(ccxt, self.exchange_id)()
        await self.exchange.load_markets()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.exchange:
            await self.exchange.close()

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: datetime = None,
        until: datetime = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a given symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'SOL/USDC:USDC')
            timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
            since: Start date for historical data
            until: End date for historical data
            limit: Number of candles per request (default: 1000)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume, datetime
        """
        if not self.exchange:
            raise RuntimeError("Exchange not initialized. Use async context manager.")

        # Convert datetime to milliseconds timestamp
        since_ts = int(since.timestamp() * 1000) if since else None
        until_ts = int(until.timestamp() * 1000) if until else None

        all_ohlcv = []
        current_since = since_ts

        logger.info(f"Fetching historical data for {symbol} from {since} to {until}")

        while True:
            try:
                ohlcv = await self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=current_since,
                    limit=limit
                )

                if not ohlcv:
                    break

                # Filter data up to 'until' timestamp
                if until_ts:
                    ohlcv = [candle for candle in ohlcv if candle[0] <= until_ts]

                all_ohlcv.extend(ohlcv)

                # Check if we've reached the end
                if len(ohlcv) < limit or (until_ts and ohlcv[-1][0] >= until_ts):
                    break

                # Update since to last timestamp + 1ms
                current_since = ohlcv[-1][0] + 1

                # Rate limiting
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Error fetching OHLCV data: {e}")
                raise

        # Convert to DataFrame
        if not all_ohlcv:
            raise ValueError(f"No data fetched for {symbol}")

        df = pd.DataFrame(all_ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.drop_duplicates(subset=["timestamp"]).reset_index(drop=True)

        logger.info(f"Fetched {len(df)} candles for {symbol}")

        return df

    async def fetch_recent_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        days: int = 30
    ) -> pd.DataFrame:
        """
        Fetch recent historical data for the last N days.

        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe
            days: Number of days to fetch (default: 30)

        Returns:
            DataFrame with OHLCV data
        """
        until = datetime.utcnow()
        since = until - timedelta(days=days)

        return await self.fetch_ohlcv(symbol, timeframe, since, until)


async def fetch_historical_data(
    symbol: str,
    timeframe: str = "1h",
    days: int = 30,
    exchange_id: str = "binance"
) -> pd.DataFrame:
    """
    Convenience function to fetch historical data without explicit context manager.

    Args:
        symbol: Trading pair symbol
        timeframe: Candle timeframe
        days: Number of days to fetch
        exchange_id: Exchange to use

    Returns:
        DataFrame with OHLCV data
    """
    async with HistoricalDataFetcher(exchange_id=exchange_id) as fetcher:
        return await fetcher.fetch_recent_data(symbol, timeframe, days)
