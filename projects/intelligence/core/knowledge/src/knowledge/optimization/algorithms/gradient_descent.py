"""
Gradient descent optimization algorithm
"""

import asyncio
from typing import Dict, Any

from ..data_models import OptimizationContext, OptimizationDecision


class GradientDescentOptimizer:
    """Fast gradient descent optimization for urgent situations"""
    
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
    
    async def optimize(self, context: OptimizationContext, 
                     analysis: Dict[str, Any]) -> OptimizationDecision:
        """Fast gradient descent optimization"""
        current_metrics = context.current_metrics
        objective = context.optimization_objective
        
        gradient = self._calculate_performance_gradient(context)
        step_size = analysis["optimization_urgency"] * self.learning_rate
        
        best_strategy = "high_performance"
        parameters = {}
        
        for param_name, current_value in self._get_current_parameters().items():
            gradient_component = gradient.get(param_name, 0)
            new_value = current_value + step_size * gradient_component
            parameters[param_name] = self._clamp_parameter(param_name, new_value)
        
        expected_improvement = self._estimate_improvement(parameters, context)
        
        return OptimizationDecision(
            strategy_name=best_strategy,
            parameters=parameters,
            expected_improvement=expected_improvement,
            confidence=0.8,
            reasoning="Gradient descent optimization for urgent performance improvement",
            execution_time=0.0
        )
    
    def _calculate_performance_gradient(self, context: OptimizationContext) -> Dict[str, float]:
        """Calculate performance gradient"""
        if len(context.historical_performance) < 2:
            return {"batch_size": 0.1, "learning_rate": 0.05, "threads": 1.0}
        
        recent = context.historical_performance[-2:]
        gradient = {}
        
        for metric in context.current_metrics:
            if metric in recent[0] and metric in recent[1]:
                gradient[metric] = (recent[1][metric] - recent[0][metric]) / max(abs(recent[0][metric]), 1e-6)
        
        return gradient
    
    def _get_current_parameters(self) -> Dict[str, float]:
        """Get current system parameters"""
        return {
            "batch_size": 32.0,
            "learning_rate": 0.001,
            "threads": 4.0,
            "cache_size": 1024.0
        }
    
    def _clamp_parameter(self, param_name: str, value: float) -> float:
        """Clamp parameter to valid range"""
        bounds = {
            "batch_size": (1, 256),
            "learning_rate": (1e-6, 1.0),
            "threads": (1, 16),
            "cache_size": (64, 8192)
        }
        
        if param_name in bounds:
            min_val, max_val = bounds[param_name]
            return max(min_val, min(max_val, value))
        
        return value
    
    def _estimate_improvement(self, parameters: Dict[str, Any], context: OptimizationContext) -> float:
        """Estimate performance improvement"""
        if not context.historical_performance:
            return 0.1
        
        current_performance = sum(context.current_metrics.values()) / len(context.current_metrics)
        historical_avg = sum(
            sum(perf.values()) / len(perf) for perf in context.historical_performance[-5:]
        ) / min(len(context.historical_performance), 5)
        
        base_improvement = (current_performance - historical_avg) / max(abs(historical_avg), 1e-6)
        
        parameter_bonus = 0.0
        for param, value in parameters.items():
            if param == "batch_size" and value > 64:
                parameter_bonus += 0.05
            elif param == "threads" and value > 2:
                parameter_bonus += 0.03
        
        return max(0.01, base_improvement + parameter_bonus)
