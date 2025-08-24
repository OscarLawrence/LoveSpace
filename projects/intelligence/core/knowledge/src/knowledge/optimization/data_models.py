"""
Data models for optimization engine
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class OptimizationObjective(Enum):
    """Optimization objectives"""
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    BALANCE_ALL = "balance_all"
    CUSTOM = "custom"


@dataclass
class OptimizationContext:
    """Context for optimization decisions"""
    current_metrics: Dict[str, float]
    historical_performance: List[Dict[str, float]]
    system_constraints: Dict[str, Any]
    optimization_objective: OptimizationObjective
    time_horizon: float  # seconds
    priority_weights: Dict[str, float]


@dataclass
class OptimizationDecision:
    """Optimization decision output"""
    strategy_name: str
    parameters: Dict[str, Any]
    expected_improvement: float
    confidence: float
    reasoning: str
    execution_time: float
