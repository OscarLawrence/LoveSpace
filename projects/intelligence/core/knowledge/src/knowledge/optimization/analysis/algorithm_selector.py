"""
Algorithm selection logic for optimization
"""

from typing import Dict, Any, Callable

from ..data_models import OptimizationContext
from ..algorithms import (
    GradientDescentOptimizer,
    BayesianOptimizer,
    GeneticOptimizer,
    ReinforcementOptimizer,
    AdaptiveOptimizer
)


class AlgorithmSelector:
    """Selects appropriate optimization algorithm based on context"""
    
    def __init__(self):
        self.algorithms = {
            "gradient_descent": GradientDescentOptimizer(),
            "bayesian": BayesianOptimizer(),
            "genetic": GeneticOptimizer(),
            "reinforcement": ReinforcementOptimizer(),
            "adaptive": AdaptiveOptimizer()
        }
    
    def select_algorithm(self, context: OptimizationContext, analysis: Dict[str, Any]) -> str:
        """Select appropriate optimization algorithm"""
        urgency = analysis["optimization_urgency"]
        confidence = analysis["prediction_confidence"]
        
        # High urgency + high confidence = gradient descent (fast)
        if urgency > 0.8 and confidence > 0.7:
            return "gradient_descent"
        
        # Low confidence = exploration with genetic algorithm
        elif confidence < 0.4:
            return "genetic"
        
        # Balanced situation = adaptive algorithm
        elif 0.4 <= urgency <= 0.8:
            return "adaptive"
        
        # Complex optimization = Bayesian
        else:
            return "bayesian"
    
    def get_algorithm(self, algorithm_name: str):
        """Get algorithm instance by name"""
        return self.algorithms.get(algorithm_name)
