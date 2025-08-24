#!/usr/bin/env python3
"""
Parameter Optimization - Finding Optimal Strategy Parameters

Systematically tests different correlation and confidence thresholds to find
the optimal parameters for current market conditions.

This is the logical next step after comprehensive backtesting showed 0 trades.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json
import pandas as pd
from typing import Dict, List, Any, Tuple
import itertools

# Add module paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from backtesting.coherent_backtester import CoherentBacktester, BacktestConfig
from dynamic_market_discovery import DynamicMarketDiscovery

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise during optimization
logger = logging.getLogger(__name__)

class ParameterOptimizer:
    """Systematic parameter optimization for correlation breakdown strategy."""
    
    def __init__(self):
        self.backtester = CoherentBacktester(cache_dir="param_optimization_cache")
        self.market_discovery = DynamicMarketDiscovery()
        self.optimization_results = []
        
    def define_parameter_grid(self) -> Dict[str, List[float]]:
        """Define parameter ranges for systematic testing."""
        return {
            'correlation_threshold': [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50],
            'min_confidence': [0.50, 0.60, 0.70, 0.75, 0.80, 0.90],
            'max_position_size': [0.015, 0.020, 0.025]  # Keep position sizing consistent
        }
    
    def get_test_symbols(self, max_symbols: int = 8) -> List[str]:
        """Get symbols for optimization testing."""
        try:
            optimal_assets = self.market_discovery.discover_optimal_assets(max_assets=15)
            symbols = [asset.symbol for asset in optimal_assets[:max_symbols]]
            logger.info(f"Using {len(symbols)} symbols for optimization")
            return symbols
        except Exception as e:
            logger.warning(f"Using fallback symbols: {e}")
            return ["BTCUSDC", "ETHUSDC", "XRPUSDC", "BNBUSDC", "SOLUSDC", "ADAUSDC"]
    
    def test_parameter_combination(self, params: Dict[str, float], 
                                 test_period_days: int = 90) -> Dict[str, Any]:
        """Test a specific parameter combination."""
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=test_period_days)
        
        symbols = self.get_test_symbols()
        
        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=10000.0,
            symbols=symbols,
            timeframe="1h",
            correlation_threshold=params['correlation_threshold'],
            min_confidence=params['min_confidence'],
            max_position_size=params['max_position_size'],
            use_realistic_execution=True,
            include_fees=True
        )
        
        try:
            result = self.backtester.run_backtest(config)
            metrics = result.performance_metrics
            
            # Calculate optimization score
            # Prioritize: trades > 0, positive return, good Sharpe, low drawdown
            score = 0.0
            if metrics.total_trades > 0:
                score += 10.0  # Base score for generating trades
                score += min(metrics.annualized_return * 10, 5.0)  # Return component
                score += min(metrics.sharpe_ratio * 2, 3.0)  # Sharpe component
                score -= abs(metrics.max_drawdown) * 5  # Drawdown penalty
                score += min(metrics.total_trades / 10, 2.0)  # Trade frequency bonus
            
            return {
                'params': params,
                'total_trades': metrics.total_trades,
                'annualized_return': metrics.annualized_return,
                'sharpe_ratio': metrics.sharpe_ratio,
                'max_drawdown': metrics.max_drawdown,
                'win_rate': metrics.win_rate,
                'profit_factor': metrics.profit_factor,
                'is_statistically_significant': metrics.is_statistically_significant(),
                'optimization_score': score,
                'test_period_days': test_period_days,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Parameter test failed {params}: {e}")
            return {
                'params': params,
                'error': str(e),
                'optimization_score': -999.0,
                'success': False
            }
    
    def run_systematic_optimization(self, max_combinations: int = 50) -> List[Dict[str, Any]]:
        """Run systematic parameter optimization."""
        print("\\n🔧 SYSTEMATIC PARAMETER OPTIMIZATION")
        print("="*60)
        print("Testing correlation breakdown strategy parameters...")
        print("Goal: Find parameters that generate trades in current market")
        
        param_grid = self.define_parameter_grid()
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        all_combinations = list(itertools.product(*param_values))
        
        print(f"\\n📊 Testing {min(len(all_combinations), max_combinations)} parameter combinations")
        print(f"Parameter ranges:")
        for param, values in param_grid.items():
            print(f"  • {param}: {min(values):.3f} - {max(values):.3f}")
        
        results = []
        
        # Test each combination (limit to max_combinations for speed)
        for i, combination in enumerate(all_combinations[:max_combinations]):
            params = dict(zip(param_names, combination))
            
            print(f"\\rTesting {i+1}/{min(len(all_combinations), max_combinations)}: "
                  f"corr={params['correlation_threshold']:.2f}, "
                  f"conf={params['min_confidence']:.2f}", end="", flush=True)
            
            result = self.test_parameter_combination(params)
            results.append(result)
            
            # Early feedback for promising results
            if result.get('total_trades', 0) > 0:
                print(f"\\n  ✅ Found {result['total_trades']} trades! "
                      f"Return: {result['annualized_return']:.1%}, "
                      f"Score: {result['optimization_score']:.1f}")
        
        print("\\n\\n🔍 OPTIMIZATION COMPLETE")
        return results
    
    def run_timeframe_analysis(self) -> Dict[str, Any]:
        """Test different timeframes to see if longer periods show more opportunities."""
        print("\\n📈 TIMEFRAME ANALYSIS")
        print("="*40)
        
        timeframes = ["1h", "4h", "12h", "1d"]
        symbols = self.get_test_symbols(6)  # Smaller set for speed
        
        # Use best parameters from quick test
        base_params = {
            'correlation_threshold': 0.25,  # Lower threshold
            'min_confidence': 0.60,         # Lower confidence
            'max_position_size': 0.020
        }
        
        timeframe_results = {}
        
        for timeframe in timeframes:
            print(f"\\nTesting {timeframe} timeframe...")
            
            config = BacktestConfig(
                start_date=datetime.now() - timedelta(days=180),  # 6 months
                end_date=datetime.now() - timedelta(days=1),
                initial_capital=10000.0,
                symbols=symbols,
                timeframe=timeframe,
                **base_params,
                use_realistic_execution=True,
                include_fees=True
            )
            
            try:
                result = self.backtester.run_backtest(config)
                metrics = result.performance_metrics
                
                timeframe_results[timeframe] = {
                    'total_trades': metrics.total_trades,
                    'annualized_return': metrics.annualized_return,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'max_drawdown': metrics.max_drawdown,
                    'success': True
                }
                
                print(f"  {timeframe}: {metrics.total_trades} trades, "
                      f"{metrics.annualized_return:.1%} return")
                
            except Exception as e:
                print(f"  {timeframe}: Failed - {e}")
                timeframe_results[timeframe] = {'success': False, 'error': str(e)}
        
        return timeframe_results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze optimization results and provide recommendations."""
        successful_results = [r for r in results if r.get('success', False)]
        
        if not successful_results:
            return {
                'status': 'FAILED',
                'message': 'No successful parameter combinations',
                'recommendation': 'Strategy may not be viable for current market conditions'
            }
        
        # Find results with trades
        results_with_trades = [r for r in successful_results if r.get('total_trades', 0) > 0]
        
        if not results_with_trades:
            # Even with parameter optimization, no trades found
            best_score = max(successful_results, key=lambda x: x.get('optimization_score', -999))
            return {
                'status': 'NO_TRADES',
                'message': 'No parameter combination generated trades',
                'best_params_tested': best_score.get('params'),
                'total_combinations_tested': len(successful_results),
                'recommendation': 'Consider: (1) Different timeframes, (2) Alternative strategies, (3) Market regime analysis'
            }
        
        # Analyze successful results
        best_result = max(results_with_trades, key=lambda x: x.get('optimization_score', 0))
        most_trades = max(results_with_trades, key=lambda x: x.get('total_trades', 0))
        best_return = max(results_with_trades, key=lambda x: x.get('annualized_return', -999))
        
        # Parameter sensitivity analysis
        correlation_values = [r['params']['correlation_threshold'] for r in results_with_trades]
        confidence_values = [r['params']['min_confidence'] for r in results_with_trades]
        
        analysis = {
            'status': 'SUCCESS',
            'total_combinations_tested': len(successful_results),
            'combinations_with_trades': len(results_with_trades),
            'best_overall': best_result,
            'most_trades': most_trades,
            'best_return': best_return,
            'parameter_insights': {
                'optimal_correlation_range': f"{min(correlation_values):.2f} - {max(correlation_values):.2f}",
                'optimal_confidence_range': f"{min(confidence_values):.2f} - {max(confidence_values):.2f}",
                'avg_correlation_threshold': sum(correlation_values) / len(correlation_values),
                'avg_confidence_level': sum(confidence_values) / len(confidence_values)
            },
            'recommendation': self._generate_optimization_recommendation(results_with_trades)
        }
        
        return analysis
    
    def _generate_optimization_recommendation(self, results_with_trades: List[Dict]) -> str:
        """Generate recommendation based on optimization results."""
        if not results_with_trades:
            return "Strategy not viable for current market conditions"
        
        avg_return = sum(r.get('annualized_return', 0) for r in results_with_trades) / len(results_with_trades)
        avg_trades = sum(r.get('total_trades', 0) for r in results_with_trades) / len(results_with_trades)
        
        if avg_return > 0.10 and avg_trades > 5:
            return "PROMISING - Strategy shows potential with optimized parameters"
        elif avg_return > 0.05:
            return "MARGINAL - Strategy generates trades but returns are modest"
        else:
            return "LIMITED - Strategy generates activity but profitability questionable"
    
    def print_optimization_summary(self, results: List[Dict], analysis: Dict, timeframe_results: Dict = None):
        """Print comprehensive optimization summary."""
        print("\\n" + "="*80)
        print("🔧 PARAMETER OPTIMIZATION SUMMARY")
        print("="*80)
        
        print(f"\\n📊 OPTIMIZATION STATUS: {analysis['status']}")
        
        if analysis['status'] == 'SUCCESS':
            print(f"\\n🎯 BEST PARAMETERS FOUND:")
            best = analysis['best_overall']
            params = best['params']
            print(f"   • Correlation Threshold: {params['correlation_threshold']:.3f}")
            print(f"   • Confidence Level: {params['min_confidence']:.3f}")
            print(f"   • Position Size: {params['max_position_size']:.3f}")
            print(f"   • Generated {best['total_trades']} trades")
            print(f"   • Annualized Return: {best['annualized_return']:.2%}")
            print(f"   • Sharpe Ratio: {best['sharpe_ratio']:.2f}")
            print(f"   • Max Drawdown: {best['max_drawdown']:.2%}")
            
            print(f"\\n📈 PARAMETER INSIGHTS:")
            insights = analysis['parameter_insights']
            print(f"   • Optimal Correlation Range: {insights['optimal_correlation_range']}")
            print(f"   • Optimal Confidence Range: {insights['optimal_confidence_range']}")
            print(f"   • Tested {analysis['total_combinations_tested']} combinations")
            print(f"   • {analysis['combinations_with_trades']} generated trades")
            
        elif analysis['status'] == 'NO_TRADES':
            print(f"\\n⚠️ NO TRADES GENERATED:")
            print(f"   • Tested {analysis['total_combinations_tested']} parameter combinations")
            print(f"   • Best parameters tested: {analysis.get('best_params_tested')}")
            
        if timeframe_results:
            print(f"\\n📅 TIMEFRAME ANALYSIS:")
            for tf, result in timeframe_results.items():
                if result.get('success'):
                    print(f"   • {tf}: {result['total_trades']} trades, {result['annualized_return']:.1%} return")
                else:
                    print(f"   • {tf}: Failed")
        
        print(f"\\n🎯 RECOMMENDATION:")
        print(f"   {analysis.get('recommendation', 'Further analysis needed')}")
        
        print(f"\\n💡 NEXT STEPS:")
        if analysis['status'] == 'SUCCESS':
            print("   ✅ Deploy optimized parameters for live testing")
            print("   📊 Monitor performance and fine-tune")
            print("   🔄 Re-optimize periodically as market conditions change")
        else:
            print("   🔄 Consider alternative strategies")
            print("   📈 Test different timeframes or assets")
            print("   🧪 Analyze market microstructure changes")

def save_optimization_results(results: List[Dict], analysis: Dict, timeframe_results: Dict = None):
    """Save optimization results to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"parameter_optimization_{timestamp}.json"
    filepath = Path(__file__).parent / filename
    
    full_results = {
        'timestamp': datetime.now().isoformat(),
        'parameter_tests': results,
        'analysis': analysis,
        'timeframe_analysis': timeframe_results,
        'summary': {
            'total_tests': len(results),
            'successful_tests': len([r for r in results if r.get('success')]),
            'tests_with_trades': len([r for r in results if r.get('total_trades', 0) > 0])
        }
    }
    
    with open(filepath, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    
    print(f"\\n📄 Optimization results saved to: {filepath}")
    return filepath

def main():
    """Main optimization execution."""
    print("🔧 MomoAI Funding System - Parameter Optimization")
    print("Finding optimal parameters for correlation breakdown strategy")
    print("="*70)
    
    try:
        optimizer = ParameterOptimizer()
        
        # Run systematic parameter optimization
        results = optimizer.run_systematic_optimization(max_combinations=40)
        
        # Analyze results
        analysis = optimizer.analyze_results(results)
        
        # Test different timeframes if no trades found
        timeframe_results = None
        if analysis['status'] != 'SUCCESS':
            timeframe_results = optimizer.run_timeframe_analysis()
        
        # Print summary
        optimizer.print_optimization_summary(results, analysis, timeframe_results)
        
        # Save results
        save_optimization_results(results, analysis, timeframe_results)
        
        print("\\n🎉 Parameter optimization completed!")
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()