#!/usr/bin/env python3
"""
Backtest Runner for MomoAI Trading System
Generates historical data and runs comprehensive backtesting.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import math

# Add trading_system to path
sys.path.insert(0, str(Path(__file__).parent / "trading_system"))

from trading_system.backtesting_engine import BacktestEngine
from trading_system.technical_analysis import TechnicalAnalyzer


def generate_realistic_price_data(days: int = 30, initial_price: float = 50000.0) -> list:
    """Generate realistic crypto price data for backtesting."""
    data = []
    current_price = initial_price
    current_time = datetime.now() - timedelta(days=days)
    
    # Market parameters
    daily_volatility = 0.03  # 3% daily volatility
    trend_strength = 0.001   # Slight upward trend
    
    for i in range(days * 24):  # Hourly data
        # Generate realistic OHLCV data
        price_change = random.gauss(trend_strength, daily_volatility / 24)
        new_price = current_price * (1 + price_change)
        
        # Generate OHLC with realistic spread
        volatility_factor = random.uniform(0.5, 1.5)
        high_low_range = new_price * daily_volatility * volatility_factor / 24
        
        open_price = current_price
        close_price = new_price
        high_price = max(open_price, close_price) + random.uniform(0, high_low_range)
        low_price = min(open_price, close_price) - random.uniform(0, high_low_range)
        
        # Volume (higher during volatile periods)
        base_volume = 1000000
        volume_multiplier = 1 + abs(price_change) * 10
        volume = base_volume * volume_multiplier * random.uniform(0.5, 2.0)
        
        data.append({
            'timestamp': current_time,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
        
        current_price = new_price
        current_time += timedelta(hours=1)
    
    return data


def generate_trading_signals(price_data: list) -> list:
    """Generate trading signals using the technical analyzer."""
    analyzer = TechnicalAnalyzer(collaboration_weight=0.1)  # Lower collaboration weight for more signals
    analyzer.min_confidence_threshold = 0.4  # Lower threshold for testing
    signals = []
    
    for i in range(50, len(price_data)):  # Start after enough history
        # Get price history for analysis
        history = price_data[max(0, i-99):i+1]  # Use up to 100 bars of history
        prices = [bar['close'] for bar in history]
        volumes = [bar['volume'] for bar in history]
        current_price = prices[-1]
        
        try:
            # Generate signal
            signal = analyzer.generate_signal(prices, volumes, current_price)
            
            if signal:
                # Convert to backtest format
                signals.append({
                    'timestamp': price_data[i]['timestamp'],
                    'signal': signal.signal_type.value.lower(),
                    'confidence': signal.confidence,
                    'market_impact': signal.market_impact_score,
                    'reasoning': signal.reasoning
                })
        except Exception as e:
            print(f"Signal generation error at index {i}: {e}")
            continue
    
    return signals


def print_backtest_summary(result):
    """Print comprehensive backtest results."""
    print("\n" + "="*80)
    print("🎯 MOMOAI TRADING SYSTEM BACKTEST RESULTS")
    print("="*80)
    
    # Performance Metrics
    print(f"📊 PERFORMANCE METRICS")
    print(f"  Total Return:        {result.total_return*100:+6.2f}%")
    print(f"  Annualized Return:   {result.annualized_return*100:+6.2f}%")
    print(f"  Sharpe Ratio:        {result.sharpe_ratio:6.2f}")
    print(f"  Max Drawdown:        {result.max_drawdown*100:6.2f}%")
    print(f"  Calmar Ratio:        {result.calmar_ratio:6.2f}")
    
    # Risk Metrics
    print(f"\n🛡️  RISK METRICS")
    print(f"  Value at Risk (95%): {result.var_95*100:6.2f}%")
    print(f"  Expected Shortfall:  {result.expected_shortfall*100:6.2f}%")
    
    # Trading Statistics
    print(f"\n📈 TRADING STATISTICS")
    print(f"  Total Trades:        {result.total_trades:6d}")
    print(f"  Winning Trades:      {result.winning_trades:6d}")
    print(f"  Losing Trades:       {result.losing_trades:6d}")
    print(f"  Win Rate:            {result.win_rate*100:6.1f}%")
    print(f"  Profit Factor:       {result.profit_factor:6.2f}")
    print(f"  Avg Trade Duration:  {result.avg_trade_duration:6.1f} hours")
    
    # Collaboration Metrics
    print(f"\n🤝 COLLABORATION METRICS")
    print(f"  Market Impact Score: {result.market_impact_score:6.3f}")
    print(f"  Volatility Contrib:  {result.volatility_contribution:6.3f}")
    print(f"  Liquidity Impact:    {result.liquidity_impact:6.3f}")
    
    # Execution Details
    print(f"\n⚙️  EXECUTION DETAILS")
    print(f"  Backtest Period:     {result.start_date.strftime('%Y-%m-%d')} to {result.end_date.strftime('%Y-%m-%d')}")
    print(f"  Execution Time:      {result.execution_time:.2f} seconds")
    print(f"  Status:              {result.status.value.upper()}")
    
    # Performance Rating
    print(f"\n🏆 PERFORMANCE RATING")
    rating = rate_strategy_performance(result)
    print(f"  Overall Rating:      {rating}")
    
    print("="*80)


def rate_strategy_performance(result) -> str:
    """Rate the strategy performance based on multiple metrics."""
    score = 0
    
    # Return score (0-30 points)
    if result.annualized_return > 0.20:
        score += 30
    elif result.annualized_return > 0.10:
        score += 20
    elif result.annualized_return > 0.05:
        score += 10
    elif result.annualized_return > 0:
        score += 5
    
    # Sharpe ratio score (0-25 points)
    if result.sharpe_ratio > 2.0:
        score += 25
    elif result.sharpe_ratio > 1.0:
        score += 15
    elif result.sharpe_ratio > 0.5:
        score += 10
    elif result.sharpe_ratio > 0:
        score += 5
    
    # Drawdown score (0-20 points)
    if result.max_drawdown < 0.05:
        score += 20
    elif result.max_drawdown < 0.10:
        score += 15
    elif result.max_drawdown < 0.20:
        score += 10
    elif result.max_drawdown < 0.30:
        score += 5
    
    # Win rate score (0-15 points)
    if result.win_rate > 0.60:
        score += 15
    elif result.win_rate > 0.50:
        score += 10
    elif result.win_rate > 0.40:
        score += 5
    
    # Collaboration score (0-10 points)
    if result.market_impact_score < 0.3:
        score += 10
    elif result.market_impact_score < 0.5:
        score += 5
    
    # Rating based on total score
    if score >= 85:
        return "⭐⭐⭐⭐⭐ EXCELLENT (Strategy ready for live trading)"
    elif score >= 70:
        return "⭐⭐⭐⭐ VERY GOOD (Minor optimizations recommended)"
    elif score >= 55:
        return "⭐⭐⭐ GOOD (Moderate improvements needed)"
    elif score >= 40:
        return "⭐⭐ FAIR (Significant improvements required)"
    else:
        return "⭐ POOR (Strategy needs major rework)"


def main():
    """Run comprehensive backtest."""
    print("🚀 Starting MomoAI Trading System Backtest...")
    
    # Generate test data
    print("📊 Generating realistic market data...")
    price_data = generate_realistic_price_data(days=30)
    print(f"✅ Generated {len(price_data)} data points over 30 days")
    
    # Generate trading signals
    print("🎯 Generating trading signals...")
    signals = generate_trading_signals(price_data)
    print(f"✅ Generated {len(signals)} trading signals")
    
    # Run backtest
    print("⚡ Running backtest...")
    engine = BacktestEngine(initial_capital=100000.0)
    
    # Debug: Print sample signals
    print(f"📋 Sample signals (first 5):")
    for i, sig in enumerate(signals[:5]):
        print(f"  {i+1}. {sig['timestamp']}: {sig['signal']} (confidence: {sig['confidence']:.2f})")
    
    risk_params = {
        'max_position_size': 0.1,
        'stop_loss': 0.02,
        'take_profit': 0.05
    }
    
    result = engine.run_backtest(price_data, signals, risk_params)
    
    # Display results
    print_backtest_summary(result)
    
    return result


if __name__ == "__main__":
    main()