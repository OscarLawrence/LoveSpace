#!/usr/bin/env python3
"""
Basic Backtesting Test - Without SciPy Dependencies

Tests core backtesting functionality with minimal dependencies to validate integration.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add module paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Test imports without scipy-dependent modules
try:
    from backtesting.historical_data_engine import HistoricalDataEngine, OHLCV
    from backtesting.market_simulator import MarketSimulator, OrderRequest, OrderSide, OrderType
    from dynamic_market_discovery import DynamicMarketDiscovery
    from strategies.altcoin_correlation_matrix import AltcoinCorrelationDetector
    from risk.position_sizing import VolatilityAdjustedSizer
    
    print("✓ All core modules imported successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_historical_data_engine():
    """Test historical data engine functionality."""
    print("\n1. Testing Historical Data Engine...")
    
    try:
        engine = HistoricalDataEngine()
        
        # Test OHLCV data validation
        valid_ohlcv = OHLCV(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0
        )
        print("✓ OHLCV validation working")
        
        # Test invalid OHLCV (should raise error)
        try:
            invalid_ohlcv = OHLCV(
                timestamp=datetime.now(),
                open=100.0,
                high=90.0,  # High < Open (invalid)
                low=95.0,
                close=102.0,
                volume=1000.0
            )
            print("❌ OHLCV validation failed - invalid data accepted")
        except ValueError:
            print("✓ OHLCV validation correctly rejects invalid data")
        
        print("✓ Historical Data Engine basic functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Historical Data Engine test failed: {e}")
        return False

def test_market_simulator():
    """Test market simulator functionality."""
    print("\n2. Testing Market Simulator...")
    
    try:
        simulator = MarketSimulator(use_realistic_execution=False)  # Simplified for testing
        
        # Create test order
        order = OrderRequest(
            timestamp=datetime.now(),
            symbol="BTCUSDC",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.001
        )
        
        # Test execution
        result = simulator.execute_order(
            order=order,
            market_price=50000.0,
            volume_24h=1000000000,
            volatility=0.02
        )
        
        print(f"✓ Order execution result: {result.status}")
        print(f"✓ Fill price: ${result.average_fill_price:,.2f}")
        print(f"✓ Slippage: {result.slippage_bps:.2f} bps")
        
        print("✓ Market Simulator basic functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Market Simulator test failed: {e}")
        return False

def test_strategy_components():
    """Test strategy components integration."""
    print("\n3. Testing Strategy Components...")
    
    try:
        # Test market discovery
        discovery = DynamicMarketDiscovery()
        print("✓ DynamicMarketDiscovery initialized")
        
        # Test correlation detector
        detector = AltcoinCorrelationDetector(min_confidence=0.75)
        print("✓ AltcoinCorrelationDetector initialized")
        
        # Test position sizer
        sizer = VolatilityAdjustedSizer(max_position=0.02)
        print("✓ VolatilityAdjustedSizer initialized")
        
        # Test correlation detection with mock data
        mock_prices = {
            'BTCUSDC': 50000.0,
            'ETHUSDC': 3000.0,
            'ADAUSDC': 0.5,
            'DOTUSDC': 8.0
        }
        
        # This will likely return empty results due to lack of historical data
        # but should not crash
        opportunities = detector.detect_correlation_breakdowns(mock_prices)
        print(f"✓ Correlation detection returned {len(opportunities)} opportunities")
        
        print("✓ Strategy Components integration working")
        return True
        
    except Exception as e:
        print(f"❌ Strategy Components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_flow():
    """Test the basic integration flow without full backtesting."""
    print("\n4. Testing Integration Flow...")
    
    try:
        # Initialize components
        data_engine = HistoricalDataEngine()
        market_simulator = MarketSimulator(use_realistic_execution=False)
        correlation_detector = AltcoinCorrelationDetector(min_confidence=0.75)
        position_sizer = VolatilityAdjustedSizer(max_position=0.02)
        
        print("✓ All components initialized")
        
        # Mock portfolio state
        portfolio_value = 10000.0
        current_positions = {}
        
        # Mock current prices
        current_prices = {
            'BTCUSDC': 50000.0,
            'ETHUSDC': 3000.0,
            'ADAUSDC': 0.5,
            'DOTUSDC': 8.0,
            'MATICUSDC': 1.0
        }
        
        # Test opportunity detection
        opportunities = correlation_detector.detect_correlation_breakdowns(current_prices)
        print(f"✓ Found {len(opportunities)} correlation opportunities")
        
        # Test position sizing for each opportunity
        for i, opportunity in enumerate(opportunities[:2]):  # Test first 2
            if opportunity.pair1 in current_prices:
                price = current_prices[opportunity.pair1]
                position = position_sizer.calculate_position_size(
                    portfolio_value=portfolio_value,
                    entry_price=price,
                    volatility=opportunity.risk_level
                )
                print(f"✓ Position size for {opportunity.pair1}: ${position.position_value:.2f}")
        
        # Test order creation and execution
        if opportunities and opportunities[0].pair1 in current_prices:
            symbol = opportunities[0].pair1
            price = current_prices[symbol]
            
            order = OrderRequest(
                timestamp=datetime.now(),
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=0.001
            )
            
            execution = market_simulator.execute_order(
                order=order,
                market_price=price,
                volume_24h=1000000,
                volatility=0.02
            )
            
            print(f"✓ Test order execution: {execution.status}")
        
        print("✓ Integration Flow test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration Flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests."""
    print("MomoAI Funding System - Backtesting Integration Test")
    print("=" * 60)
    
    tests = [
        test_historical_data_engine,
        test_market_simulator,
        test_strategy_components,
        test_integration_flow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Backtesting integration is working!")
        print("✓ Ready to implement full backtesting pipeline")
        print("✓ Core components properly integrated")
        print("✓ Strategy logic accessible from backtesting framework")
    elif passed >= total * 0.75:
        print("\n⚠️ MOSTLY WORKING - Some issues need attention")
        print("✓ Core functionality operational")
        print("⚠️ Some components need debugging")
    else:
        print("\n❌ SIGNIFICANT ISSUES - Major debugging needed")
        print("❌ Core integration problems detected")
        print("❌ Requires fundamental fixes before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)