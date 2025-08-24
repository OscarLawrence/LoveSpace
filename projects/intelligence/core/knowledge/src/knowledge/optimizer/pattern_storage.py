"""
Pattern storage and retrieval for optimizer
"""

import time
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from pathlib import Path

from .data_models import PerformancePattern


class PatternStorage:
    """Storage and retrieval of performance patterns"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.performance_patterns: Dict[str, PerformancePattern] = {}
        self.pattern_correlations: Dict[str, List[Tuple[str, float]]] = {}
        
    def store_pattern(self, context_type: str, strategy_name: str,
                     performance_metrics: Dict[str, float],
                     improvement_score: float,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a performance pattern"""
        if metadata is None:
            metadata = {}
        
        pattern_id = self._generate_pattern_id(context_type, strategy_name)
        current_time = time.time()
        
        if pattern_id in self.performance_patterns:
            pattern = self.performance_patterns[pattern_id]
            pattern.usage_count += 1
            pattern.last_used = current_time
            
            success = 1.0 if improvement_score > 0 else 0.0
            pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + success) / pattern.usage_count
            
            alpha = 0.3
            for metric, value in performance_metrics.items():
                if metric in pattern.performance_metrics:
                    pattern.performance_metrics[metric] = (
                        alpha * value + (1 - alpha) * pattern.performance_metrics[metric]
                    )
                else:
                    pattern.performance_metrics[metric] = value
            
            pattern.improvement_score = (
                alpha * improvement_score + (1 - alpha) * pattern.improvement_score
            )
        else:
            pattern = PerformancePattern(
                pattern_id=pattern_id,
                context_type=context_type,
                strategy_name=strategy_name,
                performance_metrics=performance_metrics.copy(),
                improvement_score=improvement_score,
                usage_count=1,
                success_rate=1.0 if improvement_score > 0 else 0.0,
                created_at=current_time,
                last_used=current_time,
                metadata=metadata
            )
            self.performance_patterns[pattern_id] = pattern
        
        self._save_pattern(pattern)
        return pattern_id
    
    def retrieve_similar_patterns(self, context_type: str, 
                                current_metrics: Dict[str, float],
                                top_k: int = 5) -> List[Tuple[PerformancePattern, float]]:
        """Retrieve patterns similar to current context"""
        candidates = [
            pattern for pattern in self.performance_patterns.values()
            if pattern.context_type == context_type
        ]
        
        if not candidates:
            return []
        
        pattern_similarities = []
        for pattern in candidates:
            similarity = self._calculate_pattern_similarity(
                current_metrics, pattern.performance_metrics
            )
            pattern_similarities.append((pattern, similarity))
        
        pattern_similarities.sort(key=lambda x: x[1], reverse=True)
        return pattern_similarities[:top_k]
    
    def _generate_pattern_id(self, context_type: str, strategy_name: str) -> str:
        """Generate unique pattern ID"""
        return f"{context_type}_{strategy_name}_{hash(f'{context_type}{strategy_name}') % 10000}"
    
    def _calculate_pattern_similarity(self, metrics1: Dict[str, float],
                                    metrics2: Dict[str, float]) -> float:
        """Calculate similarity between two metric sets"""
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
    
    def _save_pattern(self, pattern: PerformancePattern) -> None:
        """Save pattern to persistent storage"""
        pattern_file = self.storage_path / f"pattern_{pattern.pattern_id}.json"
        
        pattern_data = {
            "pattern_id": pattern.pattern_id,
            "context_type": pattern.context_type,
            "strategy_name": pattern.strategy_name,
            "performance_metrics": pattern.performance_metrics,
            "improvement_score": pattern.improvement_score,
            "usage_count": pattern.usage_count,
            "success_rate": pattern.success_rate,
            "created_at": pattern.created_at,
            "last_used": pattern.last_used,
            "metadata": pattern.metadata
        }
        
        with open(pattern_file, 'w') as f:
            json.dump(pattern_data, f, indent=2)
    
    def load_patterns(self) -> None:
        """Load patterns from persistent storage"""
        if not self.storage_path.exists():
            return
        
        for pattern_file in self.storage_path.glob("pattern_*.json"):
            try:
                with open(pattern_file, 'r') as f:
                    pattern_data = json.load(f)
                
                pattern = PerformancePattern(**pattern_data)
                self.performance_patterns[pattern.pattern_id] = pattern
                
            except Exception as e:
                print(f"Error loading pattern from {pattern_file}: {e}")
