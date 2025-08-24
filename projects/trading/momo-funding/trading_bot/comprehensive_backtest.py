#!/usr/bin/env python3
"""
Comprehensive Backtesting - Multi-Market Condition Analysis

Tests the correlation breakdown strategy across different market regimes:
- Bull markets (2020-2021)
- Bear markets (2022)
- Sideways markets (2023-2024)
- High volatility periods
- Low volatility periods

Provides statistical significance testing and regime-specific performance analysis.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Any

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

class ComprehensiveBacktester:
    """Comprehensive backtesting across multiple market conditions."""
    
    def __init__(self):
        self.backtester = CoherentBacktester(cache_dir="comprehensive_backtest_cache")
        self.market_discovery = DynamicMarketDiscovery()
        self.results = {}
        
    def define_market_regimes(self) -> Dict[str, Dict]:
        """
        Define different market regimes for testing.
        
        Each regime tests different market conditions to ensure strategy robustness.
        """
        return {
            "crypto_winter_2022": {
                "name": "Crypto Winter 2022",
                "start_date": datetime(2022, 1, 1),
                "end_date": datetime(2022, 12, 31),
                "description": "Bear market, high correlation, limited opportunities",
                "expected_trades": "Low",
                "market_condition": "Bear"
            },
            "recovery_2023": {
                "name": "Recovery 2023", 
                "start_date": datetime(2023, 1, 1),
                "end_date": datetime(2023, 12, 31),
                "description": "Recovery phase, changing correlations, moderate opportunities",
                "expected_trades": "Medium",
                "market_condition": "Sideways"
            },
            "recent_period": {
                "name": "Recent Period 2024",
                "start_date": datetime(2024, 1, 1), 
                "end_date": datetime(2024, 12, 31),
                "description": "Current market, mixed conditions",
                "expected_trades": "Variable",
                "market_condition": "Mixed"
            },
            "full_cycle": {
                "name": "Full Cycle 2022-2024",
                "start_date": datetime(2022, 1, 1),
                "end_date": datetime(2024, 12, 31),
                "description": "Complete market cycle, all conditions",
                "expected_trades": "High", 
                "market_condition": "Full Cycle"
            },
            "high_volatility": {
                "name": "High Volatility Q1 2022",
                "start_date": datetime(2022, 1, 1),
                "end_date": datetime(2022, 3, 31),
                "description": "High volatility period, many breakdown opportunities",
                "expected_trades": "High",
                "market_condition": "High Vol"
            },
            "recent_3months": {
                "name": "Recent 3 Months",
                "start_date": datetime.now() - timedelta(days=90),
                "end_date": datetime.now() - timedelta(days=1),
                "description": "Most recent data, current market conditions",
                "expected_trades": "Low-Medium",
                "market_condition": "Current"
            }
        }
    
    def get_optimal_symbols(self, max_symbols: int = 12) -> List[str]:
        """Get optimal symbols for backtesting."""
        try:
            optimal_assets = self.market_discovery.discover_optimal_assets(max_assets=20)
            symbols = [asset.symbol for asset in optimal_assets[:max_symbols]]
            logger.info(f"Selected {len(symbols)} symbols for backtesting: {symbols}")
            return symbols
        except Exception as e:
            logger.warning(f"Dynamic discovery failed: {e}, using fallback symbols")
            # Fallback to known liquid pairs
            return [
                "BTCUSDC", "ETHUSDC", "XRPUSDC", "BNBUSDC", "SOLUSDC", "ADAUSDC",
                "LINKUSDC", "SUIUSDC", "TRXUSDC", "XLMUSDC", "BCHUSDC", "LTCUSDC"
            ]
    
    def run_regime_backtest(self, regime_name: str, regime_config: Dict) -> Dict[str, Any]:
        """Run backtest for a specific market regime."""
        logger.info(f"\\n{'='*60}")
        logger.info(f"TESTING REGIME: {regime_config['name']}")
        logger.info(f"Period: {regime_config['start_date'].strftime('%Y-%m-%d')} to {regime_config['end_date'].strftime('%Y-%m-%d')}")
        logger.info(f"Condition: {regime_config['market_condition']}")
        logger.info(f"{'='*60}")
        
        symbols = self.get_optimal_symbols(10)  # 10 symbols for faster testing
        
        # Configure backtest for this regime
        config = BacktestConfig(
            start_date=regime_config['start_date'],
            end_date=regime_config['end_date'],
            initial_capital=10000.0,
            symbols=symbols,
            timeframe="1h",
            correlation_threshold=0.35,  # Standard threshold
            min_confidence=0.75,
            max_position_size=0.02,
            use_realistic_execution=True,
            include_fees=True
        )
        
        try:
            result = self.backtester.run_backtest(config)
            
            # Calculate regime-specific metrics
            metrics = result.performance_metrics
            execution_stats = result.execution_stats
            
            regime_results = {
                "regime_name": regime_name,
                "period": f"{regime_config['start_date'].strftime('%Y-%m-%d')} to {regime_config['end_date'].strftime('%Y-%m-%d')}",
                "market_condition": regime_config['market_condition'],
                "description": regime_config['description'],
                "symbols_tested": len(symbols),
                "total_trades": metrics.total_trades,
                "total_return": metrics.total_return,
                "annualized_return": metrics.annualized_return,
                "volatility": metrics.volatility,
                "sharpe_ratio": metrics.sharpe_ratio,
                "sortino_ratio": metrics.sortino_ratio,
                "max_drawdown": metrics.max_drawdown,
                "calmar_ratio": metrics.calmar_ratio,
                "win_rate": metrics.win_rate,
                "profit_factor": metrics.profit_factor,
                "recovery_factor": metrics.recovery_factor,
                "var_95": metrics.var_95,
                "expected_shortfall_95": metrics.expected_shortfall_95,
                "is_statistically_significant": metrics.is_statistically_significant(),
                "t_statistic": metrics.t_statistic,
                "p_value": metrics.p_value,
                "confidence_interval_95": metrics.confidence_interval_95,
                "execution_stats": execution_stats,
                "success": True
            }
            
            # Log results
            logger.info(f"RESULTS - {regime_config['name']}:")
            logger.info(f"  Trades: {metrics.total_trades}")
            logger.info(f"  Return: {metrics.annualized_return:.2%}")
            logger.info(f"  Sharpe: {metrics.sharpe_ratio:.2f}")
            logger.info(f"  Max DD: {metrics.max_drawdown:.2%}")
            logger.info(f"  Significant: {metrics.is_statistically_significant()}")
            
            return regime_results
            
        except Exception as e:
            logger.error(f"Backtest failed for {regime_name}: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "regime_name": regime_name,
                "period": f"{regime_config['start_date'].strftime('%Y-%m-%d')} to {regime_config['end_date'].strftime('%Y-%m-%d')}",
                "market_condition": regime_config['market_condition'],
                "error": str(e),
                "success": False
            }
    
    def run_walk_forward_validation(self) -> Dict[str, Any]:
        """Run walk-forward validation across multiple market conditions."""
        logger.info("\\n" + "="*60)
        logger.info("WALK-FORWARD VALIDATION")
        logger.info("="*60)
        
        symbols = self.get_optimal_symbols(8)  # Smaller set for validation
        
        # Use 2-year period for validation
        base_config = BacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 12, 31),
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
            result = self.backtester.run_walk_forward_validation(
                base_config=base_config,
                parameter_grid=parameter_grid,
                train_months=6,  # 6 month training
                test_months=2   # 2 month testing
            )
            
            if result.validation_results:
                val_results = result.validation_results
                return {
                    "validation_periods": len(val_results.validation_periods),
                    "overfitting_score": val_results.overfitting_score,
                    "is_robust": val_results.is_robust,
                    "overall_metrics": val_results.overall_metrics,
                    "stability_metrics": val_results.stability_metrics,
                    "final_performance": {
                        "return": result.performance_metrics.annualized_return,
                        "sharpe": result.performance_metrics.sharpe_ratio,
                        "drawdown": result.performance_metrics.max_drawdown
                    },
                    "success": True
                }
            else:
                return {"success": False, "error": "No validation results"}
                
        except Exception as e:
            logger.error(f"Walk-forward validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete comprehensive backtesting analysis."""
        logger.info("\\n🔬 COMPREHENSIVE BACKTESTING ANALYSIS")
        logger.info("Testing correlation breakdown strategy across multiple market regimes")
        logger.info("="*80)
        
        regimes = self.define_market_regimes()
        regime_results = {}
        
        # Test each market regime
        for regime_name, regime_config in regimes.items():
            try:
                result = self.run_regime_backtest(regime_name, regime_config)
                regime_results[regime_name] = result
            except Exception as e:
                logger.error(f"Failed to test regime {regime_name}: {e}")
                regime_results[regime_name] = {
                    "success": False,
                    "error": str(e),
                    "regime_name": regime_name
                }
        
        # Run walk-forward validation
        logger.info("\\nRunning walk-forward validation...")
        validation_results = self.run_walk_forward_validation()
        
        # Compile comprehensive results
        comprehensive_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "regime_results": regime_results,
            "walk_forward_validation": validation_results,
            "summary": self._generate_summary(regime_results, validation_results)
        }
        
        return comprehensive_results
    
    def _generate_summary(self, regime_results: Dict, validation_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive summary of all results."""
        successful_regimes = [r for r in regime_results.values() if r.get("success", False)]
        
        if not successful_regimes:
            return {"status": "FAILED", "reason": "No successful regime tests"}
        
        # Calculate aggregate statistics
        total_trades = sum(r.get("total_trades", 0) for r in successful_regimes)
        avg_return = sum(r.get("annualized_return", 0) for r in successful_regimes) / len(successful_regimes)
        avg_sharpe = sum(r.get("sharpe_ratio", 0) for r in successful_regimes) / len(successful_regimes)
        worst_drawdown = min(r.get("max_drawdown", 0) for r in successful_regimes)
        significant_results = sum(1 for r in successful_regimes if r.get("is_statistically_significant", False))
        
        # Determine overall strategy viability
        if significant_results >= len(successful_regimes) * 0.5 and avg_sharpe > 0.5:
            status = "VIABLE"
        elif total_trades > 10 and avg_return > 0:
            status = "PROMISING"
        else:
            status = "NEEDS_IMPROVEMENT"
        
        return {
            "status": status,
            "regimes_tested": len(regime_results),
            "successful_regimes": len(successful_regimes),
            "total_trades_all_regimes": total_trades,
            "average_annual_return": avg_return,
            "average_sharpe_ratio": avg_sharpe,
            "worst_max_drawdown": worst_drawdown,
            "statistically_significant_regimes": significant_results,
            "validation_robust": validation_results.get("is_robust", False) if validation_results.get("success") else False,
            "recommendation": self._generate_recommendation(status, avg_return, avg_sharpe, worst_drawdown, validation_results)
        }
    
    def _generate_recommendation(self, status: str, avg_return: float, avg_sharpe: float, 
                               worst_drawdown: float, validation_results: Dict) -> str:
        """Generate trading recommendation based on results."""
        if status == "VIABLE" and validation_results.get("is_robust", False):
            return "APPROVED for live trading with current parameters"
        elif status == "PROMISING":
            return "CONDITIONAL approval - requires parameter optimization"
        elif avg_return > 0.05:
            return "POTENTIAL - needs longer testing period and parameter tuning"
        else:
            return "NOT RECOMMENDED - strategy shows insufficient edge"

def save_results_to_file(results: Dict[str, Any], filename: str = None):
    """Save comprehensive results to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_backtest_{timestamp}.json"
    
    filepath = Path(__file__).parent / filename
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to: {filepath}")
    return filepath

def print_executive_summary(results: Dict[str, Any]):
    """Print executive summary of comprehensive backtesting."""
    print("\\n" + "="*80)
    print("🔬 COMPREHENSIVE BACKTESTING - EXECUTIVE SUMMARY")
    print("="*80)
    
    summary = results.get("summary", {})
    regime_results = results.get("regime_results", {})
    validation = results.get("walk_forward_validation", {})
    
    print(f"\\n📊 OVERALL STATUS: {summary.get('status', 'UNKNOWN')}")
    print(f"🎯 RECOMMENDATION: {summary.get('recommendation', 'N/A')}")
    
    print(f"\\n📈 PERFORMANCE SUMMARY:")
    print(f"   • Regimes Tested: {summary.get('regimes_tested', 0)}")
    print(f"   • Successful Tests: {summary.get('successful_regimes', 0)}")
    print(f"   • Total Trades: {summary.get('total_trades_all_regimes', 0)}")
    print(f"   • Avg Annual Return: {summary.get('average_annual_return', 0):.2%}")
    print(f"   • Avg Sharpe Ratio: {summary.get('average_sharpe_ratio', 0):.2f}")
    print(f"   • Worst Drawdown: {summary.get('worst_max_drawdown', 0):.2%}")
    print(f"   • Statistically Significant: {summary.get('statistically_significant_regimes', 0)}/{summary.get('successful_regimes', 0)}")
    
    if validation.get("success"):
        print(f"\\n🔬 VALIDATION RESULTS:")
        print(f"   • Strategy Robust: {validation.get('is_robust', False)}")
        print(f"   • Overfitting Score: {validation.get('overfitting_score', 0):.3f}")
        print(f"   • Validation Periods: {validation.get('validation_periods', 0)}")
    
    print(f"\\n📋 REGIME BREAKDOWN:")
    for regime_name, result in regime_results.items():
        if result.get("success"):
            status_icon = "✅" if result.get("is_statistically_significant") else "⚠️"
            print(f"   {status_icon} {result.get('market_condition', 'Unknown')}: "
                  f"{result.get('total_trades', 0)} trades, "
                  f"{result.get('annualized_return', 0):.1%} return, "
                  f"{result.get('sharpe_ratio', 0):.1f} Sharpe")
        else:
            print(f"   ❌ {regime_name}: {result.get('error', 'Failed')}")
    
    print(f"\\n🎯 NEXT STEPS:")
    if summary.get('status') == 'VIABLE':
        print("   ✅ Strategy ready for live deployment")
        print("   💰 Recommended position size: 2% max per trade")
        print("   🔄 Monitor performance and adjust if needed")
    elif summary.get('status') == 'PROMISING':
        print("   🔧 Optimize parameters using validation results")
        print("   📊 Run additional testing on recent data")
        print("   ⚠️ Start with smaller position sizes")
    else:
        print("   🔄 Strategy needs fundamental improvements")
        print("   📈 Consider different timeframes or thresholds")
        print("   🛑 Not recommended for live trading yet")

def main():
    """Main execution function."""
    print("🔬 MomoAI Funding System - Comprehensive Backtesting")
    print("Testing correlation breakdown strategy across multiple market conditions")
    print("="*80)
    
    try:
        # Initialize comprehensive backtester
        comp_backtester = ComprehensiveBacktester()
        
        # Run comprehensive analysis
        results = comp_backtester.run_comprehensive_analysis()
        
        # Save results
        results_file = save_results_to_file(results)
        
        # Print executive summary
        print_executive_summary(results)
        
        print(f"\\n📄 Detailed results saved to: {results_file}")
        print("\\n🎉 Comprehensive backtesting completed!")
        
    except Exception as e:
        logger.error(f"Comprehensive backtesting failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()