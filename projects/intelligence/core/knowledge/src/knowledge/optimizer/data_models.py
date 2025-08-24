"""
Data models for optimizer integration
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PerformancePattern:
    """Performance pattern for storage and retrieval"""
    pattern_id: str
    context_type: str
    strategy_name: str
    performance_metrics: Dict[str, float]
    improvement_score: float
    usage_count: int
    success_rate: float
    created_at: float
    last_used: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationSession:
    """Complete optimization session data"""
    session_id: str
    start_time: float
    end_time: Optional[float]
    strategies_used: List[str]
    performance_trajectory: List[Dict[str, float]]
    final_improvement: float
    context_data: Dict[str, Any]
    lessons_learned: List[str] = field(default_factory=list)
