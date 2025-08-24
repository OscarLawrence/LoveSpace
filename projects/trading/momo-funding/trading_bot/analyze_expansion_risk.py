#!/usr/bin/env python3
"""
Risk Analysis: Expanding to ALL Coins vs Top 10-100
Mathematical analysis of liquidity, slippage, and execution risks.
"""

from scientific_trader import ScientificTrader
import time

def analyze_expansion_risks():
    """
    Analyze the risks and benefits of expanding beyond top 100 coins.
    
    KEY RISKS FOR SMALL COINS:
    1. Liquidity Risk - Wide bid-ask spreads
    2. Execution Risk - Cannot fill orders at expected prices  
    3. Manipulation Risk - Pump and dump schemes
    4. Delisting Risk - Exchange removes trading pairs
    5. Technical Risk - API failures, data gaps
    
    MATHEMATICAL ANALYSIS:
    - Theoretical opportunities increase with more coins
    - BUT execution costs may exceed theoretical profits
    """
    
    print("🔬 EXPANSION RISK ANALYSIS: ALL COINS vs TOP 100")
    print("="*60)
    
    try:
        trader = ScientificTrader()
        
        print("\n📊 FETCHING COMPREHENSIVE MARKET DATA...")
        
        # Test different market cap tiers
        test_tiers = {
            "Top 10": ["BTCUSDC", "ETHUSDC", "BNBUSDC", "SOLUSDC", "ADAUSDC", 
                      "AVAXUSDC", "DOTUSDC", "LINKUSDC", "MATICUSDC", "UNIUSDC"],
            "Top 11-25": ["ATOMUSDC", "ALGOUSDC", "VETUSDC", "XLMUSDC", "TRXUSDC",
                         "FILUSDC", "ICPUSDC", "HBARUSDC", "NEARUSDC", "FLOWUSDC"],
            "Mid Cap (26-50)": ["AAVEUSDC", "GRTUSDC", "SANDUSDC", "MANAUSDC", "AXSUSDC"],
            "Lower Cap (51-100)": ["CHZUSDC", "ENJUSDC", "BATUSDC", "ZECUSDC"],
            "Micro Cap (100+)": ["HOTUSDC", "DENTUSDC", "WINUSDC", "BTTUSDC"]
        }
        
        tier_analysis = {}
        
        for tier_name, symbols in test_tiers.items():
            print(f"\n🔍 Analyzing {tier_name}:")
            
            tier_data = {
                'symbols_tested': 0,
                'symbols_available': 0,
                'avg_volume': 0,
                'avg_spread': 0,
                'price_ranges': [],
                'volumes': [],
                'execution_feasible': 0
            }
            
            for symbol in symbols[:5]:  # Test first 5 to avoid rate limits
                try:
                    # Get market data
                    data = trader.get_market_data(symbol, "1h", 24)  # Just 24h for quick test
                    tier_data['symbols_tested'] += 1
                    
                    if len(data) >= 10:
                        tier_data['symbols_available'] += 1
                        
                        current_price = data[-1].close
                        avg_volume = sum(d.volume for d in data[-10:]) / 10
                        
                        # Calculate price volatility (proxy for spread)
                        prices = [d.close for d in data[-10:]]
                        if len(prices) >= 2:
                            price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] 
                                           for i in range(1, len(prices))]
                            avg_volatility = sum(price_changes) / len(price_changes)
                        else:
                            avg_volatility = 0
                        
                        # Estimate execution feasibility
                        min_trade_size = 10  # $10 minimum
                        shares_needed = min_trade_size / current_price
                        
                        # Very rough liquidity estimate
                        volume_in_usd = avg_volume * current_price
                        daily_volume = volume_in_usd * 24  # Rough daily volume
                        
                        execution_feasible = daily_volume > 1000  # Need >$1000 daily volume
                        
                        tier_data['volumes'].append(daily_volume)
                        tier_data['price_ranges'].append(avg_volatility)
                        if execution_feasible:
                            tier_data['execution_feasible'] += 1
                        
                        print(f"   {symbol}: ${current_price:,.4f}, Vol: ${daily_volume:,.0f}/day, "
                              f"Volatility: {avg_volatility:.2%}")
                    
                    time.sleep(0.2)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ❌ {symbol}: {e}")
            
            # Calculate tier statistics
            if tier_data['volumes']:
                tier_data['avg_volume'] = sum(tier_data['volumes']) / len(tier_data['volumes'])
                tier_data['avg_spread'] = sum(tier_data['price_ranges']) / len(tier_data['price_ranges'])
            
            tier_analysis[tier_name] = tier_data
            
            # Tier summary
            feasible_pct = (tier_data['execution_feasible'] / tier_data['symbols_tested'] 
                           if tier_data['symbols_tested'] > 0 else 0)
            
            print(f"   📊 Summary:")
            print(f"      Available Data: {tier_data['symbols_available']}/{tier_data['symbols_tested']}")
            print(f"      Avg Daily Volume: ${tier_data['avg_volume']:,.0f}")
            print(f"      Avg Volatility: {tier_data['avg_spread']:.2%}")
            print(f"      Execution Feasible: {tier_data['execution_feasible']}/{tier_data['symbols_tested']} ({feasible_pct:.1%})")
        
        # Risk analysis summary
        print(f"\n🎯 RISK ANALYSIS RESULTS:")
        
        for tier_name, data in tier_analysis.items():
            if data['symbols_tested'] > 0:
                risk_score = calculate_risk_score(data)
                opportunity_score = calculate_opportunity_score(data)
                
                print(f"\n📈 {tier_name}:")
                print(f"   Risk Score: {risk_score:.1f}/10 (lower is better)")
                print(f"   Opportunity Score: {opportunity_score:.1f}/10 (higher is better)")
                print(f"   Risk-Adjusted Score: {opportunity_score - risk_score:.1f}")
        
        # Recommendations
        print(f"\n💡 EXPANSION STRATEGY RECOMMENDATIONS:")
        
        best_tier = max(tier_analysis.items(), 
                       key=lambda x: calculate_opportunity_score(x[1]) - calculate_risk_score(x[1]))
        
        print(f"   🏆 OPTIMAL TIER: {best_tier[0]}")
        print(f"   📊 REASONING:")
        print(f"      • Best risk-adjusted opportunity score")
        print(f"      • Sufficient liquidity for execution")
        print(f"      • Manageable volatility and spreads")
        
        print(f"\n⚠️  EXPANSION RISKS FOR MICRO CAPS:")
        print(f"   1. 🚫 Liquidity Risk: Bid-ask spreads can be 5-20%")
        print(f"   2. 📉 Execution Risk: Cannot fill orders at theoretical prices")
        print(f"   3. 🎭 Manipulation Risk: Pump and dump schemes common") 
        print(f"   4. 💀 Delisting Risk: Exchanges remove low-volume pairs")
        print(f"   5. 🔧 Technical Risk: Poor API reliability, data gaps")
        
        print(f"\n✅ RECOMMENDED APPROACH:")
        print(f"   Phase 1: Start with Top 25 (proven liquidity)")
        print(f"   Phase 2: Add Top 50 after successful Phase 1")
        print(f"   Phase 3: Expand to Top 100 with enhanced filters")
        print(f"   Phase 4: Consider micro-caps ONLY with:")
        print(f"      • Minimum $10K daily volume filter")
        print(f"      • Maximum 5% spread filter") 
        print(f"      • Real-time delisting monitoring")
        print(f"      • Smaller position sizes (0.5% max)")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

def calculate_risk_score(tier_data):
    """Calculate risk score (0-10, higher = more risky)."""
    if tier_data['symbols_tested'] == 0:
        return 10
    
    # Low volume = high risk
    volume_risk = max(0, min(10, 10 - tier_data['avg_volume'] / 10000))
    
    # High volatility = high risk (but also opportunity)
    volatility_risk = min(10, tier_data['avg_spread'] * 1000)
    
    # Low execution feasibility = high risk
    feasible_pct = tier_data['execution_feasible'] / tier_data['symbols_tested']
    execution_risk = (1 - feasible_pct) * 10
    
    return (volume_risk + volatility_risk + execution_risk) / 3

def calculate_opportunity_score(tier_data):
    """Calculate opportunity score (0-10, higher = more opportunities)."""
    if tier_data['symbols_tested'] == 0:
        return 0
    
    # Higher volatility = more opportunities (up to a point)
    volatility_opportunity = min(10, tier_data['avg_spread'] * 2000)
    
    # Data availability = opportunities
    availability_opportunity = (tier_data['symbols_available'] / tier_data['symbols_tested']) * 10
    
    # But must be executable
    execution_modifier = tier_data['execution_feasible'] / tier_data['symbols_tested']
    
    return (volatility_opportunity + availability_opportunity) / 2 * execution_modifier

if __name__ == "__main__":
    analyze_expansion_risks()