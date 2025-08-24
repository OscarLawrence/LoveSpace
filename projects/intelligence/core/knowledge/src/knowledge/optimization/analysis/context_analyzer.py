"""
Context analysis for optimization decisions
"""

import numpy as np
from typing import Dict, List, Any

from ..data_models import OptimizationContext


class ContextAnalyzer:
    """Analyzes optimization context for decision making"""
    
    def __init__(self):
        pass
    
    def analyze_context(self, context: OptimizationContext) -> Dict[str, Any]:
        """Analyze optimization context"""
        analysis = {
            "performance_trend": self._calculate_performance_trend(context.historical_performance),
            "constraint_violations": self._check_constraint_violations(context),
            "optimization_urgency": self._calculate_optimization_urgency(context),
            "resource_availability": self._assess_resource_availability(context),
            "prediction_confidence": self._get_prediction_confidence(context)
        }
        
        return analysis
    
    def _calculate_performance_trend(self, historical_performance: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate performance trends from historical data"""
        if len(historical_performance) < 2:
            return {"accuracy": 0, "speed": 0, "quality": 0}
        
        trends = {}
        for metric in ["accuracy", "speed", "quality"]:
            values = [perf.get(metric, 0) for perf in historical_performance]
            if len(values) >= 2:
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                trends[metric] = slope
            else:
                trends[metric] = 0
        
        return trends
    
    def _check_constraint_violations(self, context: OptimizationContext) -> List[str]:
        """Check for constraint violations"""
        violations = []
        constraints = context.system_constraints
        current_metrics = context.current_metrics
        
        for constraint_name, constraint_value in constraints.items():
            if constraint_name in current_metrics:
                if isinstance(constraint_value, dict):
                    min_val = constraint_value.get("min")
                    max_val = constraint_value.get("max")
                    current_val = current_metrics[constraint_name]
                    
                    if min_val and current_val < min_val:
                        violations.append(f"{constraint_name} below minimum")
                    if max_val and current_val > max_val:
                        violations.append(f"{constraint_name} above maximum")
        
        return violations
    
    def _calculate_optimization_urgency(self, context: OptimizationContext) -> float:
        """Calculate how urgently optimization is needed"""
        current_metrics = context.current_metrics
        urgency_factors = []
        
        accuracy = current_metrics.get("accuracy", 1.0)
        if accuracy < 0.8:
            urgency_factors.append((0.8 - accuracy) * 2)
        
        speed = current_metrics.get("speed", 100.0)
        if speed < 50.0:
            urgency_factors.append((50.0 - speed) / 50.0)
        
        quality = current_metrics.get("quality", 1.0)
        if quality < 0.7:
            urgency_factors.append((0.7 - quality) * 1.5)
        
        if not urgency_factors:
            return 0.1
        
        return min(np.mean(urgency_factors), 1.0)
    
    def _assess_resource_availability(self, context: OptimizationContext) -> Dict[str, float]:
        """Assess available computational resources"""
        return {
            "cpu": 0.7,
            "memory": 0.8,
            "network": 0.9,
            "optimization_budget": 1.0
        }
    
    def _get_prediction_confidence(self, context: OptimizationContext) -> float:
        """Get confidence in performance predictions"""
        historical_count = len(context.historical_performance)
        
        if historical_count < 5:
            return 0.3
        elif historical_count < 20:
            return 0.6
        else:
            return 0.8
