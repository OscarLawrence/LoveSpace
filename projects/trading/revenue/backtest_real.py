#!/usr/bin/env python3
"""
Real Historical Backtest using existing trading system components
"""

import sys
from pathlib import Path
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add trading_system to path
sys.path.insert(0, str(Path(__file__).parent / "trading_system"))

from trading_system.binance_connector import create_binance_connector
from trading_system.backtesting_engine import BacktestEngine
from trading_system.technical_analysis import TechnicalAnalyzer


def main():
    print("🚀 Running Real Historical Backtest")
    print("="*50)
    
    # Get real market data
    print("📊 Fetching real historical data from Binance...")
    connector = create_binance_connector()
    if not connector:
        print("❌ Failed to connect to Binance")
        return
    
    # Get 30 days of hourly data
    klines = connector.get_kline_data("BTCUSDC", "1h", 720)  # 30 days
    if not klines:
        print("❌ Failed to fetch historical data")
        return
    
    print(f"✅ Fetched {len(klines)} data points")
    
    # Convert to backtest format
    price_data = []
    for kline in klines:
        price_data.append({
            'timestamp': datetime.fromtimestamp(kline['open_time'] / 1000),
            'open': kline['open'],
            'high': kline['high'], 
            'low': kline['low'],
            'close': kline['close'],
            'volume': kline['volume']
        })
    
    # Generate signals chronologically
    print("🎯 Generating trading signals...")
    analyzer = TechnicalAnalyzer(collaboration_weight=0.1)
    analyzer.min_confidence_threshold = 0.4  # Lower threshold
    signals = []
    
    for i in range(50, len(price_data)):  # Need history
        current_data = price_data[i]
        history = price_data[max(0, i-99):i+1]
        
        prices = [d['close'] for d in history]
        volumes = [d['volume'] for d in history]
        
        try:
            signal = analyzer.generate_signal(prices, volumes, current_data['close'])
            
            if signal:
                signals.append({
                    'timestamp': current_data['timestamp'],
                    'signal': signal.signal_type.value,
                    'confidence': signal.confidence,
                    'market_impact': signal.market_impact_score,
                    'reasoning': signal.reasoning
                })
        except Exception as e:
            if i == 50:  # Only print first error
                print(f"⚠️  Signal generation error: {e}")
                print(f"   Sample prices: {prices[-5:]}")
                print(f"   Sample volumes: {volumes[-5:]}")
            continue
    
    print(f"✅ Generated {len(signals)} signals")
    
    # Run backtest
    print("⚡ Running backtest...")
    engine = BacktestEngine(initial_capital=100000.0)
    
    risk_params = {
        'max_position_size': 0.1,
        'stop_loss': 0.02,
        'take_profit': 0.05
    }
    
    result = engine.run_backtest(price_data, signals, risk_params)
    
    # Print results
    print("\n" + "="*60)
    print("📈 REAL MARKET BACKTEST RESULTS")
    print("="*60)
    print(f"💰 Total Return:         {result.total_return*100:+6.2f}%")
    print(f"📊 Annualized Return:    {result.annualized_return*100:+6.2f}%")
    print(f"🛡️  Sharpe Ratio:         {result.sharpe_ratio:6.2f}")
    print(f"📉 Max Drawdown:         {result.max_drawdown*100:6.2f}%")
    print(f"🎯 Total Trades:         {result.total_trades:6d}")
    print(f"✅ Win Rate:             {result.win_rate*100:6.1f}%")
    print(f"⚙️  Execution Time:       {result.execution_time:.2f}s")
    print(f"📅 Period:               {result.start_date.strftime('%Y-%m-%d')} to {result.end_date.strftime('%Y-%m-%d')}")
    print("="*60)


if __name__ == "__main__":
    main()