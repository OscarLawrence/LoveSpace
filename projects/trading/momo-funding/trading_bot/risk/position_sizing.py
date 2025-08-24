#!/usr/bin/env python3
"""
Position Sizing - Mathematical Risk Management
Micro-module implementing Kelly Criterion with volatility adjustments.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import math

# Add formal contracts
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "MomoAI/projects/coherence/formal_contracts"))
from contract_language import coherence_contract, ComplexityClass

class KellyPositionSizer:
    """Kelly Criterion position sizing with safety factors and volatility adjustments."""
    
    def __init__(self, safety_factor: float = 0.25, max_position: float = 0.02):
        """
        Initialize Kelly position sizer.
        
        Args:
            safety_factor: Fraction of Kelly bet (0.25 = 25% of full Kelly)
            max_position: Maximum position size as fraction of capital (0.02 = 2%)
        """
        self.safety_factor = safety_factor
        self.max_position = max_position
    
    @coherence_contract(
        input_types={"win_prob": "float", "expected_return": "float", "risk_level": "float"},
        output_type="float",
        requires=[
            "0.0 <= win_prob <= 1.0",
            "expected_return > 0.0",
            "risk_level > 0.0"
        ],
        ensures=["result >= 0.0"],
        complexity_time=ComplexityClass.CONSTANT,
        pure=True
    )
    def calculate_kelly_fraction(self, win_prob: float, expected_return: float, risk_level: float) -> float:
        """
        Calculate Kelly fraction for optimal position sizing.
        
        Kelly Formula: f = (bp - q) / b
        Where:
        - f = fraction of capital to bet
        - b = odds of winning (expected_return / risk_level)
        - p = probability of winning (confidence)
        - q = probability of losing (1 - p)
        """
        if risk_level <= 0 or expected_return <= 0:
            return 0.0
        
        b = expected_return / risk_level  # Reward/risk ratio
        p = win_prob
        q = 1.0 - p
        
        if b <= 0:
            return 0.0
        
        kelly_fraction = (b * p - q) / b
        
        # Ensure non-negative (return 0 if expected value is negative)
        # This handles cases where risk > expected return
        return max(0.0, kelly_fraction)
    
    @coherence_contract(
        input_types={
            "confidence": "float", 
            "expected_return": "float", 
            "risk_level": "float",
            "capital": "float"
        },
        output_type="float",
        requires=[
            "0.0 <= confidence <= 1.0",
            "expected_return >= 0.0",
            "risk_level > 0.0", 
            "capital > 0.0"
        ],
        ensures=["0.0 <= result <= capital"],
        complexity_time=ComplexityClass.CONSTANT,
        pure=True
    )
    def calculate_position_size(self, confidence: float, expected_return: float, 
                              risk_level: float, capital: float) -> float:
        """
        Calculate optimal position size using Kelly criterion with safety factors.
        
        Args:
            confidence: Statistical confidence [0.0, 1.0] 
            expected_return: Expected return percentage
            risk_level: Risk percentage
            capital: Available capital
            
        Returns:
            Position size in dollars
        """
        if capital <= 0 or expected_return <= 0 or risk_level <= 0:
            return 0.0
        
        # Calculate raw Kelly fraction
        kelly_fraction = self.calculate_kelly_fraction(confidence, expected_return, risk_level)
        
        # Apply safety factor (never bet full Kelly)
        adjusted_fraction = kelly_fraction * self.safety_factor
        
        # Apply maximum position constraint
        final_fraction = min(adjusted_fraction, self.max_position)
        
        # Calculate position size
        position_size = capital * final_fraction
        
        return max(0.0, position_size)
    
    @coherence_contract(
        input_types={"position_size": "float", "min_trade": "float"},
        output_type="bool",
        requires=["position_size >= 0.0", "min_trade >= 0.0"],
        ensures=["result in [True, False]"],
        complexity_time=ComplexityClass.CONSTANT,
        pure=True
    )
    def is_position_viable(self, position_size: float, min_trade: float = 10.0) -> bool:
        """Check if calculated position size meets minimum trading requirements."""
        return position_size >= min_trade


class VolatilityAdjustedSizer:
    """Position sizer that adjusts Kelly based on market volatility."""
    
    def __init__(self, kelly_sizer: KellyPositionSizer, base_volatility: float = 0.02):
        self.kelly_sizer = kelly_sizer
        self.base_volatility = base_volatility
    
    @coherence_contract(
        input_types={"prices": "List[float]"},
        output_type="float",
        requires=["len(prices) >= 2"],
        ensures=["result >= 0.0"],
        complexity_time=ComplexityClass.LINEAR,
        pure=True
    )
    def calculate_volatility(self, prices: List[float]) -> float:
        """Calculate realized volatility from price series."""
        if len(prices) < 2:
            return 0.0
        
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
        
        if len(returns) < 2:
            return 0.0
        
        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        
        return math.sqrt(variance)
    
    @coherence_contract(
        input_types={
            "confidence": "float",
            "expected_return": "float", 
            "risk_level": "float",
            "capital": "float",
            "recent_prices": "List[float]"
        },
        output_type="float",
        requires=[
            "0.0 <= confidence <= 1.0",
            "expected_return >= 0.0",
            "risk_level > 0.0",
            "capital > 0.0"
        ],
        ensures=["0.0 <= result <= capital"],
        complexity_time=ComplexityClass.LINEAR,
        pure=True
    )
    def calculate_volatility_adjusted_position(self, confidence: float, expected_return: float,
                                             risk_level: float, capital: float,
                                             recent_prices: List[float]) -> float:
        """
        Calculate position size adjusted for current market volatility.
        
        Lower position sizes in high volatility environments.
        """
        # Get base Kelly position
        base_position = self.kelly_sizer.calculate_position_size(
            confidence, expected_return, risk_level, capital
        )
        
        if len(recent_prices) < 2:
            return base_position
        
        # Calculate current volatility
        current_volatility = self.calculate_volatility(recent_prices)
        
        # Volatility adjustment factor
        volatility_adjustment = min(1.0, self.base_volatility / max(current_volatility, 0.001))
        
        # Apply volatility adjustment
        adjusted_position = base_position * volatility_adjustment
        
        return max(0.0, adjusted_position)


def create_position_sizer(safety_factor: float = 0.25, max_position: float = 0.02) -> KellyPositionSizer:
    """Factory function to create Kelly position sizer."""
    return KellyPositionSizer(safety_factor=safety_factor, max_position=max_position)

def create_volatility_sizer(safety_factor: float = 0.25, max_position: float = 0.02, 
                           base_volatility: float = 0.02) -> VolatilityAdjustedSizer:
    """Factory function to create volatility-adjusted position sizer."""
    kelly_sizer = KellyPositionSizer(safety_factor=safety_factor, max_position=max_position)
    return VolatilityAdjustedSizer(kelly_sizer=kelly_sizer, base_volatility=base_volatility)