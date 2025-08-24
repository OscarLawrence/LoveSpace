"""
Data models for optimization engine
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


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

    current_metrics: dict[str, float]
    historical_performance: list[dict[str, float]]
    system_constraints: dict[str, Any]
    optimization_objective: OptimizationObjective
    time_horizon: float  # seconds
    priority_weights: dict[str, float]


@dataclass
class OptimizationDecision:
    """Optimization decision output"""

    strategy_name: str
    parameters: dict[str, Any]
    expected_improvement: float
    confidence: float
    reasoning: str
    execution_time: float
