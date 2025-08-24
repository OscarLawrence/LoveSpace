"""
Data models for optimizer integration
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PerformancePattern:
    """Performance pattern for storage and retrieval"""

    pattern_id: str
    context_type: str
    strategy_name: str
    performance_metrics: dict[str, float]
    improvement_score: float
    usage_count: int
    success_rate: float
    created_at: float
    last_used: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationSession:
    """Complete optimization session data"""

    session_id: str
    start_time: float
    end_time: float | None
    strategies_used: list[str]
    performance_trajectory: list[dict[str, float]]
    final_improvement: float
    context_data: dict[str, Any]
    lessons_learned: list[str] = field(default_factory=list)
