"""
Validation Framework - Scientific Backtesting Validation

Provides rigorous validation methods to prevent overfitting:
- Walk-forward analysis
- Cross-validation for time series
- Out-of-sample testing
- Monte Carlo simulation
- Bootstrap resampling
- Multiple hypothesis correction
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Callable, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class ValidationPeriod:
    """Single validation period for walk-forward analysis."""
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    period_id: int
    
    @property
    def train_duration_days(self) -> int:
        """Training period duration in days."""
        return (self.train_end - self.train_start).days
    
    @property
    def test_duration_days(self) -> int:
        """Test period duration in days."""
        return (self.test_end - self.test_start).days

@dataclass
class ValidationResult:
    """Result from a single validation period."""
    period: ValidationPeriod
    train_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    parameter_set: Dict[str, Any]
    trades_count: int
    
    @property
    def performance_degradation(self) -> float:
        """Calculate performance degradation from train to test."""
        train_return = self.train_metrics.get('annualized_return', 0)
        test_return = self.test_metrics.get('annualized_return', 0)
        
        if train_return == 0:
            return 0.0
        return (train_return - test_return) / abs(train_return)

@dataclass
class WalkForwardResults:
    """Complete walk-forward analysis results."""
    validation_periods: List[ValidationResult]
    overall_metrics: Dict[str, float]
    stability_metrics: Dict[str, float]
    overfitting_score: float  # 0-1, higher indicates more overfitting
    
    @property
    def is_robust(self) -> bool:
        """Check if strategy shows robust performance."""
        return (self.overfitting_score < 0.3 and 
                self.stability_metrics.get('consistency_ratio', 0) > 0.6)

class TimeSeriesSplitter:
    """
    Time series aware data splitting for validation.
    
    Ensures no look-ahead bias and maintains temporal order.
    """
    
    def __init__(self, train_size_months: int = 12, test_size_months: int = 3,
                 step_size_months: int = 1):
        self.train_size_months = train_size_months
        self.test_size_months = test_size_months
        self.step_size_months = step_size_months
    
    def split(self, start_date: datetime, end_date: datetime) -> List[ValidationPeriod]:
        """
        Create validation periods for walk-forward analysis.
        
        Args:
            start_date: Start of available data
            end_date: End of available data
            
        Returns:
            List of ValidationPeriod objects
        """
        periods = []
        period_id = 0
        
        current_date = start_date
        
        while True:
            # Calculate train period
            train_start = current_date
            train_end = train_start + timedelta(days=self.train_size_months * 30)
            
            # Calculate test period
            test_start = train_end
            test_end = test_start + timedelta(days=self.test_size_months * 30)
            
            # Check if we have enough data
            if test_end > end_date:
                break
            
            periods.append(ValidationPeriod(
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                period_id=period_id
            ))
            
            # Move to next period
            current_date += timedelta(days=self.step_size_months * 30)
            period_id += 1
        
        logger.info(f"Created {len(periods)} validation periods")
        return periods

class ParameterOptimizer:
    """
    Parameter optimization with overfitting protection.
    
    Uses proper validation techniques to find robust parameters.
    """
    
    def __init__(self, max_iterations: int = 100):
        self.max_iterations = max_iterations
        self.optimization_history = []
    
    def optimize_parameters(self, parameter_grid: Dict[str, List[Any]],
                          objective_function: Callable,
                          validation_periods: List[ValidationPeriod]) -> Dict[str, Any]:
        """
        Optimize parameters using walk-forward validation.
        
        Args:
            parameter_grid: Dictionary of parameter names and possible values
            objective_function: Function to evaluate parameter sets
            validation_periods: Periods for validation
            
        Returns:
            Best parameter set based on out-of-sample performance
        """
        logger.info("Starting parameter optimization...")
        
        # Generate parameter combinations
        param_combinations = self._generate_parameter_combinations(parameter_grid)
        
        best_params = None
        best_score = float('-inf')
        results = []
        
        for i, params in enumerate(param_combinations[:self.max_iterations]):
            logger.info(f"Testing parameter set {i+1}/{min(len(param_combinations), self.max_iterations)}")
            
            # Evaluate on all validation periods
            period_scores = []
            for period in validation_periods:
                try:
                    score = objective_function(params, period)
                    period_scores.append(score)
                except Exception as e:
                    logger.warning(f"Parameter evaluation failed: {e}")
                    period_scores.append(float('-inf'))
            
            # Calculate robust score (median to reduce outlier impact)
            robust_score = np.median(period_scores) if period_scores else float('-inf')
            
            results.append({
                'params': params,
                'score': robust_score,
                'period_scores': period_scores,
                'stability': np.std(period_scores) if len(period_scores) > 1 else 0
            })
            
            if robust_score > best_score:
                best_score = robust_score
                best_params = params
        
        self.optimization_history = results
        logger.info(f"Optimization complete. Best score: {best_score:.4f}")
        
        return best_params or {}
    
    def _generate_parameter_combinations(self, parameter_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """Generate all combinations of parameters."""
        import itertools
        
        keys = list(parameter_grid.keys())
        values = list(parameter_grid.values())
        
        combinations = []
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations

class ValidationFramework:
    """
    Main validation framework for scientific backtesting.
    
    Provides comprehensive validation methods to ensure robust results.
    """
    
    def __init__(self):
        self.splitter = TimeSeriesSplitter()
        self.optimizer = ParameterOptimizer()
        
    def walk_forward_analysis(self, strategy_function: Callable,
                            data: pd.DataFrame,
                            parameter_grid: Optional[Dict[str, List[Any]]] = None,
                            train_size_months: int = 12,
                            test_size_months: int = 3) -> WalkForwardResults:
        """
        Perform comprehensive walk-forward analysis.
        
        Args:
            strategy_function: Function that implements the trading strategy
            data: Historical market data
            parameter_grid: Optional parameters to optimize
            train_size_months: Training period size
            test_size_months: Test period size
            
        Returns:
            WalkForwardResults with comprehensive analysis
        """
        logger.info("Starting walk-forward analysis...")
        
        # Create validation periods
        self.splitter.train_size_months = train_size_months
        self.splitter.test_size_months = test_size_months
        
        start_date = data.index[0]
        end_date = data.index[-1]
        periods = self.splitter.split(start_date, end_date)
        
        if len(periods) < 3:
            raise ValueError("Insufficient data for walk-forward analysis (need at least 3 periods)")
        
        validation_results = []
        
        for period in periods:
            logger.info(f"Processing period {period.period_id + 1}/{len(periods)}")
            
            # Split data
            train_data = data[(data.index >= period.train_start) & 
                            (data.index <= period.train_end)]
            test_data = data[(data.index >= period.test_start) & 
                           (data.index <= period.test_end)]
            
            if len(train_data) < 100 or len(test_data) < 30:
                logger.warning(f"Insufficient data in period {period.period_id}")
                continue
            
            # Optimize parameters on training data (if provided)
            if parameter_grid:
                best_params = self._optimize_for_period(
                    strategy_function, train_data, parameter_grid
                )
            else:
                best_params = {}
            
            # Evaluate on training data
            train_metrics = self._evaluate_strategy(
                strategy_function, train_data, best_params
            )
            
            # Evaluate on test data (out-of-sample)
            test_metrics = self._evaluate_strategy(
                strategy_function, test_data, best_params
            )
            
            validation_results.append(ValidationResult(
                period=period,
                train_metrics=train_metrics,
                test_metrics=test_metrics,
                parameter_set=best_params,
                trades_count=test_metrics.get('total_trades', 0)
            ))
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(validation_results)
        stability_metrics = self._calculate_stability_metrics(validation_results)
        overfitting_score = self._calculate_overfitting_score(validation_results)
        
        return WalkForwardResults(
            validation_periods=validation_results,
            overall_metrics=overall_metrics,
            stability_metrics=stability_metrics,
            overfitting_score=overfitting_score
        )
    
    def _optimize_for_period(self, strategy_function: Callable,
                           train_data: pd.DataFrame,
                           parameter_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Optimize parameters for a single training period."""
        def objective(params, period=None):
            metrics = self._evaluate_strategy(strategy_function, train_data, params)
            # Use Sharpe ratio as primary objective
            return metrics.get('sharpe_ratio', 0)
        
        # Create a single pseudo-period for optimization
        pseudo_period = ValidationPeriod(
            train_start=train_data.index[0],
            train_end=train_data.index[-1],
            test_start=train_data.index[-1],
            test_end=train_data.index[-1],
            period_id=0
        )
        
        return self.optimizer.optimize_parameters(
            parameter_grid, objective, [pseudo_period]
        )
    
    def _evaluate_strategy(self, strategy_function: Callable,
                         data: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate strategy performance on given data."""
        try:
            # Run strategy
            results = strategy_function(data, **params)
            
            # Extract metrics (assuming strategy returns performance metrics)
            if isinstance(results, dict):
                return results
            else:
                # If strategy returns trades or equity curve, calculate metrics
                from .performance_analyzer import create_performance_analyzer
                analyzer = create_performance_analyzer()
                
                # Placeholder - in real implementation, would extract trades/equity
                return {
                    'annualized_return': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0,
                    'total_trades': 0
                }
                
        except Exception as e:
            logger.error(f"Strategy evaluation failed: {e}")
            return {
                'annualized_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0
            }
    
    def _calculate_overall_metrics(self, results: List[ValidationResult]) -> Dict[str, float]:
        """Calculate overall performance metrics across all periods."""
        if not results:
            return {}
        
        # Aggregate test metrics (out-of-sample performance)
        test_returns = [r.test_metrics.get('annualized_return', 0) for r in results]
        test_sharpes = [r.test_metrics.get('sharpe_ratio', 0) for r in results]
        test_drawdowns = [r.test_metrics.get('max_drawdown', 0) for r in results]
        
        return {
            'avg_return': np.mean(test_returns),
            'median_return': np.median(test_returns),
            'std_return': np.std(test_returns),
            'avg_sharpe': np.mean(test_sharpes),
            'median_sharpe': np.median(test_sharpes),
            'avg_drawdown': np.mean(test_drawdowns),
            'worst_drawdown': min(test_drawdowns) if test_drawdowns else 0,
            'positive_periods': sum(1 for r in test_returns if r > 0) / len(test_returns)
        }
    
    def _calculate_stability_metrics(self, results: List[ValidationResult]) -> Dict[str, float]:
        """Calculate stability metrics to assess robustness."""
        if len(results) < 2:
            return {}
        
        test_returns = [r.test_metrics.get('annualized_return', 0) for r in results]
        test_sharpes = [r.test_metrics.get('sharpe_ratio', 0) for r in results]
        
        # Consistency ratio (percentage of periods with positive returns)
        consistency_ratio = sum(1 for r in test_returns if r > 0) / len(test_returns)
        
        # Return stability (inverse of coefficient of variation)
        return_stability = 1 / (np.std(test_returns) / abs(np.mean(test_returns))) if np.mean(test_returns) != 0 else 0
        
        # Sharpe stability
        sharpe_stability = 1 / (np.std(test_sharpes) / abs(np.mean(test_sharpes))) if np.mean(test_sharpes) != 0 else 0
        
        return {
            'consistency_ratio': consistency_ratio,
            'return_stability': min(return_stability, 10),  # Cap at 10
            'sharpe_stability': min(sharpe_stability, 10),   # Cap at 10
            'return_volatility': np.std(test_returns),
            'sharpe_volatility': np.std(test_sharpes)
        }
    
    def _calculate_overfitting_score(self, results: List[ValidationResult]) -> float:
        """
        Calculate overfitting score (0-1, higher = more overfitting).
        
        Based on performance degradation from train to test periods.
        """
        if not results:
            return 1.0
        
        degradations = []
        for result in results:
            train_return = result.train_metrics.get('annualized_return', 0)
            test_return = result.test_metrics.get('annualized_return', 0)
            
            if train_return > 0:
                degradation = max(0, (train_return - test_return) / train_return)
                degradations.append(degradation)
        
        if not degradations:
            return 1.0
        
        # Average degradation as overfitting score
        avg_degradation = np.mean(degradations)
        
        # Normalize to 0-1 scale (degradation > 50% = high overfitting)
        overfitting_score = min(1.0, avg_degradation / 0.5)
        
        return overfitting_score

class MonteCarloValidator:
    """
    Monte Carlo validation for strategy robustness testing.
    
    Tests strategy performance under various market scenarios.
    """
    
    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
    
    def bootstrap_validation(self, returns: pd.Series, 
                           block_size: int = 30) -> Dict[str, float]:
        """
        Bootstrap validation using block bootstrap for time series.
        
        Args:
            returns: Strategy returns time series
            block_size: Size of blocks for bootstrap (preserves autocorrelation)
            
        Returns:
            Bootstrap statistics and confidence intervals
        """
        if len(returns) < block_size * 2:
            return {}
        
        bootstrap_returns = []
        
        for _ in range(self.n_simulations):
            # Block bootstrap
            bootstrapped = self._block_bootstrap(returns, block_size)
            
            # Calculate metrics for bootstrapped series
            annual_return = (1 + bootstrapped.mean()) ** 365 - 1
            sharpe = bootstrapped.mean() / bootstrapped.std() * np.sqrt(365) if bootstrapped.std() > 0 else 0
            
            bootstrap_returns.append({
                'annual_return': annual_return,
                'sharpe_ratio': sharpe
            })
        
        # Calculate confidence intervals
        annual_returns = [r['annual_return'] for r in bootstrap_returns]
        sharpe_ratios = [r['sharpe_ratio'] for r in bootstrap_returns]
        
        return {
            'return_mean': np.mean(annual_returns),
            'return_std': np.std(annual_returns),
            'return_ci_lower': np.percentile(annual_returns, 2.5),
            'return_ci_upper': np.percentile(annual_returns, 97.5),
            'sharpe_mean': np.mean(sharpe_ratios),
            'sharpe_std': np.std(sharpe_ratios),
            'sharpe_ci_lower': np.percentile(sharpe_ratios, 2.5),
            'sharpe_ci_upper': np.percentile(sharpe_ratios, 97.5)
        }
    
    def _block_bootstrap(self, series: pd.Series, block_size: int) -> pd.Series:
        """Perform block bootstrap on time series."""
        n = len(series)
        n_blocks = n // block_size
        
        # Randomly select blocks
        selected_blocks = np.random.choice(n_blocks, size=n_blocks, replace=True)
        
        bootstrapped_data = []
        for block_idx in selected_blocks:
            start_idx = block_idx * block_size
            end_idx = min(start_idx + block_size, n)
            bootstrapped_data.extend(series.iloc[start_idx:end_idx].values)
        
        return pd.Series(bootstrapped_data[:n])

class MultipleHypothesisCorrection:
    """
    Multiple hypothesis testing correction for parameter optimization.
    
    Prevents false discoveries when testing many parameter combinations.
    """
    
    @staticmethod
    def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
        """
        Bonferroni correction for multiple comparisons.
        
        Args:
            p_values: List of p-values from hypothesis tests
            alpha: Significance level
            
        Returns:
            List of booleans indicating significance after correction
        """
        corrected_alpha = alpha / len(p_values)
        return [p <= corrected_alpha for p in p_values]
    
    @staticmethod
    def fdr_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
        """
        False Discovery Rate (Benjamini-Hochberg) correction.
        
        Less conservative than Bonferroni, controls expected proportion of false discoveries.
        """
        n = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p_values = np.array(p_values)[sorted_indices]
        
        # Find largest k such that P(k) <= (k/n) * alpha
        significant = np.zeros(n, dtype=bool)
        
        for i in range(n-1, -1, -1):
            if sorted_p_values[i] <= ((i + 1) / n) * alpha:
                significant[sorted_indices[:i+1]] = True
                break
        
        return significant.tolist()

def create_validation_framework() -> ValidationFramework:
    """Factory function to create a configured validation framework."""
    return ValidationFramework()

def create_monte_carlo_validator(n_simulations: int = 1000) -> MonteCarloValidator:
    """Factory function to create a Monte Carlo validator."""
    return MonteCarloValidator(n_simulations)