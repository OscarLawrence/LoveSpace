"""
Performance analysis for optimizer patterns
"""

import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

from .data_models import PerformancePattern, OptimizationSession


class PerformanceAnalyzer:
    """Analyzes performance patterns and trends"""
    
    def __init__(self):
        self.pattern_usage_history: deque = deque(maxlen=1000)
    
    def analyze_history(self, performance_patterns: Dict[str, PerformancePattern],
                       optimization_sessions: Dict[str, OptimizationSession],
                       context_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze historical performance patterns"""
        if context_type:
            patterns = [p for p in performance_patterns.values() if p.context_type == context_type]
        else:
            patterns = list(performance_patterns.values())
        
        if not patterns:
            return {"error": "No patterns found"}
        
        strategy_performance = defaultdict(list)
        for pattern in patterns:
            strategy_performance[pattern.strategy_name].append(pattern.improvement_score)
        
        strategy_stats = {}
        for strategy, improvements in strategy_performance.items():
            strategy_stats[strategy] = {
                "avg_improvement": np.mean(improvements),
                "success_rate": len([i for i in improvements if i > 0]) / len(improvements),
                "usage_count": len(improvements),
                "improvement_std": np.std(improvements)
            }
        
        context_stats = defaultdict(lambda: {"patterns": 0, "avg_improvement": 0.0})
        for pattern in patterns:
            context_stats[pattern.context_type]["patterns"] += 1
            context_stats[pattern.context_type]["avg_improvement"] += pattern.improvement_score
        
        for context, stats in context_stats.items():
            stats["avg_improvement"] /= stats["patterns"]
        
        recent_usage = list(self.pattern_usage_history)[-100:]
        if recent_usage:
            recent_improvements = [usage["improvement"] for usage in recent_usage]
            learning_trend = np.polyfit(range(len(recent_improvements)), recent_improvements, 1)[0]
        else:
            learning_trend = 0.0
        
        return {
            "total_patterns": len(patterns),
            "strategy_performance": dict(strategy_stats),
            "context_analysis": dict(context_stats),
            "learning_trend": learning_trend,
            "memory_utilization": len(performance_patterns),
            "session_count": len(optimization_sessions)
        }
