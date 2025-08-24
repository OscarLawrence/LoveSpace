#!/usr/bin/env python3
"""
Backtesting Runner - Scientific Validation of Correlation Breakdown Strategy

Runs comprehensive backtesting with walk-forward validation to ensure
statistical significance and robustness of the trading strategy.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add module paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from backtesting.coherent_backtester import CoherentBacktester, BacktestConfig
from dynamic_market_discovery import DynamicMarketDiscovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_basic_backtest():
    """Run basic backtesting without parameter optimization."""
    logger.info("Starting basic backtesting...")
    
    # Initialize backtester
    backtester = CoherentBacktester(cache_dir="backtest_cache")
    
    # Get optimal asset universe from live system
    market_discovery = DynamicMarketDiscovery()
    optimal_assets = market_discovery.discover_optimal_assets(max_assets=17)
    symbols = [asset.symbol for asset in optimal_assets[:10]]  # Top 10 for initial test
    
    logger.info(f"Testing with symbols: {symbols}")
    
    # Configure backtest parameters
    config = BacktestConfig(
        start_date=datetime.now() - timedelta(days=90),  # 3 months
        end_date=datetime.now() - timedelta(days=1),
        initial_capital=10000.0,  # $10K test capital
        symbols=symbols,
        timeframe="1h",
        correlation_threshold=0.35,  # From live system analysis
        min_confidence=0.75,
        max_position_size=0.02,  # 2% max position
        use_realistic_execution=True,
        include_fees=True
    )
    
    try:
        # Run backtest
        result = backtester.run_backtest(config)
        
        # Display results
        print("\n" + "="*60)
        print("BACKTESTING RESULTS")
        print("="*60)
        print(f"Period: {config.start_date.strftime('%Y-%m-%d')} to {config.end_date.strftime('%Y-%m-%d')}")
        print(f"Initial Capital: ${config.initial_capital:,.2f}")
        print(f"Symbols Tested: {len(symbols)}")
        print()
        
        metrics = result.performance_metrics
        print("PERFORMANCE METRICS:")
        print(f"  Total Return: {metrics.total_return:.2%}")
        print(f"  Annualized Return: {metrics.annualized_return:.2%}")
        print(f"  Volatility: {metrics.volatility:.2%}")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"  Sortino Ratio: {metrics.sortino_ratio:.2f}")
        print(f"  Calmar Ratio: {metrics.calmar_ratio:.2f}")
        print(f"  Maximum Drawdown: {metrics.max_drawdown:.2%}")
        print(f"  Recovery Factor: {metrics.recovery_factor:.2f}")
        print()
        
        print("TRADE STATISTICS:")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Win Rate: {metrics.win_rate:.1%}")
        print(f"  Average Win: {metrics.avg_win:.2%}")
        print(f"  Average Loss: {metrics.avg_loss:.2%}")
        print(f"  Profit Factor: {metrics.profit_factor:.2f}")
        print()
        
        print("RISK METRICS:")
        print(f"  95% VaR: {metrics.var_95:.2%}")
        print(f"  99% VaR: {metrics.var_99:.2%}")
        print(f"  95% Expected Shortfall: {metrics.expected_shortfall_95:.2%}")
        print()
        
        print("STATISTICAL SIGNIFICANCE:")
        print(f"  t-statistic: {metrics.t_statistic:.2f}")
        print(f"  p-value: {metrics.p_value:.4f}")
        print(f"  Statistically Significant: {metrics.is_statistically_significant()}")
        print(f"  95% Confidence Interval: ({metrics.confidence_interval_95[0]:.4f}, {metrics.confidence_interval_95[1]:.4f})")
        print()
        
        print("EXECUTION STATISTICS:")
        for key, value in result.execution_stats.items():
            print(f"  {key}: {value}")
        
        # Validation check
        print("\nVALIDATION CHECK:")
        is_profitable = metrics.total_return > 0
        is_significant = metrics.is_statistically_significant()
        acceptable_sharpe = metrics.sharpe_ratio > 1.0
        acceptable_drawdown = metrics.max_drawdown > -0.20  # Max 20% drawdown
        
        print(f"  ✓ Profitable: {is_profitable}")
        print(f"  ✓ Statistically Significant: {is_significant}")
        print(f"  ✓ Good Sharpe Ratio (>1.0): {acceptable_sharpe}")
        print(f"  ✓ Acceptable Drawdown (<20%): {acceptable_drawdown}")
        
        overall_success = is_profitable and is_significant and acceptable_sharpe and acceptable_drawdown
        print(f"\n  OVERALL VALIDATION: {'PASS' if overall_success else 'FAIL'}")
        
        return result
        
    except Exception as e:
        logger.error(f"Backtesting failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_walk_forward_validation():
    """Run walk-forward validation with parameter optimization."""
    logger.info("Starting walk-forward validation...")
    
    # Initialize backtester
    backtester = CoherentBacktester(cache_dir="backtest_cache")
    
    # Get optimal asset universe
    market_discovery = DynamicMarketDiscovery()
    optimal_assets = market_discovery.discover_optimal_assets(max_assets=17)
    symbols = [asset.symbol for asset in optimal_assets[:8]]  # Smaller set for validation
    
    logger.info(f"Walk-forward validation with symbols: {symbols}")
    
    # Base configuration
    base_config = BacktestConfig(
        start_date=datetime.now() - timedelta(days=180),  # 6 months
        end_date=datetime.now() - timedelta(days=1),
        initial_capital=10000.0,
        symbols=symbols,
        timeframe="1h",
        use_realistic_execution=True,
        include_fees=True
    )
    
    # Parameter grid for optimization
    parameter_grid = {
        'correlation_threshold': [0.30, 0.35, 0.40],
        'min_confidence': [0.70, 0.75, 0.80],
        'max_position_size': [0.015, 0.020, 0.025]
    }
    
    try:
        # Run walk-forward validation
        result = backtester.run_walk_forward_validation(
            base_config=base_config,
            parameter_grid=parameter_grid,
            train_months=4,  # 4 month training
            test_months=1    # 1 month testing
        )
        
        # Display validation results
        print("\n" + "="*70)
        print("WALK-FORWARD VALIDATION RESULTS")
        print("="*70)
        
        if result.validation_results:
            val_results = result.validation_results
            
            print(f"Validation Periods: {len(val_results.validation_periods)}")
            print(f"Overfitting Score: {val_results.overfitting_score:.3f} (lower is better)")
            print(f"Strategy Robustness: {'ROBUST' if val_results.is_robust else 'QUESTIONABLE'}")
            print()
            
            print("OVERALL METRICS (Out-of-Sample):")
            for key, value in val_results.overall_metrics.items():
                print(f"  {key}: {value:.4f}")
            print()
            
            print("STABILITY METRICS:")
            for key, value in val_results.stability_metrics.items():
                print(f"  {key}: {value:.4f}")
            print()
            
            print("INDIVIDUAL PERIOD RESULTS:")
            for i, period_result in enumerate(val_results.validation_periods):
                print(f"  Period {i+1}:")
                print(f"    Train Return: {period_result.train_metrics.get('annualized_return', 0):.2%}")
                print(f"    Test Return: {period_result.test_metrics.get('annualized_return', 0):.2%}")
                print(f"    Test Sharpe: {period_result.test_metrics.get('sharpe_ratio', 0):.2f}")
                print(f"    Degradation: {period_result.performance_degradation:.2%}")
                print(f"    Parameters: {period_result.parameter_set}")
                print()
        
        # Display final optimized results
        print("FINAL OPTIMIZED BACKTEST:")
        metrics = result.performance_metrics
        print(f"  Optimized Return: {metrics.annualized_return:.2%}")
        print(f"  Optimized Sharpe: {metrics.sharpe_ratio:.2f}")
        print(f"  Optimized Drawdown: {metrics.max_drawdown:.2%}")
        print(f"  Statistical Significance: {metrics.is_statistically_significant()}")
        
        return result
        
    except Exception as e:
        logger.error(f"Walk-forward validation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("MomoAI Funding System - Scientific Backtesting")
    print("=" * 50)
    
    # Run basic backtest first
    print("1. Running basic backtesting...")
    basic_result = run_basic_backtest()
    
    if basic_result and basic_result.performance_metrics.is_statistically_significant():
        print("\n✓ Basic backtest shows statistical significance. Proceeding to validation...")
        
        # Run walk-forward validation
        print("\n2. Running walk-forward validation...")
        validation_result = run_walk_forward_validation()
        
        if validation_result and validation_result.validation_results:
            if validation_result.validation_results.is_robust:
                print("\n🎉 VALIDATION SUCCESS: Strategy shows robust performance!")
                print("Ready for small-scale live trading implementation.")
            else:
                print("\n⚠️ VALIDATION WARNING: Strategy shows signs of overfitting.")
                print("Requires further optimization before live trading.")
        else:
            print("\n❌ VALIDATION FAILED: Unable to complete walk-forward analysis.")
    else:
        print("\n❌ BASIC BACKTEST FAILED: Strategy not statistically significant.")
        print("Strategy requires fundamental improvements before live trading.")