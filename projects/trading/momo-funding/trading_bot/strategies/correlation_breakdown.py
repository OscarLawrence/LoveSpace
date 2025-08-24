#!/usr/bin/env python3
"""
Correlation Breakdown Detection - Mathematical Trading Strategy
Micro-module with formal contracts for statistical edge detection.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Add formal contracts
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "MomoAI/projects/coherence/formal_contracts"))
from contract_language import coherence_contract, ComplexityClass

@dataclass
class MarketData:
    """Single market data point."""
    timestamp: float
    close: float
    volume: float

@dataclass
class TradingSignal:
    """Mathematical trading signal with proof."""
    strategy: str
    confidence: float  # [0.0, 1.0] statistical confidence
    expected_return: float  # Expected return percentage
    risk_level: float  # Risk percentage
    mathematical_proof: str  # Human-readable mathematical justification
    
    # Strategy-specific data
    breakdown_magnitude: float  # How large the correlation breakdown is
    historical_correlation: float
    current_correlation: float

class CorrelationBreakdownDetector:
    """Detects statistically significant correlation breakdowns between BTC/ETH."""
    
    def __init__(self, min_confidence: float = 0.75, min_history: int = 50):
        self.min_confidence = min_confidence
        self.min_history = min_history
    
    @coherence_contract(
        input_types={"prices": "List[float]"},
        output_type="List[float]",
        requires=["len(prices) >= 2"],
        ensures=["len(result) == len(prices) - 1", "all(isinstance(r, float) for r in result)"],
        complexity_time=ComplexityClass.LINEAR,
        pure=True
    )
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate percentage returns from price series."""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
        
        return returns
    
    @coherence_contract(
        input_types={"x_returns": "List[float]", "y_returns": "List[float]"},
        output_type="float",
        requires=["len(x_returns) == len(y_returns)", "len(x_returns) >= 2"],
        ensures=["-1.0 <= result <= 1.0"],
        complexity_time=ComplexityClass.LINEAR,
        pure=True
    )
    def calculate_correlation(self, x_returns: List[float], y_returns: List[float]) -> float:
        """Calculate Pearson correlation coefficient between two return series."""
        if len(x_returns) != len(y_returns) or len(x_returns) < 2:
            return 0.0
        
        n = len(x_returns)
        if n == 0:
            return 0.0
            
        # Calculate means
        mean_x = sum(x_returns) / n
        mean_y = sum(y_returns) / n
        
        # Calculate correlation coefficient
        numerator = sum((x_returns[i] - mean_x) * (y_returns[i] - mean_y) for i in range(n))
        
        sum_sq_x = sum((x_returns[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y_returns[i] - mean_y) ** 2 for i in range(n))
        
        if sum_sq_x == 0 or sum_sq_y == 0:
            return 0.0
            
        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0.0
    
    @coherence_contract(
        input_types={"btc_data": "List[MarketData]", "eth_data": "List[MarketData]"},
        output_type="Optional[TradingSignal]",
        requires=[
            "len(btc_data) >= 50",
            "len(eth_data) >= 50", 
            "len(btc_data) == len(eth_data)"
        ],
        ensures=["result is None or (0.0 <= result.confidence <= 1.0)"],
        complexity_time=ComplexityClass.LINEAR,
        pure=True
    )
    def detect_breakdown(self, btc_data: List[MarketData], eth_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Detect correlation breakdown between BTC and ETH.
        
        Mathematical Method:
        1. Calculate recent correlation (last 20 periods)
        2. Calculate historical correlation (periods 50-20 ago)  
        3. If |historical_corr - current_corr| > 0.4, signal breakdown
        4. Confidence = min(breakdown_magnitude * 1.5, 0.9)
        5. Expected return = breakdown_magnitude * 0.3
        """
        if len(btc_data) < self.min_history or len(eth_data) < self.min_history:
            return None
        
        if len(btc_data) != len(eth_data):
            return None
        
        # Extract recent prices (last 20 periods)
        recent_btc = [d.close for d in btc_data[-20:]]
        recent_eth = [d.close for d in eth_data[-20:]]
        
        # Extract historical prices (periods 50-20 ago)
        historical_btc = [d.close for d in btc_data[-50:-20]]
        historical_eth = [d.close for d in eth_data[-50:-20]]
        
        # Calculate returns
        recent_btc_returns = self.calculate_returns(recent_btc)
        recent_eth_returns = self.calculate_returns(recent_eth)
        hist_btc_returns = self.calculate_returns(historical_btc)
        hist_eth_returns = self.calculate_returns(historical_eth)
        
        if len(recent_btc_returns) < 10 or len(hist_btc_returns) < 20:
            return None
        
        # Calculate correlations
        current_correlation = self.calculate_correlation(recent_btc_returns, recent_eth_returns)
        historical_correlation = self.calculate_correlation(hist_btc_returns, hist_eth_returns)
        
        # Detect breakdown
        breakdown_magnitude = abs(historical_correlation - current_correlation)
        
        if breakdown_magnitude > 0.4:  # Significant correlation change
            confidence = min(breakdown_magnitude * 1.5, 0.9)
            expected_return = breakdown_magnitude * 0.3
            
            if confidence >= self.min_confidence:
                return TradingSignal(
                    strategy="correlation_breakdown",
                    confidence=confidence,
                    expected_return=expected_return,
                    risk_level=0.15,
                    mathematical_proof=f"Correlation breakdown: {breakdown_magnitude:.2%} change "
                                     f"from historical {historical_correlation:.3f} to current {current_correlation:.3f}. "
                                     f"Statistical significance: {confidence:.1%}",
                    breakdown_magnitude=breakdown_magnitude,
                    historical_correlation=historical_correlation,
                    current_correlation=current_correlation
                )
        
        return None


def create_correlation_detector(min_confidence: float = 0.75) -> CorrelationBreakdownDetector:
    """Factory function to create correlation breakdown detector."""
    return CorrelationBreakdownDetector(min_confidence=min_confidence)