"""
Strategy recommendation engine
"""

import numpy as np
from typing import Dict, List, Any
from collections import defaultdict

from .pattern_storage import PatternStorage


class RecommendationEngine:
    """Generates strategy recommendations based on patterns"""
    
    def __init__(self, pattern_storage: PatternStorage):
        self.pattern_storage = pattern_storage
    
    def get_recommendations(self, context_type: str,
                          current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get strategy recommendations based on memory"""
        similar_patterns = self.pattern_storage.retrieve_similar_patterns(
            context_type, current_metrics
        )
        
        if not similar_patterns:
            return []
        
        strategy_scores = defaultdict(list)
        for pattern, similarity in similar_patterns:
            strategy_scores[pattern.strategy_name].append({
                "similarity": similarity,
                "success_rate": pattern.success_rate,
                "improvement_score": pattern.improvement_score,
                "usage_count": pattern.usage_count
            })
        
        recommendations = []
        for strategy_name, scores in strategy_scores.items():
            weights = [score["similarity"] for score in scores]
            total_weight = sum(weights)
            
            if total_weight == 0:
                continue
            
            avg_success_rate = sum(
                score["success_rate"] * score["similarity"] for score in scores
            ) / total_weight
            
            avg_improvement = sum(
                score["improvement_score"] * score["similarity"] for score in scores
            ) / total_weight
            
            total_usage = sum(score["usage_count"] for score in scores)
            
            confidence = min(total_usage / 10.0, 1.0) * (total_weight / len(scores))
            
            recommendations.append({
                "strategy_name": strategy_name,
                "expected_success_rate": avg_success_rate,
                "expected_improvement": avg_improvement,
                "confidence": confidence,
                "supporting_patterns": len(scores),
                "total_usage": total_usage
            })
        
        recommendations.sort(
            key=lambda x: x["expected_improvement"] * x["confidence"],
            reverse=True
        )
        
        return recommendations
