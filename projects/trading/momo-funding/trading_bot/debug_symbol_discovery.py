#!/usr/bin/env python3
"""Debug symbol discovery step by step."""

import requests

def debug_binance_symbols():
    """Debug exactly what's happening with symbol discovery."""
    print("🔧 DEBUGGING BINANCE SYMBOL DISCOVERY")
    
    try:
        # Step 1: Raw API call
        print("\n1. Testing raw API call...")
        response = requests.get("https://api.binance.com/api/v3/exchangeInfo", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            symbols = data.get("symbols", [])
            print(f"   Total symbols: {len(symbols)}")
            
            # Step 2: Check a few sample symbols
            print(f"\n2. Sample symbols:")
            for i, symbol in enumerate(symbols[:5]):
                print(f"   {symbol['symbol']}: {symbol['baseAsset']}/{symbol['quoteAsset']} - {symbol['status']}")
                print(f"      Permissions: {symbol.get('permissions', [])}")
            
            # Step 3: Filter for TRADING status
            trading_symbols = [s for s in symbols if s.get("status") == "TRADING"]
            print(f"\n3. Trading symbols: {len(trading_symbols)}")
            
            # Step 4: Filter for quote currencies
            quote_currencies = ["USDC", "USDC", "BUSD"]
            quote_filtered = [s for s in trading_symbols if s.get("quoteAsset") in quote_currencies]
            print(f"4. With USDC/USDC/BUSD: {len(quote_filtered)}")
            
            # Step 5: Filter for SPOT permissions
            spot_filtered = [s for s in quote_filtered if "SPOT" in s.get("permissions", [])]
            print(f"5. With SPOT permissions: {len(spot_filtered)}")
            
            if spot_filtered:
                print(f"\n✅ Sample SPOT trading pairs:")
                for symbol in spot_filtered[:10]:
                    print(f"   - {symbol['symbol']}: {symbol['baseAsset']}/{symbol['quoteAsset']}")
            
            return spot_filtered
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_ticker_data(symbols):
    """Test getting ticker data for discovered symbols."""
    if not symbols:
        print("\n❌ No symbols to test ticker data")
        return
        
    print(f"\n🔧 TESTING TICKER DATA...")
    
    try:
        # Get 24h ticker stats
        response = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        
        if response.status_code == 200:
            ticker_data = response.json()
            print(f"   Total ticker entries: {len(ticker_data)}")
            
            # Create symbol lookup
            symbol_names = [s["symbol"] for s in symbols[:20]]  # Test first 20
            ticker_lookup = {t["symbol"]: t for t in ticker_data}
            
            print(f"\n   Testing ticker data for sample symbols:")
            found_count = 0
            for symbol_name in symbol_names[:5]:
                if symbol_name in ticker_lookup:
                    ticker = ticker_lookup[symbol_name]
                    volume = float(ticker.get("quoteVolume", 0))
                    price = float(ticker.get("lastPrice", 0))
                    print(f"   ✅ {symbol_name}: ${price:.4f}, ${volume:,.0f} volume")
                    found_count += 1
                else:
                    print(f"   ❌ {symbol_name}: No ticker data")
            
            print(f"   Ticker data found for {found_count}/{len(symbol_names[:5])} symbols")
            
    except Exception as e:
        print(f"❌ Ticker test failed: {e}")

if __name__ == "__main__":
    symbols = debug_binance_symbols()
    test_ticker_data(symbols)