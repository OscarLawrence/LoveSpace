"""
Reinforcement learning optimization algorithm
"""

import asyncio
import random
import numpy as np
from typing import Dict, Any, Tuple

from ..data_models import OptimizationContext, OptimizationDecision


class ReinforcementOptimizer:
    """Reinforcement learning based optimization"""
    
    def __init__(self, exploration_rate: float = 0.2):
        self.exploration_rate = exploration_rate
        self.q_table = {}
        self.actions = ["aggressive", "balanced", "conservative", "exploratory"]
    
    async def optimize(self, context: OptimizationContext,
                     analysis: Dict[str, Any]) -> OptimizationDecision:
        """Reinforcement learning with epsilon-greedy exploration"""
        state = self._encode_state(context)
        
        if np.random.random() < self.exploration_rate:
            action = self._sample_random_action()
        else:
            action = self._select_best_action(state)
        
        strategy_name, parameters = self._decode_action(action)
        q_value = self._estimate_q_value(state, action)
        
        return OptimizationDecision(
            strategy_name=strategy_name,
            parameters=parameters,
            expected_improvement=q_value,
            confidence=0.65,
            reasoning="Reinforcement learning with epsilon-greedy exploration",
            execution_time=0.0
        )
    
    def _encode_state(self, context: OptimizationContext) -> str:
        """Encode context into state representation"""
        performance_level = "high" if sum(context.current_metrics.values()) > 0.7 else "low"
        trend = "improving" if len(context.historical_performance) > 1 else "stable"
        
        constraint_level = "constrained" if context.system_constraints else "free"
        
        return f"{performance_level}_{trend}_{constraint_level}"
    
    def _sample_random_action(self) -> str:
        """Sample random action for exploration"""
        return random.choice(self.actions)
    
    def _select_best_action(self, state: str) -> str:
        """Select best action based on Q-values"""
        if state not in self.q_table:
            return self._sample_random_action()
        
        state_q_values = self.q_table[state]
        return max(state_q_values, key=state_q_values.get)
    
    def _decode_action(self, action: str) -> Tuple[str, Dict[str, Any]]:
        """Decode action into strategy and parameters"""
        action_mapping = {
            "aggressive": ("high_performance", {"batch_size": 128, "learning_rate": 0.1, "threads": 8}),
            "balanced": ("balanced", {"batch_size": 64, "learning_rate": 0.01, "threads": 4}),
            "conservative": ("stable", {"batch_size": 32, "learning_rate": 0.001, "threads": 2}),
            "exploratory": ("experimental", {"batch_size": 96, "learning_rate": 0.05, "threads": 6})
        }
        
        return action_mapping.get(action, action_mapping["balanced"])
    
    def _estimate_q_value(self, state: str, action: str) -> float:
        """Estimate Q-value for state-action pair"""
        if state not in self.q_table:
            self.q_table[state] = {a: random.uniform(0.3, 0.7) for a in self.actions}
        
        return self.q_table[state].get(action, 0.5)
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value based on experience"""
        if state not in self.q_table:
            self.q_table[state] = {a: 0.5 for a in self.actions}
        
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.5 for a in self.actions}
        
        learning_rate = 0.1
        discount_factor = 0.9
        
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values())
        
        new_q = current_q + learning_rate * (reward + discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
