#!/usr/bin/env python3
"""
Simple script to check Binance account balance.
Displays balances for both Spot and Futures accounts.
"""

import os
import asyncio
import ccxt.async_support as ccxt
from dotenv import load_dotenv


async def check_balance():
    """Fetch and display Binance account balance."""

    # Load environment variables from .env file
    load_dotenv()

    API_KEY = os.getenv("API_KEY", "").strip()
    API_SECRET = os.getenv("API_SECRET", "").strip()
    USE_TESTNET = os.getenv("USE_TESTNET", "false").lower().strip() in ("true", "1", "yes")

    if not API_KEY or not API_SECRET:
        print("❌ Error: API_KEY and API_SECRET must be set in .env file")
        return

    # Configure exchange based on testnet or live
    exchange_config = {
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',  # Set default to futures since bot uses futures
        }
    }

    # Add testnet URLs if testnet mode is enabled
    if USE_TESTNET:
        print("🧪 TESTNET MODE ENABLED")
        # Manually configure testnet endpoints (sandbox mode is deprecated)
        exchange_config['options']['defaultType'] = 'future'
        exchange_config['hostname'] = 'testnet.binancefuture.com'
    else:
        print("💼 LIVE TRADING MODE")

    # Initialize Binance exchange
    exchange = ccxt.binance(exchange_config)

    # Override URLs after initialization for testnet
    if USE_TESTNET:
        exchange.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
        exchange.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
        exchange.urls['api']['fapiPrivateV2'] = 'https://testnet.binancefuture.com/fapi/v2'

    try:
        print("🔄 Connecting to Binance...")
        print("🔍 Validating API credentials...\n")

        # First, load markets (public endpoint - no auth needed)
        try:
            print("  → Loading market data...")
            if USE_TESTNET:
                print(f"  🔍 Using endpoint: {exchange.urls['api'].get('fapiPublic', 'N/A')}")
            # For testnet, skip load_markets as it might use authenticated endpoints
            if not USE_TESTNET:
                await exchange.load_markets()
            print("  ✅ Connection established")
        except Exception as e:
            print(f"  ⚠️  Market data loading issue: {str(e)}")
            if USE_TESTNET:
                print(f"  💡 Continuing anyway for testnet...")
            else:
                raise

        # Display Futures Balance FIRST (primary use case for this bot)
        print("\n" + "=" * 60)
        print("🚀 FUTURES WALLET (Primary)")
        print("=" * 60)

        futures_total_usd = 0
        has_futures_balance = False

        try:
            print("  → Fetching futures balance...")
            futures_balance = await exchange.fetch_balance({'type': 'future'})
            print("  ✅ Futures balance retrieved successfully\n")

            for currency, amount in futures_balance['total'].items():
                if amount > 0 and currency not in ['info', 'free', 'used', 'total']:
                    has_futures_balance = True
                    free = futures_balance['free'].get(currency, 0)
                    used = futures_balance['used'].get(currency, 0)

                    print(f"{currency}:")
                    print(f"  Total:  {amount:,.8f}")
                    print(f"  Free:   {free:,.8f}")
                    print(f"  Locked: {used:,.8f}")

                    if currency in ['USDT', 'USDC', 'USD']:
                        futures_total_usd += amount
                        print(f"  ≈ ${amount:,.2f} USD")
                    print()

            if not has_futures_balance:
                print("No assets in Futures wallet")
            else:
                print(f"{'─' * 60}")
                print(f"Total Futures Value: ≈ ${futures_total_usd:,.2f} USD")

            # Display open positions if any
            try:
                print("\n  → Fetching open positions...")
                positions = await exchange.fetch_positions()
                open_positions = [p for p in positions if float(p.get('contracts', 0)) != 0]
                print(f"  ✅ Found {len(open_positions)} open position(s)")

                if open_positions:
                    print("\n" + "=" * 60)
                    print("📈 OPEN POSITIONS")
                    print("=" * 60)

                    for pos in open_positions:
                        symbol = pos['symbol']
                        contracts = float(pos.get('contracts', 0))
                        side = pos.get('side', 'N/A')
                        entry_price = float(pos.get('entryPrice', 0))
                        mark_price = float(pos.get('markPrice', 0))
                        unrealized_pnl = float(pos.get('unrealizedPnl', 0))

                        print(f"\n{symbol}:")
                        print(f"  Side:           {side.upper()}")
                        print(f"  Contracts:      {contracts:,.4f}")
                        print(f"  Entry Price:    ${entry_price:,.4f}")
                        print(f"  Mark Price:     ${mark_price:,.4f}")
                        print(f"  Unrealized PnL: ${unrealized_pnl:,.2f}")
            except Exception as e:
                print(f"  ⚠️  Could not fetch positions: {str(e)}")

        except ccxt.AuthenticationError as e:
            print(f"  ❌ Futures Authentication Error: {str(e)}")
            print(f"  💡 Your API key may not have 'Enable Futures' permission")
            print(f"  💡 Check Binance → API Management → Enable Futures")
        except Exception as e:
            print(f"  ❌ Futures Error: {str(e)}")

        # Display Spot Balance (Secondary - optional)
        print("\n" + "=" * 60)
        print("📊 SPOT WALLET (Optional)")
        print("=" * 60)

        spot_total_usd = 0
        has_spot_balance = False

        try:
            print("  → Fetching spot balance...")
            balance = await exchange.fetch_balance({'type': 'spot'})
            print("  ✅ Spot balance retrieved successfully\n")

            for currency, amount in balance['total'].items():
                if amount > 0 and currency not in ['info', 'free', 'used', 'total']:
                    has_spot_balance = True
                    free = balance['free'].get(currency, 0)
                    used = balance['used'].get(currency, 0)

                    print(f"{currency}:")
                    print(f"  Total:  {amount:,.8f}")
                    print(f"  Free:   {free:,.8f}")
                    print(f"  Locked: {used:,.8f}")

                    # Try to get USD value
                    try:
                        if currency == 'USDT' or currency == 'USDC' or currency == 'USD':
                            spot_total_usd += amount
                        else:
                            ticker = await exchange.fetch_ticker(f"{currency}/USDT")
                            usd_value = amount * ticker['last']
                            spot_total_usd += usd_value
                            print(f"  ≈ ${usd_value:,.2f} USD")
                    except Exception:
                        # If we can't get the price, just skip the USD conversion
                        pass
                    print()

            if not has_spot_balance:
                print("No assets in Spot wallet")
            else:
                print(f"{'─' * 60}")
                print(f"Total Spot Value: ≈ ${spot_total_usd:,.2f} USD")

        except ccxt.AuthenticationError as e:
            print(f"  ❌ Spot Authentication Error: {str(e)}")
            print(f"  💡 Your API key may not have 'Enable Spot & Margin Trading' permission")
            print(f"  💡 This is optional - your bot only needs Futures access")
        except Exception as e:
            print(f"  ⚠️  Spot wallet not accessible: {str(e)}")
            print(f"  💡 This is optional - your bot only needs Futures access")

        # Grand total
        total_value = spot_total_usd + futures_total_usd
        print("\n" + "=" * 60)
        print(f"💰 TOTAL ACCOUNT VALUE: ≈ ${total_value:,.2f} USD")
        print("=" * 60)

    except ccxt.AuthenticationError as e:
        print(f"\n❌ Authentication Error: {str(e)}")
        print("\n🔍 Troubleshooting:")
        if USE_TESTNET:
            print("  1. Make sure your API keys are from https://testnet.binancefuture.com")
            print("  2. Testnet API keys are different from live Binance keys")
            print("  3. Enable 'Enable Reading' and 'Enable Futures' permissions")
            print("  4. No IP restrictions on testnet keys (or whitelist your IP)")
        else:
            print("  1. Check your API_KEY and API_SECRET in .env file")
            print("  2. Verify keys are from binance.com API Management")
            print("  3. Enable 'Enable Reading' and 'Enable Futures' permissions")
            print("  4. Check IP whitelist settings if enabled")
    except ccxt.NetworkError as e:
        print(f"❌ Network Error: {str(e)}")
        print("Please check your internet connection")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await exchange.close()


def main():
    """Entry point for the script."""
    asyncio.run(check_balance())


if __name__ == "__main__":
    main()
