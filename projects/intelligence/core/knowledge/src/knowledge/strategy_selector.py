"""
Strategy Selector - Intelligent strategy selection
Context-aware optimization strategy selection
"""

import asyncio
from typing import Dict, List, Any, Optional
import numpy as np
from enum import Enum
from dataclasses import dataclass


class ContextType(Enum):
    """Different context types for strategy selection"""
    CODE_GENERATION = "code_generation"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    GENERAL = "general"


@dataclass
class SelectionCriteria:
    """Criteria for strategy selection"""
    context_type: ContextType
    priority_metric: str
    performance_threshold: float
    resource_constraints: Dict[str, float]


class StrategySelector:
    """Intelligent strategy selection system"""
    
    def __init__(self):
        self.selection_history: List[Dict[str, Any]] = []
        self.context_performance: Dict[str, Dict[str, float]] = {}
        self.strategy_rankings: Dict[str, float] = {}
        
        # Context-specific strategy preferences
        self.context_preferences = {
            ContextType.CODE_GENERATION: {
                "preferred_metrics": ["accuracy", "quality"],
                "strategy_bias": {"high_accuracy": 1.2, "quality_focused": 1.1}
            },
            ContextType.DOCUMENTATION: {
                "preferred_metrics": ["quality", "coherence"],
                "strategy_bias": {"quality_focused": 1.3, "balanced": 1.1}
            },
            ContextType.ANALYSIS: {
                "preferred_metrics": ["accuracy", "coherence"],
                "strategy_bias": {"high_accuracy": 1.2, "balanced": 1.1}
            },
            ContextType.DEBUGGING: {
                "preferred_metrics": ["accuracy", "speed"],
                "strategy_bias": {"high_accuracy": 1.3, "high_speed": 1.1}
            },
            ContextType.OPTIMIZATION: {
                "preferred_metrics": ["efficiency", "speed"],
                "strategy_bias": {"high_speed": 1.2, "balanced": 1.1}
            },
            ContextType.GENERAL: {
                "preferred_metrics": ["accuracy", "quality", "speed"],
                "strategy_bias": {"balanced": 1.2}
            }
        }
    
    async def select_strategy(self, current_metrics: 'PerformanceMetrics',
                            available_strategies: Dict[str, 'OptimizationStrategy'],
                            optimization_mode: 'OptimizationMode') -> 'OptimizationStrategy':
        """Select optimal strategy based on current context and performance"""
        
        # Determine context type
        context_type = self._determine_context_type(current_metrics)
        
        # Calculate strategy scores
        strategy_scores = {}
        for name, strategy in available_strategies.items():
            score = await self._calculate_strategy_score(
                strategy, current_metrics, context_type, optimization_mode
            )
            strategy_scores[name] = score
        
        # Select best strategy
        best_strategy_name = max(strategy_scores, key=strategy_scores.get)
        selected_strategy = available_strategies[best_strategy_name]
        
        # Record selection
        self._record_selection(selected_strategy, current_metrics, context_type, strategy_scores)
        
        return selected_strategy
    
    def _determine_context_type(self, metrics: 'PerformanceMetrics') -> ContextType:
        """Determine current context type from metrics and environment"""
        context_info = metrics.context
        
        # Simple heuristic-based context detection
        if "code" in str(context_info).lower():
            return ContextType.CODE_GENERATION
        elif "doc" in str(context_info).lower():
            return ContextType.DOCUMENTATION
        elif "debug" in str(context_info).lower():
            return ContextType.DEBUGGING
        elif "analyze" in str(context_info).lower():
            return ContextType.ANALYSIS
        elif "optimize" in str(context_info).lower():
            return ContextType.OPTIMIZATION
        else:
            return ContextType.GENERAL
    
    async def _calculate_strategy_score(self, strategy: 'OptimizationStrategy',
                                      current_metrics: 'PerformanceMetrics',
                                      context_type: ContextType,
                                      optimization_mode: 'OptimizationMode') -> float:
        """Calculate comprehensive strategy score"""
        
        # Base effectiveness score
        base_score = strategy.effectiveness_score
        
        # Context-specific adjustments
        context_score = self._calculate_context_score(strategy, context_type)
        
        # Performance gap analysis
        gap_score = self._calculate_performance_gap_score(strategy, current_metrics)
        
        # Mode-specific adjustments
        mode_score = self._calculate_mode_score(strategy, optimization_mode)
        
        # Historical performance
        history_score = self._calculate_history_score(strategy, context_type)
        
        # Combine scores with weights
        total_score = (
            base_score * 0.3 +
            context_score * 0.25 +
            gap_score * 0.2 +
            mode_score * 0.15 +
            history_score * 0.1
        )
        
        return total_score
    
    def _calculate_context_score(self, strategy: 'OptimizationStrategy',
                               context_type: ContextType) -> float:
        """Calculate context-specific strategy score"""
        if context_type not in self.context_preferences:
            return 0.5
        
        preferences = self.context_preferences[context_type]
        
        # Check strategy bias
        strategy_bias = preferences["strategy_bias"].get(strategy.name, 1.0)
        
        # Check metric alignment
        preferred_metrics = preferences["preferred_metrics"]
        metric_alignment = 0.0
        
        for metric in preferred_metrics:
            if metric in strategy.priority_weights:
                metric_alignment += strategy.priority_weights[metric]
        
        metric_alignment /= len(preferred_metrics)
        
        return (strategy_bias * 0.6 + metric_alignment * 0.4) / 1.6
    
    def _calculate_performance_gap_score(self, strategy: 'OptimizationStrategy',
                                       current_metrics: 'PerformanceMetrics') -> float:
        """Calculate score based on performance gaps"""
        gap_score = 0.0
        total_weight = 0.0
        
        # Performance targets (should be configurable)
        targets = {
            "accuracy": 0.95,
            "speed": 100.0,
            "quality": 0.90,
            "coherence": 0.85,
            "efficiency": 0.80
        }
        
        for metric, weight in strategy.priority_weights.items():
            current_value = getattr(current_metrics, metric, 0.0)
            target_value = targets.get(metric, 1.0)
            
            if current_value < target_value:
                # Strategy gets higher score if it prioritizes metrics we're lacking
                gap = target_value - current_value
                gap_score += gap * weight
            
            total_weight += weight
        
        return gap_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_mode_score(self, strategy: 'OptimizationStrategy',
                            optimization_mode: 'OptimizationMode') -> float:
        """Calculate mode-specific strategy score"""
        from .optimizer import OptimizationMode
        
        mode_preferences = {
            OptimizationMode.ACCURACY: {"accuracy": 1.5, "quality": 1.2},
            OptimizationMode.SPEED: {"speed": 1.5, "efficiency": 1.2},
            OptimizationMode.QUALITY: {"quality": 1.5, "coherence": 1.2},
            OptimizationMode.BALANCED: {"accuracy": 1.1, "speed": 1.1, "quality": 1.1},
            OptimizationMode.ADAPTIVE: {}  # No specific preferences
        }
        
        if optimization_mode not in mode_preferences:
            return 0.5
        
        preferences = mode_preferences[optimization_mode]
        if not preferences:  # Adaptive mode
            return 0.5
        
        score = 0.0
        total_weight = 0.0
        
        for metric, preference_weight in preferences.items():
            strategy_weight = strategy.priority_weights.get(metric, 0.0)
            score += strategy_weight * preference_weight
            total_weight += preference_weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_history_score(self, strategy: 'OptimizationStrategy',
                               context_type: ContextType) -> float:
        """Calculate score based on historical performance in this context"""
        context_key = f"{strategy.name}_{context_type.value}"
        
        if context_key not in self.context_performance:
            return 0.5  # Neutral score for unknown performance
        
        performance_data = self.context_performance[context_key]
        
        # Calculate weighted average of recent performance
        recent_scores = list(performance_data.values())[-10:]  # Last 10 records
        
        if not recent_scores:
            return 0.5
        
        # Apply exponential weighting to recent scores
        weights = np.exp(np.linspace(-1, 0, len(recent_scores)))
        return float(np.average(recent_scores, weights=weights))
    
    def _record_selection(self, strategy: 'OptimizationStrategy',
                         metrics: 'PerformanceMetrics',
                         context_type: ContextType,
                         all_scores: Dict[str, float]) -> None:
        """Record strategy selection for learning"""
        selection_record = {
            "strategy_name": strategy.name,
            "context_type": context_type.value,
            "timestamp": metrics.timestamp,
            "metrics": {
                "accuracy": metrics.accuracy,
                "speed": metrics.speed,
                "quality": metrics.quality,
                "coherence": metrics.coherence,
                "efficiency": metrics.efficiency
            },
            "all_scores": all_scores
        }
        
        self.selection_history.append(selection_record)
        
        # Update context performance tracking
        context_key = f"{strategy.name}_{context_type.value}"
        if context_key not in self.context_performance:
            self.context_performance[context_key] = {}
        
        # Use timestamp as key for performance tracking
        self.context_performance[context_key][metrics.timestamp] = all_scores[strategy.name]
    
    def update_strategy_performance(self, strategy_name: str, context_type: ContextType,
                                  performance_score: float, timestamp: float) -> None:
        """Update strategy performance based on actual results"""
        context_key = f"{strategy_name}_{context_type.value}"
        
        if context_key not in self.context_performance:
            self.context_performance[context_key] = {}
        
        self.context_performance[context_key][timestamp] = performance_score
        
        # Update overall strategy ranking
        self._update_strategy_rankings()
    
    def _update_strategy_rankings(self) -> None:
        """Update overall strategy rankings based on performance history"""
        strategy_scores = {}
        
        for context_key, performance_data in self.context_performance.items():
            strategy_name = context_key.split('_')[0]
            
            if strategy_name not in strategy_scores:
                strategy_scores[strategy_name] = []
            
            # Add recent performance scores
            recent_scores = list(performance_data.values())[-20:]
            strategy_scores[strategy_name].extend(recent_scores)
        
        # Calculate overall rankings
        for strategy_name, scores in strategy_scores.items():
            if scores:
                # Use exponential weighting for recent bias
                weights = np.exp(np.linspace(-1, 0, len(scores)))
                self.strategy_rankings[strategy_name] = float(np.average(scores, weights=weights))
    
    def get_selection_summary(self) -> Dict[str, Any]:
        """Get comprehensive selection summary"""
        return {
            "total_selections": len(self.selection_history),
            "context_performance": {
                context: {
                    "selections": len(perf_data),
                    "avg_score": np.mean(list(perf_data.values())) if perf_data else 0
                }
                for context, perf_data in self.context_performance.items()
            },
            "strategy_rankings": self.strategy_rankings,
            "recent_selections": [
                {
                    "strategy": record["strategy_name"],
                    "context": record["context_type"],
                    "timestamp": record["timestamp"]
                }
                for record in self.selection_history[-10:]
            ]
        }