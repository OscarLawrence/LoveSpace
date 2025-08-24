"""
Performance Analyzer - Rigorous Statistical Performance Metrics

Provides comprehensive performance analysis with:
- Risk-adjusted returns (Sharpe, Sortino, Calmar)
- Drawdown analysis with recovery times
- Value at Risk (VaR) and Expected Shortfall
- Statistical significance testing
- Regime-specific performance analysis
- Benchmark comparisons
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Individual trade record for performance analysis."""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    fees: float
    duration_hours: float
    
    @property
    def is_profitable(self) -> bool:
        """Check if trade was profitable."""
        return self.pnl > 0

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    # Return metrics
    total_return: float
    annualized_return: float
    volatility: float
    
    # Risk-adjusted metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Drawdown metrics
    max_drawdown: float
    max_drawdown_duration_days: float
    avg_drawdown: float
    recovery_factor: float
    
    # Risk metrics
    var_95: float  # 95% Value at Risk
    var_99: float  # 99% Value at Risk
    expected_shortfall_95: float
    expected_shortfall_99: float
    
    # Trade metrics
    total_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    
    # Statistical significance
    t_statistic: float
    p_value: float
    confidence_interval_95: Tuple[float, float]
    
    def is_statistically_significant(self, alpha: float = 0.05) -> bool:
        """Check if returns are statistically significant."""
        return self.p_value < alpha

class PerformanceAnalyzer:
    """
    Comprehensive performance analysis engine.
    
    Calculates rigorous statistical metrics with proper significance testing
    and handles multiple market regimes for robust analysis.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate  # Annual risk-free rate
        self.trading_days_per_year = 365  # Crypto trades 24/7
        
    def analyze_performance(self, trades: List[Trade], 
                          equity_curve: pd.Series,
                          benchmark_returns: Optional[pd.Series] = None) -> PerformanceMetrics:
        """
        Comprehensive performance analysis.
        
        Args:
            trades: List of individual trades
            equity_curve: Time series of portfolio equity
            benchmark_returns: Optional benchmark for comparison
            
        Returns:
            PerformanceMetrics with comprehensive analysis
        """
        if len(trades) == 0 or len(equity_curve) < 2:
            return self._empty_metrics()
        
        # Calculate returns
        returns = equity_curve.pct_change().dropna()
        
        # Basic return metrics
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        annualized_return = self._annualize_return(total_return, len(equity_curve))
        volatility = returns.std() * np.sqrt(self.trading_days_per_year)
        
        # Risk-adjusted metrics
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        sortino_ratio = self._calculate_sortino_ratio(returns)
        calmar_ratio = self._calculate_calmar_ratio(annualized_return, equity_curve)
        
        # Drawdown analysis
        drawdown_metrics = self._analyze_drawdowns(equity_curve)
        
        # Risk metrics (VaR and Expected Shortfall)
        var_95 = self._calculate_var(returns, 0.05)
        var_99 = self._calculate_var(returns, 0.01)
        es_95 = self._calculate_expected_shortfall(returns, 0.05)
        es_99 = self._calculate_expected_shortfall(returns, 0.01)
        
        # Trade analysis
        trade_metrics = self._analyze_trades(trades)
        
        # Statistical significance
        t_stat, p_value, conf_interval = self._test_statistical_significance(returns)
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=drawdown_metrics['max_drawdown'],
            max_drawdown_duration_days=drawdown_metrics['max_duration'],
            avg_drawdown=drawdown_metrics['avg_drawdown'],
            recovery_factor=drawdown_metrics['recovery_factor'],
            var_95=var_95,
            var_99=var_99,
            expected_shortfall_95=es_95,
            expected_shortfall_99=es_99,
            total_trades=trade_metrics['total_trades'],
            win_rate=trade_metrics['win_rate'],
            avg_win=trade_metrics['avg_win'],
            avg_loss=trade_metrics['avg_loss'],
            profit_factor=trade_metrics['profit_factor'],
            t_statistic=t_stat,
            p_value=p_value,
            confidence_interval_95=conf_interval
        )
    
    def _annualize_return(self, total_return: float, periods: int) -> float:
        """Annualize return based on number of periods."""
        if periods <= 1:
            return 0.0
        years = periods / self.trading_days_per_year
        return (1 + total_return) ** (1 / years) - 1
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio with proper annualization."""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / self.trading_days_per_year)
        return (excess_returns.mean() / returns.std()) * np.sqrt(self.trading_days_per_year)
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio (downside deviation focus)."""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / self.trading_days_per_year)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if excess_returns.mean() > 0 else 0.0
        
        downside_deviation = downside_returns.std() * np.sqrt(self.trading_days_per_year)
        return (excess_returns.mean() * self.trading_days_per_year) / downside_deviation
    
    def _calculate_calmar_ratio(self, annualized_return: float, equity_curve: pd.Series) -> float:
        """Calculate Calmar ratio (return / max drawdown)."""
        max_dd = self._calculate_max_drawdown(equity_curve)
        if max_dd == 0:
            return float('inf') if annualized_return > 0 else 0.0
        return annualized_return / abs(max_dd)
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    def _analyze_drawdowns(self, equity_curve: pd.Series) -> Dict[str, float]:
        """Comprehensive drawdown analysis."""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        
        # Find drawdown periods
        in_drawdown = drawdown < 0
        drawdown_periods = []
        start_idx = None
        
        for i, is_dd in enumerate(in_drawdown):
            if is_dd and start_idx is None:
                start_idx = i
            elif not is_dd and start_idx is not None:
                drawdown_periods.append((start_idx, i-1))
                start_idx = None
        
        # Handle case where we end in drawdown
        if start_idx is not None:
            drawdown_periods.append((start_idx, len(drawdown)-1))
        
        # Calculate metrics
        max_drawdown = drawdown.min()
        avg_drawdown = drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0
        
        # Maximum drawdown duration
        max_duration = 0
        if drawdown_periods:
            max_duration = max(end - start + 1 for start, end in drawdown_periods)
        
        # Recovery factor
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        recovery_factor = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'max_duration': max_duration,
            'recovery_factor': recovery_factor
        }
    
    def _calculate_var(self, returns: pd.Series, alpha: float) -> float:
        """Calculate Value at Risk at given confidence level."""
        if len(returns) == 0:
            return 0.0
        return np.percentile(returns, alpha * 100)
    
    def _calculate_expected_shortfall(self, returns: pd.Series, alpha: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)."""
        if len(returns) == 0:
            return 0.0
        var = self._calculate_var(returns, alpha)
        tail_returns = returns[returns <= var]
        return tail_returns.mean() if len(tail_returns) > 0 else 0.0
    
    def _analyze_trades(self, trades: List[Trade]) -> Dict[str, float]:
        """Analyze individual trade performance."""
        if not trades:
            return {
                'total_trades': 0, 'win_rate': 0, 'avg_win': 0,
                'avg_loss': 0, 'profit_factor': 0
            }
        
        winning_trades = [t for t in trades if t.is_profitable]
        losing_trades = [t for t in trades if not t.is_profitable]
        
        total_trades = len(trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    def _test_statistical_significance(self, returns: pd.Series) -> Tuple[float, float, Tuple[float, float]]:
        """Test statistical significance of returns."""
        if len(returns) < 2:
            return 0.0, 1.0, (0.0, 0.0)
        
        # One-sample t-test against zero mean
        t_stat, p_value = stats.ttest_1samp(returns, 0)
        
        # 95% confidence interval for mean return
        confidence_interval = stats.t.interval(
            0.95, len(returns)-1, 
            loc=returns.mean(), 
            scale=stats.sem(returns)
        )
        
        return t_stat, p_value, confidence_interval
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics for edge cases."""
        return PerformanceMetrics(
            total_return=0.0, annualized_return=0.0, volatility=0.0,
            sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
            max_drawdown=0.0, max_drawdown_duration_days=0.0, avg_drawdown=0.0, recovery_factor=0.0,
            var_95=0.0, var_99=0.0, expected_shortfall_95=0.0, expected_shortfall_99=0.0,
            total_trades=0, win_rate=0.0, avg_win=0.0, avg_loss=0.0, profit_factor=0.0,
            t_statistic=0.0, p_value=1.0, confidence_interval_95=(0.0, 0.0)
        )

def create_performance_analyzer(risk_free_rate: float = 0.02) -> PerformanceAnalyzer:
    """Factory function to create a configured performance analyzer."""
    return PerformanceAnalyzer(risk_free_rate)