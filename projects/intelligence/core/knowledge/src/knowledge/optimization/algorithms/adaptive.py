"""
Adaptive optimization algorithm combining multiple approaches
"""

import asyncio
from typing import Dict, Any

from ..data_models import OptimizationContext, OptimizationDecision
from .gradient_descent import GradientDescentOptimizer
from .bayesian import BayesianOptimizer


class AdaptiveOptimizer:
    """Adaptive optimization combining multiple approaches"""
    
    def __init__(self):
        self.gradient_optimizer = GradientDescentOptimizer()
        self.bayesian_optimizer = BayesianOptimizer()
    
    async def optimize(self, context: OptimizationContext,
                     analysis: Dict[str, Any]) -> OptimizationDecision:
        """Adaptive optimization with algorithm blending"""
        gradient_result = await self.gradient_optimizer.optimize(context, analysis)
        bayesian_result = await self.bayesian_optimizer.optimize(context, analysis)
        
        gradient_weight = analysis["optimization_urgency"]
        bayesian_weight = 1 - gradient_weight
        
        if gradient_weight > bayesian_weight:
            primary_result = gradient_result
            secondary_result = bayesian_result
        else:
            primary_result = bayesian_result
            secondary_result = gradient_result
        
        blended_parameters = {}
        for param in primary_result.parameters:
            primary_val = primary_result.parameters[param]
            secondary_val = secondary_result.parameters.get(param, primary_val)
            
            blended_val = (gradient_weight * primary_val + 
                          bayesian_weight * secondary_val)
            blended_parameters[param] = blended_val
        
        expected_improvement = (gradient_weight * primary_result.expected_improvement +
                              bayesian_weight * secondary_result.expected_improvement)
        
        return OptimizationDecision(
            strategy_name=primary_result.strategy_name,
            parameters=blended_parameters,
            expected_improvement=expected_improvement,
            confidence=0.75,
            reasoning="Adaptive optimization blending gradient descent and Bayesian approaches",
            execution_time=0.0
        )
