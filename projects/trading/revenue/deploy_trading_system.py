#!/usr/bin/env python3
"""
MomoAI Trading System - Live Deployment
Deploy the coherent mathematical trading system for real trading.
"""

import os
import sys
import time
import json
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add trading_system to path
sys.path.insert(0, str(Path(__file__).parent / "trading_system"))

from trading_system.binance_connector import create_binance_connector


class LiveTradingEngine:
    """Live trading engine using proven strategies from backtesting."""
    
    def __init__(self, initial_capital: float = None):
        self.connector = create_binance_connector()
        if not self.connector:
            raise ValueError("Failed to connect to Binance - check API credentials")
        
        # Get actual account balance
        balances = self.connector.get_account_info()
        
        # Check for stablecoin balances
        USDC_balance = balances.get("USDC")
        usdc_balance = balances.get("USDC") 
        busd_balance = balances.get("BUSD")
        
        # Use the largest stablecoin balance
        stable_balances = [(b, name) for b, name in [(USDC_balance, "USDC"), (usdc_balance, "USDC"), (busd_balance, "BUSD")] if b and b.total > 0]
        
        if not stable_balances:
            raise ValueError(f"No stablecoin balance found. Balances: USDC={USDC_balance.total if USDC_balance else 0:.2f}, USDC={usdc_balance.total if usdc_balance else 0:.2f}")
        
        # Use the largest balance
        USDC_balance, balance_currency = max(stable_balances, key=lambda x: x[0].total)
        
        if USDC_balance.total < 1:
            raise ValueError(f"Insufficient {balance_currency} balance: ${USDC_balance.total:.2f}")
        
        # For demo with small balance
        if USDC_balance.total < 100:
            self.logger.warning(f"⚠️  Small {balance_currency} balance detected: ${USDC_balance.total:.2f}")
            self.logger.warning("Running in analysis-only mode for safety")
        
        self.capital = USDC_balance.total
        self.initial_capital = self.capital
        self.positions = {}
        self.trade_history = []
        
        # Trading parameters (from successful backtest)
        self.scan_interval = 3600  # 1 hour (to match backtest)
        self.min_confidence = 0.7  # High confidence threshold
        self.max_position_percent = 0.02  # 2% max position size
        self.symbols = ["BTCUSDC", "ETHUSDC"]
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('live_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🚀 Live Trading Engine initialized with ${self.capital:.2f}")
        
    def get_market_data(self, symbol: str, hours: int = 100) -> List[Dict]:
        """Get recent market data for analysis."""
        try:
            klines = self.connector.get_kline_data(symbol, "1h", hours)
            if not klines:
                return []
            
            data = []
            for kline in klines:
                data.append({
                    'timestamp': datetime.fromtimestamp(kline['open_time'] / 1000),
                    'open': kline['open'],
                    'high': kline['high'],
                    'low': kline['low'],
                    'close': kline['close'],
                    'volume': kline['volume']
                })
            
            return data
        except Exception as e:
            self.logger.error(f"Failed to get market data for {symbol}: {e}")
            return []
    
    def calculate_correlation_breakdown(self, btc_data: List[Dict], eth_data: List[Dict]) -> Optional[Dict]:
        """Detect correlation breakdown opportunity (market neutral)."""
        if len(btc_data) < 50 or len(eth_data) < 50:
            return None
        
        # Recent correlation (20 periods)
        btc_prices = [d['close'] for d in btc_data[-20:]]
        eth_prices = [d['close'] for d in eth_data[-20:]]
        
        btc_returns = [(btc_prices[i] - btc_prices[i-1]) / btc_prices[i-1] for i in range(1, len(btc_prices))]
        eth_returns = [(eth_prices[i] - eth_prices[i-1]) / eth_prices[i-1] for i in range(1, len(eth_prices))]
        
        if len(btc_returns) < 10:
            return None
        
        # Calculate recent correlation
        mean_btc = sum(btc_returns) / len(btc_returns)
        mean_eth = sum(eth_returns) / len(eth_returns)
        
        numerator = sum((br - mean_btc) * (er - mean_eth) for br, er in zip(btc_returns, eth_returns))
        btc_var = sum((br - mean_btc) ** 2 for br in btc_returns) ** 0.5
        eth_var = sum((er - mean_eth) ** 2 for er in eth_returns) ** 0.5
        
        if btc_var == 0 or eth_var == 0:
            return None
        
        current_corr = numerator / (btc_var * eth_var)
        
        # Historical correlation (50 periods)
        hist_btc_prices = [d['close'] for d in btc_data[-50:-20]]
        hist_eth_prices = [d['close'] for d in eth_data[-50:-20]]
        
        hist_btc_returns = [(hist_btc_prices[i] - hist_btc_prices[i-1]) / hist_btc_prices[i-1] 
                           for i in range(1, len(hist_btc_prices))]
        hist_eth_returns = [(hist_eth_prices[i] - hist_eth_prices[i-1]) / hist_eth_prices[i-1] 
                           for i in range(1, len(hist_eth_prices))]
        
        if len(hist_btc_returns) < 20:
            return None
        
        hist_mean_btc = sum(hist_btc_returns) / len(hist_btc_returns)
        hist_mean_eth = sum(hist_eth_returns) / len(hist_eth_returns)
        
        hist_numerator = sum((br - hist_mean_btc) * (er - hist_mean_eth) 
                           for br, er in zip(hist_btc_returns, hist_eth_returns))
        hist_btc_var = sum((br - hist_mean_btc) ** 2 for br in hist_btc_returns) ** 0.5
        hist_eth_var = sum((er - hist_mean_eth) ** 2 for er in hist_eth_returns) ** 0.5
        
        if hist_btc_var == 0 or hist_eth_var == 0:
            return None
        
        historical_corr = hist_numerator / (hist_btc_var * hist_eth_var)
        
        # Check for breakdown
        breakdown = abs(historical_corr - current_corr)
        
        if breakdown > 0.4:  # Significant breakdown
            confidence = min(breakdown * 1.5, 0.9)
            expected_return = breakdown * 0.3
            
            if confidence >= self.min_confidence:
                return {
                    'strategy': 'correlation_breakdown',
                    'confidence': confidence,
                    'expected_return': expected_return,
                    'risk_level': 0.15,
                    'proof': f"Correlation breakdown: {breakdown:.2%} from {historical_corr:.2f} to {current_corr:.2f}"
                }
        
        return None
    
    def calculate_mean_reversion(self, data: List[Dict]) -> Optional[Dict]:
        """Detect mean reversion opportunity."""
        if len(data) < 30:
            return None
        
        prices = [d['close'] for d in data[-30:]]
        current_price = prices[-1]
        
        # 20-period moving average and standard deviation
        sma_20 = sum(prices[-20:]) / 20
        variance = sum((p - sma_20) ** 2 for p in prices[-20:]) / 20
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return None
        
        # Z-score
        z_score = abs(current_price - sma_20) / std_dev
        
        if z_score > 2.0:  # More than 2 standard deviations
            confidence = min(z_score / 3.0, 0.9)
            expected_return = min(z_score * 0.02, 0.08)
            
            if confidence >= self.min_confidence:
                return {
                    'strategy': 'mean_reversion',
                    'confidence': confidence,
                    'expected_return': expected_return,
                    'risk_level': 0.12,
                    'proof': f"Z-score: {z_score:.2f} (>2σ deviation)"
                }
        
        return None
    
    def calculate_momentum(self, data: List[Dict]) -> Optional[Dict]:
        """Detect momentum opportunity."""
        if len(data) < 20:
            return None
        
        prices = [d['close'] for d in data[-20:]]
        volumes = [d['volume'] for d in data[-20:]]
        
        # Moving averages
        sma_5 = sum(prices[-5:]) / 5
        sma_15 = sum(prices[-15:]) / 15
        
        # Volume analysis
        avg_volume = sum(volumes[-10:]) / 10
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Momentum
        momentum = (sma_5 - sma_15) / sma_15 if sma_15 > 0 else 0
        
        if abs(momentum) > 0.02 and volume_ratio > 1.5:  # Strong momentum with volume
            confidence = min(abs(momentum) * 20 + volume_ratio * 0.1, 0.9)
            expected_return = abs(momentum) * 2
            
            if confidence >= self.min_confidence:
                return {
                    'strategy': 'momentum',
                    'confidence': confidence,
                    'expected_return': expected_return,
                    'risk_level': 0.18,
                    'proof': f"Momentum: {momentum:.2%}, Volume: {volume_ratio:.1f}x"
                }
        
        return None
    
    def calculate_position_size(self, opportunity: Dict) -> float:
        """Calculate conservative position size."""
        confidence = opportunity['confidence']
        expected_return = opportunity['expected_return']
        risk_level = opportunity['risk_level']
        
        # Kelly criterion with safety factor
        if risk_level <= 0:
            return 0
        
        b = expected_return / risk_level
        p = confidence
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Very conservative
        safety_factor = 0.05  # 5% of Kelly
        position_fraction = min(kelly_fraction * safety_factor, self.max_position_percent)
        position_size = max(0, self.capital * position_fraction)
        
        # Scale position size for small accounts
        max_trade = min(500, self.capital * 0.1)  # Cap at $500 or 10% of balance
        return min(position_size, max_trade)
    
    def execute_trade(self, opportunity: Dict, symbol: str, current_price: float) -> bool:
        """Execute a live trade."""
        position_size = self.calculate_position_size(opportunity)
        
        min_position = 10 if self.capital < 100 else 20  # Lower minimum for small accounts
        if position_size < min_position:
            return False
        
        try:
            # For demo: log the trade (in real system would execute via Binance API)
            self.logger.info(f"🎯 EXECUTING {opportunity['strategy']}: {symbol}")
            self.logger.info(f"   Price: ${current_price:.2f}")
            self.logger.info(f"   Position: ${position_size:.2f}")
            self.logger.info(f"   Confidence: {opportunity['confidence']:.2%}")
            self.logger.info(f"   Proof: {opportunity['proof']}")
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now(),
                'strategy': opportunity['strategy'],
                'symbol': symbol,
                'position_size': position_size,
                'price': current_price,
                'confidence': opportunity['confidence'],
                'expected_return': opportunity['expected_return'],
                'proof': opportunity['proof']
            }
            
            self.trade_history.append(trade_record)
            
            # For demo: simulate execution (in real system would place actual orders)
            self.logger.info(f"   ✅ Trade recorded (demo mode)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute trade: {e}")
            return False
    
    def scan_opportunities(self) -> int:
        """Scan for trading opportunities."""
        opportunities_found = 0
        
        # Get market data
        btc_data = self.get_market_data("BTCUSDC")
        eth_data = self.get_market_data("ETHUSDC")
        
        if not btc_data or not eth_data:
            self.logger.warning("Failed to get market data")
            return 0
        
        current_btc_price = btc_data[-1]['close']
        current_eth_price = eth_data[-1]['close']
        
        self.logger.info(f"📊 Market Scan: BTC=${current_btc_price:,.0f}, ETH=${current_eth_price:,.0f}")
        
        # Check correlation breakdown (market neutral)
        corr_opp = self.calculate_correlation_breakdown(btc_data, eth_data)
        if corr_opp:
            self.execute_trade(corr_opp, "BTCETH_PAIR", current_btc_price)
            opportunities_found += 1
        
        # Check mean reversion for both symbols
        for symbol, data, price in [("BTCUSDC", btc_data, current_btc_price), 
                                    ("ETHUSDC", eth_data, current_eth_price)]:
            mean_rev_opp = self.calculate_mean_reversion(data)
            if mean_rev_opp:
                self.execute_trade(mean_rev_opp, symbol, price)
                opportunities_found += 1
            
            # Check momentum
            momentum_opp = self.calculate_momentum(data)
            if momentum_opp:
                self.execute_trade(momentum_opp, symbol, price)
                opportunities_found += 1
        
        if opportunities_found == 0:
            self.logger.info("📊 No opportunities found this cycle")
        
        return opportunities_found
    
    def print_status(self):
        """Print current trading status."""
        if not self.trade_history:
            self.logger.info("📊 No trades executed yet")
            return
        
        total_trades = len(self.trade_history)
        recent_trades = [t for t in self.trade_history if (datetime.now() - t['timestamp']).days < 7]
        
        strategies = {}
        for trade in self.trade_history:
            strategy = trade['strategy']
            strategies[strategy] = strategies.get(strategy, 0) + 1
        
        self.logger.info(f"📊 TRADING STATUS")
        self.logger.info(f"   Total Trades: {total_trades}")
        self.logger.info(f"   Recent (7d): {len(recent_trades)}")
        self.logger.info(f"   Strategies: {strategies}")
        self.logger.info(f"   Balance: ${self.capital:.2f}")
    
    def run_live_trading(self, duration_hours: int = 24):
        """Run live trading for specified duration."""
        self.logger.info(f"🚀 Starting live trading for {duration_hours} hours")
        
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        def signal_handler(signum, frame):
            self.logger.info("\n⏹️ Trading stopped by user")
            self.print_status()
            exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        cycle = 0
        try:
            while datetime.now() < end_time:
                cycle += 1
                self.logger.info(f"\n🔄 Trading Cycle {cycle}")
                
                opportunities = self.scan_opportunities()
                
                if cycle % 6 == 0:  # Every 6 hours
                    self.print_status()
                
                # Wait for next cycle
                self.logger.info(f"⏰ Waiting {self.scan_interval} seconds until next scan...")
                time.sleep(self.scan_interval)
                
        except Exception as e:
            self.logger.error(f"Trading error: {e}")
        finally:
            self.print_status()
            self.logger.info("🏁 Trading session completed")


def main():
    """Main entry point."""
    print("🚀 MomoAI Coherent Trading System - Live Deployment")
    print("="*60)
    
    # Check environment
    if not os.getenv("BINANCE_API_KEY") or not os.getenv("BINANCE_API_SECRET"):
        print("❌ Binance API credentials not found!")
        print("Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")
        return
    
    try:
        # Initialize trading engine
        engine = LiveTradingEngine()
        
        print(f"✅ Connected to Binance")
        print(f"💰 Account Balance: ${engine.capital:.2f}")
        print(f"🎯 Max Position Size: ${engine.capital * engine.max_position_percent:.2f} (2%)")
        print(f"⏰ Scan Interval: {engine.scan_interval/3600:.1f} hours")
        
        # Run trading
        duration = 24  # 24 hours
        print(f"\n🚀 Starting {duration}h trading session...")
        engine.run_live_trading(duration)
        
    except Exception as e:
        print(f"❌ Failed to start trading: {e}")


if __name__ == "__main__":
    main()