#!/usr/bin/env python3
"""
Check Binance account status and balances.
"""

import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add trading_system to path
sys.path.insert(0, str(Path(__file__).parent / "trading_system"))

from trading_system.binance_connector import create_binance_connector


def main():
    print("🔍 Checking Binance Account Status")
    print("="*40)
    
    connector = create_binance_connector()
    if not connector:
        print("❌ Failed to connect to Binance")
        return
    
    print("✅ Connected to Binance")
    
    # Get account info
    try:
        balances = connector.get_account_info()
        
        print(f"\n💰 Account Balances:")
        if balances:
            for asset, balance in balances.items():
                if balance.total > 0:
                    print(f"   {asset}: {balance.total:.8f} (Free: {balance.free:.8f}, Locked: {balance.locked:.8f})")
        else:
            print("   No balances found")
        
        # Get current prices for reference
        btc_price = connector.get_current_price("BTCUSDC")
        eth_price = connector.get_current_price("ETHUSDC")
        
        print(f"\n📊 Current Prices:")
        print(f"   BTC: ${btc_price:,.2f}" if btc_price else "   BTC: Price unavailable")
        print(f"   ETH: ${eth_price:,.2f}" if eth_price else "   ETH: Price unavailable")
        
        # Test market data fetch
        print(f"\n📈 Testing Market Data Access:")
        klines = connector.get_kline_data("BTCUSDC", "1h", 5)
        if klines:
            latest = klines[-1]
            print(f"   ✅ Latest BTC data: ${latest['close']:,.2f} at {latest['close_time']}")
        else:
            print(f"   ❌ Failed to fetch market data")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()