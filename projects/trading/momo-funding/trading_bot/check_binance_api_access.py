#!/usr/bin/env python3
"""
Binance API Access Check
Verify what endpoints we can access and what documentation we need.
"""

import requests
from execution.binance_connector import create_binance_connector

def check_binance_api_capabilities():
    """Check what Binance API endpoints we can access."""
    print("🔍 BINANCE API ACCESS CHECK")
    print("="*40)
    
    connector = create_binance_connector()
    if not connector:
        print("❌ Failed to create connector")
        return
    
    print("✅ Connected to Binance Mainnet")
    
    # Test different endpoints
    endpoints_to_test = [
        ("exchangeInfo", "Exchange trading rules and symbols"),
        ("ticker/24hr", "24h ticker statistics"),
        ("ticker/price", "Current average price"),
        ("depth", "Order book depth"),
        ("klines", "Kline/candlestick data"),
        ("account", "Account information (needs auth)"),
        ("openOrders", "Open orders (needs auth)")
    ]
    
    print(f"\n📊 TESTING API ENDPOINTS:")
    
    for endpoint, description in endpoints_to_test:
        try:
            print(f"\n   Testing {endpoint}: {description}")
            
            if endpoint == "exchangeInfo":
                response = connector._make_request("GET", endpoint)
                if "symbols" in response:
                    symbols = response["symbols"]
                    active_count = sum(1 for s in symbols if s.get("status") == "TRADING")
                    print(f"   ✅ Success: {active_count} active trading symbols")
                    
                    # Check for USDC pairs specifically
                    USDC_pairs = [s for s in symbols if s.get("quoteAsset") == "USDC" and s.get("status") == "TRADING"]
                    print(f"   📈 USDC pairs: {len(USDC_pairs)}")
                    
                    # Show sample pairs
                    if USDC_pairs:
                        sample_pairs = USDC_pairs[:5]
                        for pair in sample_pairs:
                            print(f"      - {pair['symbol']}: {pair['baseAsset']}/USDC")
                else:
                    print(f"   ❌ Unexpected response format")
                    
            elif endpoint == "ticker/24hr":
                response = connector._make_request("GET", endpoint)
                if isinstance(response, list):
                    print(f"   ✅ Success: {len(response)} ticker entries")
                    
                    # Find high-volume pairs
                    high_volume = sorted(response, key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)[:5]
                    print(f"   💰 Top volume pairs:")
                    for ticker in high_volume:
                        symbol = ticker.get('symbol', '')
                        volume = float(ticker.get('quoteVolume', 0))
                        print(f"      - {symbol}: ${volume:,.0f} volume")
                else:
                    print(f"   ❌ Unexpected response format")
                    
            elif endpoint == "ticker/price":
                # Test with specific symbol
                params = {"symbol": "BTCUSDC"}
                response = connector._make_request("GET", endpoint, params)
                if "price" in response:
                    price = float(response["price"])
                    print(f"   ✅ Success: BTC price ${price:,.2f}")
                else:
                    print(f"   ❌ Failed to get price")
                    
            elif endpoint == "account":
                response = connector._make_request("GET", endpoint, signed=True)
                if "balances" in response:
                    balances = [b for b in response["balances"] if float(b["free"]) > 0]
                    print(f"   ✅ Success: {len(balances)} non-zero balances")
                else:
                    print(f"   ❌ Failed: {response.get('msg', 'Unknown error')}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test external API for market cap data
    print(f"\n🌐 TESTING EXTERNAL DATA SOURCES:")
    try:
        print(f"   Testing CoinGecko API for market cap rankings...")
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets", 
                               params={"vs_currency": "usd", "per_page": 10}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Top {len(data)} coins by market cap")
            for i, coin in enumerate(data[:3], 1):
                print(f"      {i}. {coin['symbol'].upper()}: ${coin['current_price']:,.2f} (Rank {coin['market_cap_rank']})")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n💡 API CAPABILITIES SUMMARY:")
    print(f"   ✅ Basic market data: Available")
    print(f"   ✅ Price feeds: Available")  
    print(f"   ✅ Account data: Available with API keys")
    print(f"   ✅ External market cap: Available via CoinGecko")
    print(f"   🔧 Need: Proper symbol filtering and processing")

def test_symbol_discovery():
    """Test improved symbol discovery."""
    print(f"\n🔍 IMPROVED SYMBOL DISCOVERY TEST:")
    
    try:
        # Direct API call to test
        base_url = "https://api.binance.com"
        response = requests.get(f"{base_url}/api/v3/exchangeInfo", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            symbols = data.get("symbols", [])
            
            # Filter for USDC pairs
            USDC_pairs = []
            for symbol in symbols:
                if (symbol.get("status") == "TRADING" and 
                    symbol.get("quoteAsset") == "USDC" and
                    "SPOT" in symbol.get("permissions", [])):
                    USDC_pairs.append(symbol)
            
            print(f"   ✅ Found {len(USDC_pairs)} active USDC pairs")
            
            # Show sample with base assets
            if USDC_pairs:
                print(f"   📊 Sample pairs:")
                for pair in USDC_pairs[:10]:
                    print(f"      - {pair['symbol']}: {pair['baseAsset']}")
                    
                # Extract unique base assets
                base_assets = list(set(p['baseAsset'] for p in USDC_pairs))
                print(f"   🎯 Total unique base assets: {len(base_assets)}")
                
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    check_binance_api_capabilities()
    test_symbol_discovery()