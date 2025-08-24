#!/usr/bin/env python3
"""
Scientific Trading System - Real Capital, Mathematical Rigor
Orchestrates micro-modules with formal contracts for profitable trading.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import time

# Add module paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from execution.binance_connector import create_binance_connector, MarketData
from strategies.correlation_breakdown import create_correlation_detector, MarketData as StrategyMarketData, TradingSignal
from risk.position_sizing import create_position_sizer

# Add formal contracts
sys.path.insert(0, str(current_dir.parent.parent / "MomoAI/projects/coherence/formal_contracts"))
from contract_language import coherence_contract, ComplexityClass

class ScientificTrader:
    """
    Scientific trading system with mathematical guarantees.
    
    Architecture:
    - Micro-modules with formal contracts
    - Real Binance API execution
    - Statistical validation of all strategies
    - Risk management with mathematical proofs
    """
    
    def __init__(self, min_confidence: float = 0.75, max_position: float = 0.02):
        """Initialize scientific trader with risk parameters."""
        self.connector = create_binance_connector()
        self.correlation_detector = create_correlation_detector(min_confidence=min_confidence)
        self.position_sizer = create_position_sizer(max_position=max_position)
        
        if not self.connector:
            raise ValueError("Failed to connect to Binance API")
        
        print(f"🧬 Scientific Trader initialized")
        print(f"   Min Confidence: {min_confidence:.1%}")
        print(f"   Max Position: {max_position:.1%}")
    
    @coherence_contract(
        input_types={"symbol": "str", "interval": "str", "limit": "int"},
        output_type="List[MarketData]",
        requires=["len(symbol) > 0", "limit > 0"],
        ensures=["len(result) <= limit"],
        complexity_time=ComplexityClass.CONSTANT,  # API call
        pure=False  # Network side effect
    )
    def get_market_data(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[MarketData]:
        """Fetch market data from Binance."""
        klines = self.connector.get_kline_data(symbol, interval, limit)
        
        if not klines:
            return []
        
        market_data = []
        for kline in klines:
            data = MarketData(
                timestamp=kline.get('open_time', 0) / 1000,  # Convert to seconds
                close=kline.get('close', 0.0),
                volume=kline.get('volume', 0.0)
            )
            market_data.append(data)
        
        return market_data
    
    def convert_to_strategy_data(self, market_data: List[MarketData]) -> List[StrategyMarketData]:
        """Convert market data to strategy format."""
        return [
            StrategyMarketData(
                timestamp=d.timestamp,
                close=d.close,
                volume=d.volume
            )
            for d in market_data
        ]
    
    @coherence_contract(
        input_types={},
        output_type="Optional[TradingSignal]",
        requires=[],
        ensures=["result is None or (0.0 <= result.confidence <= 1.0)"],
        complexity_time=ComplexityClass.LINEAR,
        pure=False  # Market data fetch
    )
    def scan_for_opportunities(self) -> Optional[TradingSignal]:
        """
        Scan market for trading opportunities using mathematical strategies.
        
        Current strategy: BTC/ETH correlation breakdown detection
        """
        print("🔍 Scanning for opportunities...")
        
        # Get market data for BTC and ETH
        btc_data = self.get_market_data("BTCUSDC", "1h", 100)
        eth_data = self.get_market_data("ETHUSDC", "1h", 100)
        
        if len(btc_data) < 50 or len(eth_data) < 50:
            print("❌ Insufficient market data")
            return None
        
        # Ensure same length
        min_len = min(len(btc_data), len(eth_data))
        btc_data = btc_data[-min_len:]
        eth_data = eth_data[-min_len:]
        
        # Convert to strategy format
        btc_strategy_data = self.convert_to_strategy_data(btc_data)
        eth_strategy_data = self.convert_to_strategy_data(eth_data)
        
        # Detect correlation breakdown
        signal = self.correlation_detector.detect_breakdown(btc_strategy_data, eth_strategy_data)
        
        if signal:
            print(f"📊 {signal.strategy} signal detected:")
            print(f"   Confidence: {signal.confidence:.1%}")
            print(f"   Expected Return: {signal.expected_return:.2%}")
            print(f"   Mathematical Proof: {signal.mathematical_proof}")
        else:
            print("📊 No high-confidence opportunities found")
        
        return signal
    
    def get_available_capital(self) -> float:
        """Get available trading capital in USDC."""
        balances = self.connector.get_account_info()
        
        # Check for USDC, USDC, or BUSD
        for asset in ["USDC", "USDC", "BUSD"]:
            if asset in balances:
                return balances[asset].free
        
        return 0.0
    
    def execute_signal(self, signal: TradingSignal) -> bool:
        """
        Execute trading signal with proper risk management.
        
        Currently logs the trade decision. Real execution to be implemented
        after thorough testing.
        """
        capital = self.get_available_capital()
        
        if capital < 10:
            print(f"❌ Insufficient capital: ${capital:.2f}")
            return False
        
        # Calculate position size
        position_size = self.position_sizer.calculate_position_size(
            signal.confidence,
            signal.expected_return,
            signal.risk_level,
            capital
        )
        
        if not self.position_sizer.is_position_viable(position_size):
            print(f"❌ Position size too small: ${position_size:.2f}")
            return False
        
        # Log the trading decision (real execution to be added)
        print(f"💰 TRADE DECISION:")
        print(f"   Strategy: {signal.strategy}")
        print(f"   Position Size: ${position_size:.2f} ({position_size/capital:.1%} of capital)")
        print(f"   Risk: ${position_size * signal.risk_level:.2f}")
        print(f"   Expected Profit: ${position_size * signal.expected_return:.2f}")
        print(f"   Mathematical Proof: {signal.mathematical_proof}")
        
        # TODO: Implement real order execution
        print("⚠️  PAPER TRADING MODE - No real orders executed")
        
        return True
    
    def run_trading_cycle(self) -> None:
        """Run one complete trading cycle."""
        print(f"\n🔄 Trading Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Scan for opportunities
            signal = self.scan_for_opportunities()
            
            if signal:
                # Execute if viable
                self.execute_signal(signal)
            
        except Exception as e:
            print(f"❌ Trading cycle error: {e}")
    
    def run_continuous(self, interval_minutes: int = 30) -> None:
        """Run continuous trading with specified interval."""
        print(f"🚀 Starting continuous trading (every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_trading_cycle()
                print(f"💤 Sleeping for {interval_minutes} minutes...\n")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Trading stopped by user")


def main():
    """Main entry point for scientific trader."""
    print("🧬 MomoAI Scientific Trading System")
    print("Mathematical rigor • Real capital • Formal contracts")
    print("="*60)
    
    try:
        trader = ScientificTrader(min_confidence=0.75, max_position=0.02)
        
        # Run one cycle to test
        trader.run_trading_cycle()
        
        # Ask user if they want continuous trading
        response = input("\nStart continuous trading? (y/n): ").lower().strip()
        if response == 'y':
            trader.run_continuous(interval_minutes=30)
        
    except Exception as e:
        print(f"❌ System error: {e}")


if __name__ == "__main__":
    main()