#!/usr/bin/env python3
"""
Simple Integration Test - Basic functionality without complex dependencies

Tests core backtesting integration step by step with minimal external dependencies.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add module paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_imports():
    """Test that all modules can be imported."""
    print("1. Testing Basic Imports...")
    
    try:
        # Test historical data components
        from backtesting.historical_data_engine import OHLCV, DataQualityMetrics, AssetDataSeries
        print("✓ Historical data types imported")
        
        # Test market simulator components  
        from backtesting.market_simulator import OrderRequest, OrderSide, OrderType, MarketSimulator
        print("✓ Market simulator components imported")
        
        # Test strategy components
        from strategies.altcoin_correlation_matrix import AltcoinCorrelationDetector
        from risk.position_sizing import KellyPositionSizer, VolatilityAdjustedSizer
        print("✓ Strategy components imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_data_structures():
    """Test basic data structure creation and validation."""
    print("\n2. Testing Data Structures...")
    
    try:
        from backtesting.historical_data_engine import OHLCV, DataQualityMetrics
        
        # Test valid OHLCV
        ohlcv = OHLCV(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0
        )
        print("✓ Valid OHLCV created")
        
        # Test quality metrics
        quality = DataQualityMetrics(
            total_points=1000,
            missing_points=10,
            gap_count=2,
            max_gap_hours=1.0,
            price_anomalies=5,
            volume_anomalies=3,
            completeness_ratio=0.99,
            quality_score=0.95
        )
        
        print(f"✓ Quality metrics: {quality.quality_score}")
        print(f"✓ Is acceptable: {quality.is_acceptable()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_market_simulation():
    """Test market simulation without external dependencies."""
    print("\n3. Testing Market Simulation...")
    
    try:
        from backtesting.market_simulator import MarketSimulator, OrderRequest, OrderSide, OrderType
        
        # Create simulator
        simulator = MarketSimulator(use_realistic_execution=False)
        
        # Create test order
        order = OrderRequest(
            timestamp=datetime.now(),
            symbol="TESTUSDC",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=1.0
        )
        
        # Execute order
        result = simulator.execute_order(
            order=order,
            market_price=100.0,
            volume_24h=1000000.0,
            volatility=0.02
        )
        
        print(f"✓ Order executed: {result.status}")
        print(f"✓ Fill price: {result.average_fill_price}")
        print(f"✓ Quantity filled: {result.total_filled_qty}")
        
        # Test execution stats
        stats = simulator.get_execution_statistics()
        print(f"✓ Execution stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Market simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_initialization():
    """Test strategy component initialization."""
    print("\n4. Testing Strategy Initialization...")
    
    try:
        from strategies.altcoin_correlation_matrix import AltcoinCorrelationDetector
        from risk.position_sizing import KellyPositionSizer, VolatilityAdjustedSizer
        
        # Test correlation detector
        detector = AltcoinCorrelationDetector(min_confidence=0.75)
        print("✓ Correlation detector initialized")
        
        # Test position sizer
        kelly = KellyPositionSizer(max_position=0.02)
        vol_sizer = VolatilityAdjustedSizer(kelly_sizer=kelly)
        print("✓ Position sizer initialized")
        
        # Test simple calculation
        kelly_fraction = kelly.calculate_kelly_fraction(
            win_prob=0.6,
            expected_return=0.05,
            risk_level=0.02
        )
        print(f"✓ Kelly fraction calculated: {kelly_fraction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_backtesting_flow():
    """Test a simplified backtesting flow with mock data."""
    print("\n5. Testing Mock Backtesting Flow...")
    
    try:
        from backtesting.historical_data_engine import OHLCV, AssetDataSeries, DataQualityMetrics
        from backtesting.market_simulator import MarketSimulator, OrderRequest, OrderSide, OrderType
        from strategies.altcoin_correlation_matrix import AltcoinCorrelationDetector
        
        # Create mock historical data
        mock_data = [
            OHLCV(datetime.now() - timedelta(hours=i), 100+i, 105+i, 95+i, 102+i, 1000)
            for i in range(10)
        ]
        
        quality = DataQualityMetrics(10, 0, 0, 0, 0, 0, 1.0, 0.99)
        
        mock_series = AssetDataSeries(
            symbol="TESTUSDC",
            timeframe="1h",
            data=mock_data,
            quality_metrics=quality,
            source="Mock",
            last_updated=datetime.now()
        )
        
        print("✓ Mock data series created")
        
        # Test data conversion
        df = mock_series.to_dataframe()
        print(f"✓ DataFrame created with {len(df)} rows")
        
        # Initialize components
        detector = AltcoinCorrelationDetector(min_confidence=0.75)
        simulator = MarketSimulator(use_realistic_execution=False)
        
        # Test opportunity detection with mock prices
        mock_prices = {
            'BTCUSDC': 50000.0,
            'ETHUSDC': 3000.0,
            'ADAUSDC': 0.5
        }
        
        # Convert to market_data format expected by strategy
        market_data = {}
        for symbol, price in mock_prices.items():
            market_data[symbol] = [{'close': price, 'timestamp': datetime.now()}] * 50
        
        opportunities = detector.find_best_opportunities(market_data)
        print(f"✓ Found {len(opportunities)} opportunities (expected: few or none with mock data)")
        
        # Test order execution for each opportunity
        for opp in opportunities[:1]:  # Test first one only
            order = OrderRequest(
                timestamp=datetime.now(),
                symbol=opp.pair1,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=0.1
            )
            
            result = simulator.execute_order(
                order=order,
                market_price=mock_prices.get(opp.pair1, 100.0),
                volume_24h=1000000.0,
                volatility=0.02
            )
            
            print(f"✓ Test order for {opp.pair1}: {result.status}")
        
        print("✓ Mock backtesting flow completed")
        return True
        
    except Exception as e:
        print(f"❌ Mock backtesting flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("MomoAI Funding System - Simple Integration Test")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_data_structures,
        test_market_simulation,
        test_strategy_initialization,
        test_mock_backtesting_flow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✓ Core backtesting integration working")
        print("✓ Ready for advanced testing")
        status = "SUCCESS"
    elif passed >= 4:
        print("\n⚠️ MOSTLY WORKING with minor issues")
        print("✓ Core functionality operational")
        print("⚠️ Some components need debugging")
        status = "PARTIAL"
    else:
        print("\n❌ SIGNIFICANT ISSUES")
        print("❌ Core integration problems")
        print("❌ Requires major fixes")
        status = "FAILED"
    
    print(f"\nFINAL STATUS: {status}")
    return status == "SUCCESS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)