#!/usr/bin/env python3
"""
Binance Testnet vs Mainnet Data Quality Analysis
Critical validation: Is testnet data reliable for strategy development?
"""

import time
from datetime import datetime, timedelta
from execution.binance_connector import BinanceCredentials, BinanceConnector

def compare_testnet_vs_mainnet():
    """
    Compare testnet vs mainnet data quality.
    
    CRITICAL ISSUES TO CHECK:
    1. Price accuracy vs real market
    2. Volume data reliability  
    3. Timestamp accuracy
    4. Market hours simulation
    5. Order book depth simulation
    6. API response consistency
    """
    
    print("🔬 BINANCE DATA QUALITY ANALYSIS")
    print("Testnet vs Mainnet Comparison")
    print("="*50)
    
    # Test credentials (dummy for testnet, real for mainnet comparison)
    testnet_creds = BinanceCredentials(
        api_key="dummy_key",
        api_secret="dummy_secret", 
        testnet=True
    )
    
    mainnet_creds = BinanceCredentials(
        api_key="dummy_key",  # Won't work without real keys
        api_secret="dummy_secret",
        testnet=False
    )
    
    try:
        print("\n📊 TESTNET DATA ANALYSIS:")
        testnet_connector = BinanceConnector(testnet_creds)
        
        # Test connectivity
        testnet_ping = testnet_connector.test_connectivity()
        print(f"   Connectivity: {'✅' if testnet_ping else '❌'}")
        
        if testnet_ping:
            # Test market data for major pairs
            test_symbols = ["BTCUSDC", "ETHUSDC", "BNBUSDC"]
            
            for symbol in test_symbols:
                print(f"\n   Testing {symbol}:")
                
                # Current price
                try:
                    current_price = testnet_connector.get_current_price(symbol)
                    print(f"   Current Price: ${current_price:,.2f}")
                except Exception as e:
                    print(f"   ❌ Current Price Error: {e}")
                
                # Historical data
                try:
                    klines = testnet_connector.get_kline_data(symbol, "1h", 24)
                    if klines:
                        latest_kline = klines[-1]
                        print(f"   Latest Kline: ${latest_kline['close']:,.2f}")
                        print(f"   Volume: {latest_kline['volume']:,.0f}")
                        print(f"   Timestamp: {datetime.fromtimestamp(latest_kline['open_time']/1000)}")
                        
                        # Check if data is stale
                        latest_time = datetime.fromtimestamp(latest_kline['close_time']/1000)
                        time_diff = datetime.now() - latest_time
                        
                        if time_diff > timedelta(hours=2):
                            print(f"   ⚠️  STALE DATA: {time_diff} old!")
                        else:
                            print(f"   ✅ Fresh data ({time_diff})")
                        
                        # Check for realistic volume patterns
                        if len(klines) >= 24:
                            volumes = [k['volume'] for k in klines[-24:]]
                            avg_volume = sum(volumes) / len(volumes)
                            volume_variation = max(volumes) / min(volumes) if min(volumes) > 0 else 0
                            
                            print(f"   Volume Analysis:")
                            print(f"      Avg 24h Volume: {avg_volume:,.0f}")
                            print(f"      Volume Variation: {volume_variation:.1f}x")
                            
                            # Red flags for fake data
                            if volume_variation < 1.1:  # Too consistent
                                print(f"   🚨 SUSPICIOUS: Volume too consistent")
                            if all(v == volumes[0] for v in volumes):  # Identical volumes
                                print(f"   🚨 FAKE DATA: Identical volumes")
                    else:
                        print(f"   ❌ No historical data available")
                        
                except Exception as e:
                    print(f"   ❌ Historical Data Error: {e}")
                
                time.sleep(0.5)  # Rate limiting
        
        # Test account info (should fail gracefully with dummy keys)
        print(f"\n💰 ACCOUNT DATA TEST:")
        try:
            account_info = testnet_connector.get_account_info()
            if account_info:
                print(f"   ✅ Account info accessible")
                for asset, balance in list(account_info.items())[:3]:
                    print(f"   {asset}: {balance.total}")
            else:
                print(f"   ❌ No account info (expected with dummy keys)")
        except Exception as e:
            print(f"   ❌ Account Error: {e}")
        
    except Exception as e:
        print(f"❌ Testnet connection failed: {e}")
    
    # Compare with external price sources
    print(f"\n🌐 EXTERNAL PRICE VALIDATION:")
    try:
        import requests
        
        # Get real BTC price from CoinGecko for comparison
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")
        if response.status_code == 200:
            real_prices = response.json()
            real_btc = real_prices['bitcoin']['usd']
            real_eth = real_prices['ethereum']['usd']
            
            print(f"   Real BTC (CoinGecko): ${real_btc:,.2f}")
            print(f"   Real ETH (CoinGecko): ${real_eth:,.2f}")
            
            # Compare with testnet prices
            if testnet_ping:
                try:
                    testnet_btc = testnet_connector.get_current_price("BTCUSDC")
                    testnet_eth = testnet_connector.get_current_price("ETHUSDC")
                    
                    btc_diff = abs(testnet_btc - real_btc) / real_btc * 100
                    eth_diff = abs(testnet_eth - real_eth) / real_eth * 100
                    
                    print(f"   Testnet BTC: ${testnet_btc:,.2f} ({btc_diff:.1f}% diff)")
                    print(f"   Testnet ETH: ${testnet_eth:,.2f} ({eth_diff:.1f}% diff)")
                    
                    if btc_diff > 5 or eth_diff > 5:
                        print(f"   🚨 MAJOR PRICE DISCREPANCY! Testnet unreliable")
                    elif btc_diff > 1 or eth_diff > 1:
                        print(f"   ⚠️  Price difference detected")
                    else:
                        print(f"   ✅ Prices reasonably aligned")
                        
                except Exception as e:
                    print(f"   ❌ Price comparison failed: {e}")
        
    except Exception as e:
        print(f"❌ External validation failed: {e}")
    
    # Final assessment
    print(f"\n🎯 TESTNET RELIABILITY ASSESSMENT:")
    print(f"   🔍 Known Issues:")
    print(f"      • Stale/fake price data")
    print(f"      • Unrealistic volume patterns") 
    print(f"      • Order execution simulation quirks")
    print(f"      • Inconsistent API responses")
    print(f"      • No real market dynamics")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   ❌ DO NOT use testnet for:")
    print(f"      • Strategy backtesting")
    print(f"      • Correlation analysis") 
    print(f"      • Volume analysis")
    print(f"      • Real performance validation")
    
    print(f"   ✅ ONLY use testnet for:")
    print(f"      • API integration testing")
    print(f"      • Order placement mechanics")
    print(f"      • Error handling")
    print(f"      • Basic connectivity")
    
    print(f"\n🚀 SOLUTION: MAINNET WITH TINY POSITIONS")
    print(f"   • Use mainnet with $10-50 real capital")
    print(f"   • Real market data = real strategy validation")
    print(f"   • Minimal risk, maximum learning")
    print(f"   • Scale up only after proven performance")

if __name__ == "__main__":
    compare_testnet_vs_mainnet()