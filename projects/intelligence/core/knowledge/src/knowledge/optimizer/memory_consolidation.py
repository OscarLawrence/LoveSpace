"""
Memory consolidation for optimizer patterns
"""

from typing import Dict, List, Tuple
from collections import defaultdict, deque

from .data_models import PerformancePattern


class MemoryConsolidation:
    """Handles memory consolidation and pattern correlation"""
    
    def __init__(self):
        self.pattern_usage_history: deque = deque(maxlen=1000)
        self.pattern_correlations: Dict[str, List[Tuple[str, float]]] = {}
        self.consolidation_threshold = 10
    
    def record_usage(self, pattern_id: str, improvement: float) -> None:
        """Record pattern usage"""
        import time
        self.pattern_usage_history.append({
            "pattern_id": pattern_id,
            "timestamp": time.time(),
            "improvement": improvement
        })
        
        if len(self.pattern_usage_history) % self.consolidation_threshold == 0:
            self.consolidate_memory({})
    
    def consolidate_memory(self, performance_patterns: Dict[str, PerformancePattern]) -> None:
        """Consolidate memory by identifying and strengthening important patterns"""
        pattern_usage_counts = defaultdict(int)
        for usage in self.pattern_usage_history:
            pattern_usage_counts[usage["pattern_id"]] += 1
        
        successful_patterns = [
            pattern_id for pattern_id, pattern in performance_patterns.items()
            if pattern.success_rate > 0.7 and pattern.usage_count >= 3
        ]
        
        for i, pattern1 in enumerate(successful_patterns):
            for pattern2 in successful_patterns[i+1:]:
                correlation_strength = self._calculate_pattern_correlation(
                    pattern1, pattern2, performance_patterns
                )
                
                if correlation_strength > 0.5:
                    if pattern1 not in self.pattern_correlations:
                        self.pattern_correlations[pattern1] = []
                    self.pattern_correlations[pattern1].append((pattern2, correlation_strength))
    
    def _calculate_pattern_correlation(self, pattern_id1: str, pattern_id2: str,
                                     performance_patterns: Dict[str, PerformancePattern]) -> float:
        """Calculate correlation between two patterns"""
        pattern1 = performance_patterns.get(pattern_id1)
        pattern2 = performance_patterns.get(pattern_id2)
        
        if not pattern1 or not pattern2:
            return 0.0
        
        context_similarity = 1.0 if pattern1.context_type == pattern2.context_type else 0.0
        performance_similarity = self._calculate_pattern_similarity(
            pattern1.performance_metrics, pattern2.performance_metrics
        )
        
        return (context_similarity + performance_similarity) / 2.0
    
    def _calculate_pattern_similarity(self, metrics1: Dict[str, float],
                                    metrics2: Dict[str, float]) -> float:
        """Calculate similarity between two metric sets"""
        import numpy as np
        
        common_metrics = set(metrics1.keys()) & set(metrics2.keys())
        
        if not common_metrics:
            return 0.0
        
        vec1 = np.array([metrics1[metric] for metric in common_metrics])
        vec2 = np.array([metrics2[metric] for metric in common_metrics])
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        cosine_sim = np.dot(vec1, vec2) / (norm1 * norm2)
        return max(0.0, cosine_sim)
