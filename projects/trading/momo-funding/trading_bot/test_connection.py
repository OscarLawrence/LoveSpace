#!/usr/bin/env python3
"""
Test Binance connection and account access.
"""

import sys
from pathlib import Path

# Add execution module to path
sys.path.insert(0, str(Path(__file__).parent))

from execution.binance_connector import create_binance_connector


def main():
    print("🔍 Testing Binance Connection")
    print("="*40)
    
    # Create connector
    connector = create_binance_connector()
    if not connector:
        print("❌ Failed to create Binance connector")
        return
    
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
        
        # Get current prices
        btc_price = connector.get_current_price("BTCUSDC")
        eth_price = connector.get_current_price("ETHUSDC")
        
        print(f"\n📊 Current Prices:")
        print(f"   BTC: ${btc_price:,.2f}" if btc_price else "   BTC: Price unavailable")
        print(f"   ETH: ${eth_price:,.2f}" if eth_price else "   ETH: Price unavailable")
        
        # Test market data
        print(f"\n📈 Testing Market Data:")
        klines = connector.get_kline_data("BTCUSDC", "1h", 5)
        if klines:
            latest = klines[-1]
            print(f"   ✅ Latest BTC data: ${latest['close']:,.2f}")
        else:
            print(f"   ❌ Failed to fetch market data")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()