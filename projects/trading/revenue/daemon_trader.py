#!/usr/bin/env python3
"""
MomoAI Trading Daemon Worker
The actual trading engine that runs continuously in the background.
"""

import os
import sys
import time
import json
import signal
import logging
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


class ContinuousTrader:
    """Continuous trading engine that runs in the background."""
    
    def __init__(self):
        self.status_file = Path.cwd() / "trader_status.json"
        self.trade_log = Path.cwd() / "trades.jsonl"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('daemon_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize trading components
        self.connector = create_binance_connector()
        if not self.connector:
            raise ValueError("Failed to connect to Binance")
        
        # Get account balance
        balances = self.connector.get_account_info()
        USDC_balance = balances.get("USDC") or balances.get("USDC") or balances.get("BUSD")
        
        if not USDC_balance or USDC_balance.total < 1:
            raise ValueError(f"Insufficient balance: ${USDC_balance.total if USDC_balance else 0:.2f}")
        
        self.start_balance = USDC_balance.total
        self.current_balance = self.start_balance
        self.total_pnl = 0.0
        self.trade_history = []
        
        # Trading parameters
        self.scan_interval = 1800  # 30 minutes (more frequent than 1 hour)
        self.min_confidence = 0.75  # Slightly higher for live trading
        self.max_position_percent = 0.02  # 2% max per trade
        self.symbols = ["BTCUSDC", "ETHUSDC"]
        
        # State management
        self.running = True
        self.cycle_count = 0
        
        self.logger.info(f"🚀 Continuous Trader initialized with ${self.start_balance:.2f}")
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"📨 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def update_status(self):
        """Update status file with current state."""
        try:
            status = {
                'status': 'running',
                'start_balance': self.start_balance,
                'current_balance': self.current_balance,
                'total_pnl': self.total_pnl,
                'total_trades': len(self.trade_history),
                'last_update': datetime.now().isoformat(),
                'cycle_count': self.cycle_count,
                'recent_trades': self.trade_history[-10:] if self.trade_history else []
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    def log_trade(self, trade_data: Dict):
        """Log trade to JSONL file."""
        try:
            with open(self.trade_log, 'a') as f:
                json.dump(trade_data, f, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to log trade: {e}")
    
    def get_market_data(self, symbol: str) -> List[Dict]:
        """Get market data for analysis."""
        try:
            klines = self.connector.get_kline_data(symbol, "1h", 100)
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
        """Detect correlation breakdown (same as deploy_trading_system.py)."""
        if len(btc_data) < 50 or len(eth_data) < 50:
            return None
        
        # Recent correlation (20 periods)
        btc_prices = [d['close'] for d in btc_data[-20:]]
        eth_prices = [d['close'] for d in eth_data[-20:]]
        
        btc_returns = [(btc_prices[i] - btc_prices[i-1]) / btc_prices[i-1] for i in range(1, len(btc_prices))]
        eth_returns = [(eth_prices[i] - eth_prices[i-1]) / eth_prices[i-1] for i in range(1, len(eth_prices))]
        
        if len(btc_returns) < 10:
            return None
        
        # Calculate correlations (same logic as before)
        mean_btc = sum(btc_returns) / len(btc_returns)
        mean_eth = sum(eth_returns) / len(eth_returns)
        
        numerator = sum((br - mean_btc) * (er - mean_eth) for br, er in zip(btc_returns, eth_returns))
        btc_var = sum((br - mean_btc) ** 2 for br in btc_returns) ** 0.5
        eth_var = sum((er - mean_eth) ** 2 for er in eth_returns) ** 0.5
        
        if btc_var == 0 or eth_var == 0:
            return None
        
        current_corr = numerator / (btc_var * eth_var)
        
        # Historical correlation
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
        
        if breakdown > 0.4:
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
        """Mean reversion strategy (same logic as before)."""
        if len(data) < 30:
            return None
        
        prices = [d['close'] for d in data[-30:]]
        current_price = prices[-1]
        
        sma_20 = sum(prices[-20:]) / 20
        variance = sum((p - sma_20) ** 2 for p in prices[-20:]) / 20
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return None
        
        z_score = abs(current_price - sma_20) / std_dev
        
        if z_score > 2.0:
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
    
    def execute_trade(self, opportunity: Dict, symbol: str, current_price: float) -> bool:
        """Execute trade (demo mode - logs only)."""
        # Calculate position size
        confidence = opportunity['confidence']
        expected_return = opportunity['expected_return']
        risk_level = opportunity['risk_level']
        
        # Conservative Kelly sizing
        b = expected_return / risk_level if risk_level > 0 else 0
        p = confidence
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        safety_factor = 0.05
        position_fraction = min(kelly_fraction * safety_factor, self.max_position_percent)
        position_size = max(0, self.current_balance * position_fraction)
        
        min_trade = 10 if self.current_balance < 100 else 20
        if position_size < min_trade:
            return False
        
        # For now: simulate trade execution (in production would use real API)
        simulated_success = confidence > 0.8  # Higher confidence = higher success rate
        
        if simulated_success:
            simulated_pnl = position_size * expected_return * 0.7  # 70% of expected
        else:
            simulated_pnl = -(position_size * risk_level * 0.8)  # 80% of risk
        
        # Update balances
        self.current_balance += simulated_pnl
        self.total_pnl += simulated_pnl
        
        # Log trade
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'strategy': opportunity['strategy'],
            'symbol': symbol,
            'price': current_price,
            'position_size': position_size,
            'confidence': confidence,
            'expected_return': expected_return,
            'simulated_pnl': simulated_pnl,
            'success': simulated_success,
            'proof': opportunity['proof'],
            'balance_after': self.current_balance
        }
        
        self.trade_history.append(trade_data)
        self.log_trade(trade_data)
        
        result_emoji = "✅" if simulated_success else "❌"
        self.logger.info(f"{result_emoji} {opportunity['strategy']}: {symbol} @ ${current_price:.2f}")
        self.logger.info(f"   Position: ${position_size:.2f}, P&L: ${simulated_pnl:+.2f}")
        self.logger.info(f"   Balance: ${self.current_balance:.2f}")
        
        return True
    
    def trading_cycle(self):
        """Run one trading cycle."""
        self.cycle_count += 1
        self.logger.info(f"🔄 Trading Cycle {self.cycle_count}")
        
        # Get market data
        btc_data = self.get_market_data("BTCUSDC")
        eth_data = self.get_market_data("ETHUSDC")
        
        if not btc_data or not eth_data:
            self.logger.warning("⚠️ Failed to get market data")
            return
        
        current_btc = btc_data[-1]['close']
        current_eth = eth_data[-1]['close']
        
        self.logger.info(f"📊 BTC: ${current_btc:,.0f}, ETH: ${current_eth:,.0f}")
        
        opportunities_found = 0
        
        # Check correlation breakdown
        corr_opp = self.calculate_correlation_breakdown(btc_data, eth_data)
        if corr_opp:
            if self.execute_trade(corr_opp, "BTCETH_PAIR", current_btc):
                opportunities_found += 1
        
        # Check mean reversion for both symbols
        for symbol, data, price in [("BTCUSDC", btc_data, current_btc), ("ETHUSDC", eth_data, current_eth)]:
            mean_rev_opp = self.calculate_mean_reversion(data)
            if mean_rev_opp:
                if self.execute_trade(mean_rev_opp, symbol, price):
                    opportunities_found += 1
        
        if opportunities_found == 0:
            self.logger.info("📊 No high-confidence opportunities found")
        
        # Update status
        self.update_status()
        
        # Performance summary every 10 cycles
        if self.cycle_count % 10 == 0:
            total_return = (self.current_balance - self.start_balance) / self.start_balance
            self.logger.info(f"📈 Performance Summary (Cycle {self.cycle_count}):")
            self.logger.info(f"   Total Return: {total_return*100:+.2f}%")
            self.logger.info(f"   Total Trades: {len(self.trade_history)}")
            self.logger.info(f"   Current Balance: ${self.current_balance:.2f}")
    
    def run(self):
        """Main trading loop."""
        self.logger.info("🚀 Starting continuous trading...")
        
        while self.running:
            try:
                self.trading_cycle()
                
                # Sleep in chunks to allow graceful shutdown
                for _ in range(self.scan_interval // 30):  # 30-second chunks
                    if not self.running:
                        break
                    time.sleep(30)
                    
            except Exception as e:
                self.logger.error(f"❌ Trading cycle error: {e}")
                # Continue running despite errors
                time.sleep(60)  # Wait 1 minute before retry
        
        # Final status update
        self.update_status()
        self.logger.info("🏁 Continuous trading stopped")


def main():
    """Main entry point for daemon."""
    try:
        trader = ContinuousTrader()
        trader.run()
    except Exception as e:
        logging.error(f"❌ Daemon startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()