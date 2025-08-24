#!/usr/bin/env python3
"""
Real Market Correlation Analysis
Analyze actual correlation patterns in live market data vs testnet fake data.
"""

from optimal_trading_system import OptimalTradingSystem
from datetime import datetime

def analyze_real_market_correlations():
    """
    Analyze real correlation patterns to understand:
    1. What correlation breakdowns actually exist
    2. How often they occur
    3. What thresholds make sense for real markets
    4. Which asset pairs show the most opportunity
    """
    
    print("🔬 REAL MARKET CORRELATION ANALYSIS")
    print("="*50)
    
    try:
        # Initialize with real market data
        system = OptimalTradingSystem(min_confidence=0.60, max_position=0.015)  # Lower confidence for analysis
        
        # Get tradeable assets
        assets = system.get_tradeable_assets()
        print(f"\n📊 Analyzing {len(assets)} assets with real market data")
        
        # Fetch comprehensive market data
        market_data = system.get_market_data_batch(assets, hours=200)  # More history
        
        if len(market_data) < 2:
            print("❌ Insufficient market data for analysis")
            return
        
        print(f"\n🎯 CORRELATION ANALYSIS RESULTS:")
        
        correlation_stats = []
        
        # Analyze all pairs
        asset_list = list(market_data.keys())
        for i in range(len(asset_list)):
            for j in range(i + 1, len(asset_list)):
                asset1, asset2 = asset_list[i], asset_list[j]
                
                data1 = market_data[asset1]
                data2 = market_data[asset2]
                
                if len(data1) >= 100 and len(data2) >= 100:
                    # Calculate multiple correlation periods
                    recent_prices1 = [d['close'] for d in data1[-20:]]
                    recent_prices2 = [d['close'] for d in data2[-20:]]
                    
                    mid_prices1 = [d['close'] for d in data1[-40:-20]]  
                    mid_prices2 = [d['close'] for d in data2[-40:-20]]
                    
                    historical_prices1 = [d['close'] for d in data1[-60:-40]]
                    historical_prices2 = [d['close'] for d in data2[-60:-40]]
                    
                    # Calculate returns and correlations
                    recent_returns1 = system.altcoin_detector._calculate_returns(recent_prices1)
                    recent_returns2 = system.altcoin_detector._calculate_returns(recent_prices2)
                    mid_returns1 = system.altcoin_detector._calculate_returns(mid_prices1)
                    mid_returns2 = system.altcoin_detector._calculate_returns(mid_prices2)
                    hist_returns1 = system.altcoin_detector._calculate_returns(historical_prices1)
                    hist_returns2 = system.altcoin_detector._calculate_returns(historical_prices2)
                    
                    if (len(recent_returns1) >= 10 and len(mid_returns1) >= 10 and len(hist_returns1) >= 10):
                        recent_corr = system.altcoin_detector._calculate_correlation(recent_returns1, recent_returns2)
                        mid_corr = system.altcoin_detector._calculate_correlation(mid_returns1, mid_returns2)
                        hist_corr = system.altcoin_detector._calculate_correlation(hist_returns1, hist_returns2)
                        
                        # Calculate breakdowns
                        recent_vs_mid = abs(recent_corr - mid_corr)
                        recent_vs_hist = abs(recent_corr - hist_corr)
                        mid_vs_hist = abs(mid_corr - hist_corr)
                        
                        max_breakdown = max(recent_vs_mid, recent_vs_hist, mid_vs_hist)
                        
                        # Calculate volumes for feasibility
                        recent_volume1 = sum(d['volume'] for d in data1[-24:]) / 24 * data1[-1]['close']
                        recent_volume2 = sum(d['volume'] for d in data2[-24:]) / 24 * data2[-1]['close'] 
                        avg_volume = (recent_volume1 + recent_volume2) / 2
                        
                        correlation_stats.append({
                            'pair': f"{asset1}/{asset2}",
                            'recent_corr': recent_corr,
                            'mid_corr': mid_corr,
                            'hist_corr': hist_corr,
                            'max_breakdown': max_breakdown,
                            'recent_vs_hist': recent_vs_hist,
                            'avg_volume': avg_volume,
                            'asset1_rank': system.optimal_universe.get(asset1, type('obj', (object,), {'rank': 999})).rank,
                            'asset2_rank': system.optimal_universe.get(asset2, type('obj', (object,), {'rank': 999})).rank
                        })
        
        # Sort by breakdown magnitude
        correlation_stats.sort(key=lambda x: x['max_breakdown'], reverse=True)
        
        print(f"\n🏆 TOP CORRELATION BREAKDOWNS (Real Market Data):")
        for i, stat in enumerate(correlation_stats[:10], 1):
            print(f"   {i}. {stat['pair']}:")
            print(f"      Recent Correlation: {stat['recent_corr']:.3f}")
            print(f"      Historical Correlation: {stat['hist_corr']:.3f}")
            print(f"      Max Breakdown: {stat['max_breakdown']:.3f}")
            print(f"      Volume: ${stat['avg_volume']:,.0f}/day")
            print(f"      Market Cap Ranks: {stat['asset1_rank']}-{stat['asset2_rank']}")
            
            # Assess if this would trigger our strategy
            if stat['max_breakdown'] > 0.3:
                confidence = min(stat['max_breakdown'] * 2.0, 0.95)
                print(f"      🎯 WOULD TRIGGER: {confidence:.1%} confidence")
            else:
                print(f"      📊 Below threshold (need >0.3)")
            print()
        
        # Statistical summary
        if correlation_stats:
            breakdowns = [s['max_breakdown'] for s in correlation_stats]
            avg_breakdown = sum(breakdowns) / len(breakdowns)
            max_breakdown = max(breakdowns)
            
            # Count opportunities at different thresholds
            opportunities_03 = sum(1 for b in breakdowns if b > 0.3)
            opportunities_04 = sum(1 for b in breakdowns if b > 0.4)
            opportunities_05 = sum(1 for b in breakdowns if b > 0.5)
            
            print(f"📈 STATISTICAL SUMMARY:")
            print(f"   Total Pairs Analyzed: {len(correlation_stats)}")
            print(f"   Average Breakdown: {avg_breakdown:.3f}")
            print(f"   Maximum Breakdown: {max_breakdown:.3f}")
            print(f"   Opportunities at >0.3 threshold: {opportunities_03} ({opportunities_03/len(correlation_stats):.1%})")
            print(f"   Opportunities at >0.4 threshold: {opportunities_04} ({opportunities_04/len(correlation_stats):.1%})")
            print(f"   Opportunities at >0.5 threshold: {opportunities_05} ({opportunities_05/len(correlation_stats):.1%})")
            
            print(f"\n💡 REAL MARKET INSIGHTS:")
            if max_breakdown > 0.4:
                print(f"   ✅ Significant breakdowns exist in real data")
                print(f"   🎯 Current thresholds appear reasonable")
            elif max_breakdown > 0.3:
                print(f"   ⚠️  Moderate breakdowns found - consider lowering threshold")
                print(f"   🔧 Suggest 0.25-0.3 threshold for more opportunities")
            else:
                print(f"   ❌ Limited breakdowns in current timeframe")
                print(f"   🔄 May need longer observation period or different assets")
            
            # Volume analysis
            volumes = [s['avg_volume'] for s in correlation_stats if s['avg_volume'] > 0]
            if volumes:
                avg_volume = sum(volumes) / len(volumes)
                print(f"   💰 Average trading volume: ${avg_volume:,.0f}/day")
                if avg_volume > 50000:
                    print(f"   ✅ Sufficient liquidity for execution")
                else:
                    print(f"   ⚠️  May need larger positions or different assets")
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_real_market_correlations()