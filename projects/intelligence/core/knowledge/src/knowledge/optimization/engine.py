"""
Main real-time optimization engine
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from collections import deque

from .data_models import OptimizationContext, OptimizationDecision
from .analysis import ContextAnalyzer, AlgorithmSelector
from .validation import DecisionValidator


class RealTimeOptimizationEngine:
    """Core real-time optimization engine with advanced algorithms"""
    
    def __init__(self):
        self.optimization_active = False
        self.current_strategy = None
        self.strategy_history = deque(maxlen=100)
        self.performance_predictions = {}
        
        # Components
        self.context_analyzer = ContextAnalyzer()
        self.algorithm_selector = AlgorithmSelector()
        self.decision_validator = DecisionValidator()
        
        # Learning state
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.strategy_performance_matrix = {}
        self.context_strategy_mapping = {}
        
        # Performance prediction models
        self.prediction_models = {}
        self.model_accuracy = {}
    
    async def optimize(self, context: OptimizationContext) -> OptimizationDecision:
        """Main optimization entry point"""
        start_time = time.time()
        
        # Analyze current context
        context_analysis = self.context_analyzer.analyze_context(context)
        
        # Select optimization algorithm
        algorithm_name = self.algorithm_selector.select_algorithm(context, context_analysis)
        algorithm = self.algorithm_selector.get_algorithm(algorithm_name)
        
        # Execute optimization
        decision = await algorithm.optimize(context, context_analysis)
        
        # Validate decision
        validated_decision = await self.decision_validator.validate_decision(decision, context)
        
        # Update learning state
        await self._update_learning_state(context, validated_decision)
        
        # Record decision
        validated_decision.execution_time = time.time() - start_time
        self.strategy_history.append(validated_decision)
        
        return validated_decision
    
    async def _update_learning_state(self, context: OptimizationContext, decision: OptimizationDecision):
        """Update learning state based on decision"""
        # Update strategy performance matrix
        strategy_name = decision.strategy_name
        if strategy_name not in self.strategy_performance_matrix:
            self.strategy_performance_matrix[strategy_name] = []
        
        self.strategy_performance_matrix[strategy_name].append({
            "expected_improvement": decision.expected_improvement,
            "confidence": decision.confidence,
            "timestamp": time.time()
        })
        
        # Update context-strategy mapping
        context_key = self._encode_context(context)
        if context_key not in self.context_strategy_mapping:
            self.context_strategy_mapping[context_key] = {}
        
        if strategy_name not in self.context_strategy_mapping[context_key]:
            self.context_strategy_mapping[context_key][strategy_name] = 0
        
        self.context_strategy_mapping[context_key][strategy_name] += 1
    
    def _encode_context(self, context: OptimizationContext) -> str:
        """Encode context for mapping purposes"""
        objective = context.optimization_objective.value
        performance_level = "high" if sum(context.current_metrics.values()) > 2.0 else "low"
        constraint_count = len(context.system_constraints)
        
        return f"{objective}_{performance_level}_{constraint_count}"
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get optimization engine summary"""
        return {
            "optimization_active": self.optimization_active,
            "current_strategy": self.current_strategy,
            "total_decisions": len(self.strategy_history),
            "strategy_count": len(self.strategy_performance_matrix),
            "context_mappings": len(self.context_strategy_mapping),
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "recent_decisions": list(self.strategy_history)[-5:] if self.strategy_history else []
        }
