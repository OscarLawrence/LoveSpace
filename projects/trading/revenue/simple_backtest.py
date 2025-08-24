#!/usr/bin/env python3
"""
Simple Working Backtest for MomoAI Trading System
Direct implementation for immediate results.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import math

# Add trading_system to path
sys.path.insert(0, str(Path(__file__).parent / "trading_system"))

from trading_system.technical_analysis import TechnicalAnalyzer


def generate_price_data(days: int = 30) -> list:
    """Generate crypto-like price data."""
    data = []
    price = 50000.0
    time = datetime.now() - timedelta(days=days)
    
    for hour in range(days * 24):
        # Random walk with slight upward bias
        change = random.gauss(0.001, 0.02)  # 0.1% mean, 2% std
        price *= (1 + change)
        
        data.append({
            'timestamp': time,
            'price': price,
            'volume': random.uniform(800000, 1200000)
        })
        time += timedelta(hours=1)
    
    return data


def run_simple_backtest():
    """Run a straightforward backtest."""
    print("🚀 Running Simple MomoAI Trading Backtest")
    print("=" * 50)
    
    # Generate data
    data = generate_price_data(30)
    print(f"📊 Generated {len(data)} price points")
    
    # Initialize
    capital = 100000.0
    position = 0.0
    trades = []
    analyzer = TechnicalAnalyzer(collaboration_weight=0.1)
    analyzer.min_confidence_threshold = 0.4
    
    print("🎯 Running trading simulation...")
    
    for i in range(50, len(data)):  # Need history for indicators
        current = data[i]
        history = data[max(0, i-99):i+1]
        
        prices = [d['price'] for d in history]
        volumes = [d['volume'] for d in history]
        current_price = current['price']
        
        # Generate signal
        try:
            signal = analyzer.generate_signal(prices, volumes, current_price)
            
            if signal and signal.confidence > 0.5:
                # Execute trade
                if signal.signal_type.value in ['buy', 'strong_buy'] and position == 0:
                    # Buy with 20% of capital
                    trade_size = capital * 0.2
                    position = trade_size / current_price
                    capital -= trade_size
                    
                    trades.append({
                        'type': 'buy',
                        'price': current_price,
                        'quantity': position,
                        'capital': capital,
                        'timestamp': current['timestamp'],
                        'confidence': signal.confidence
                    })
                    
                elif signal.signal_type.value in ['sell', 'strong_sell'] and position > 0:
                    # Sell position
                    sell_value = position * current_price
                    capital += sell_value
                    
                    trades.append({
                        'type': 'sell',
                        'price': current_price,
                        'quantity': position,
                        'capital': capital,
                        'timestamp': current['timestamp'],
                        'confidence': signal.confidence
                    })
                    
                    position = 0
                    
        except Exception as e:
            continue
    
    # Final portfolio value
    final_value = capital + (position * data[-1]['price'])
    total_return = (final_value - 100000) / 100000
    
    # Calculate metrics
    buy_trades = [t for t in trades if t['type'] == 'buy']
    sell_trades = [t for t in trades if t['type'] == 'sell']
    
    # Match buy/sell pairs for P&L
    profitable_trades = 0
    total_profit = 0
    
    for i, buy in enumerate(buy_trades):
        if i < len(sell_trades):
            sell = sell_trades[i]
            pnl = (sell['price'] - buy['price']) * buy['quantity']
            total_profit += pnl
            if pnl > 0:
                profitable_trades += 1
    
    completed_trades = min(len(buy_trades), len(sell_trades))
    win_rate = profitable_trades / completed_trades if completed_trades > 0 else 0
    
    # Print results
    print("\n" + "=" * 60)
    print("📈 BACKTEST RESULTS")
    print("=" * 60)
    print(f"💰 Initial Capital:      ${100000:,.2f}")
    print(f"💰 Final Value:          ${final_value:,.2f}")
    print(f"📊 Total Return:         {total_return*100:+.2f}%")
    print(f"📊 Annualized Return:    {(total_return * 12):+.2f}% (30-day extrapolated)")
    print()
    print(f"🔄 Total Signals:        {len(trades)}")
    print(f"🔄 Buy Orders:           {len(buy_trades)}")
    print(f"🔄 Sell Orders:          {len(sell_trades)}")
    print(f"🔄 Completed Trades:     {completed_trades}")
    print(f"📈 Winning Trades:       {profitable_trades}")
    print(f"📈 Win Rate:             {win_rate*100:.1f}%")
    
    if completed_trades > 0:
        avg_profit_per_trade = total_profit / completed_trades
        print(f"💵 Avg Profit/Trade:     ${avg_profit_per_trade:,.2f}")
    
    # Show sample trades
    print(f"\n📋 Sample Trades (first 5):")
    for i, trade in enumerate(trades[:5]):
        print(f"  {i+1}. {trade['timestamp'].strftime('%m-%d %H:%M')}: "
              f"{trade['type'].upper()} @ ${trade['price']:,.2f} "
              f"(conf: {trade['confidence']:.2f})")
    
    # Performance rating
    print(f"\n🏆 PERFORMANCE RATING")
    if total_return > 0.20:
        rating = "⭐⭐⭐⭐⭐ EXCELLENT"
    elif total_return > 0.10:
        rating = "⭐⭐⭐⭐ VERY GOOD"
    elif total_return > 0.05:
        rating = "⭐⭐⭐ GOOD"
    elif total_return > 0:
        rating = "⭐⭐ FAIR"
    else:
        rating = "⭐ NEEDS IMPROVEMENT"
    
    print(f"  Strategy Rating:     {rating}")
    print("=" * 60)
    
    return {
        'total_return': total_return,
        'final_value': final_value,
        'trades': len(trades),
        'win_rate': win_rate,
        'rating': rating
    }


if __name__ == "__main__":
    run_simple_backtest()