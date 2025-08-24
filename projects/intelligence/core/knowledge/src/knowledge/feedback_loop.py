"""
Feedback Loop - Self-optimizing feedback system
Continuous learning and adaptation based on performance feedback
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import deque, defaultdict
import numpy as np
from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    """Types of feedback for learning"""
    PERFORMANCE = "performance"
    USER = "user"
    SYSTEM = "system"
    AUTOMATED = "automated"


@dataclass
class FeedbackEntry:
    """Individual feedback entry"""
    feedback_type: FeedbackType
    strategy_name: str
    performance_before: Dict[str, float]
    performance_after: Dict[str, float]
    improvement: float
    timestamp: float
    context: Dict[str, Any]


class FeedbackLoop:
    """Self-optimizing feedback system for continuous improvement"""
    
    def __init__(self):
        self.feedback_history: deque = deque(maxlen=1000)
        self.strategy_improvements: Dict[str, List[float]] = defaultdict(list)
        self.learning_patterns: Dict[str, Any] = {}
        self.adaptation_rules: List[Dict[str, Any]] = []
        
        # Learning parameters
        self.learning_rate = 0.1
        self.improvement_threshold = 0.05
        self.pattern_detection_window = 50
        
        # Feedback processing
        self.processing_active = False
        self.last_analysis_time = 0.0
    
    async def process_feedback(self, metrics_history: deque,
                             active_strategies: Dict[str, 'OptimizationStrategy']) -> None:
        """Process performance feedback and adapt strategies"""
        if not metrics_history or len(metrics_history) < 2:
            return
        
        # Analyze recent performance changes
        await self._analyze_performance_changes(metrics_history, active_strategies)
        
        # Detect learning patterns
        await self._detect_learning_patterns()
        
        # Generate adaptation rules
        await self._generate_adaptation_rules()
        
        # Apply learned optimizations
        await self._apply_learned_optimizations(active_strategies)
        
        self.last_analysis_time = time.time()
    
    async def _analyze_performance_changes(self, metrics_history: deque,
                                         active_strategies: Dict[str, 'OptimizationStrategy']) -> None:
        """Analyze performance changes and correlate with strategy usage"""
        if len(metrics_history) < 10:
            return
        
        recent_metrics = list(metrics_history)[-10:]
        
        # Calculate performance trends
        for i in range(1, len(recent_metrics)):
            prev_metrics = recent_metrics[i-1]
            curr_metrics = recent_metrics[i]
            
            # Calculate improvement across all metrics
            improvements = {
                "accuracy": curr_metrics.accuracy - prev_metrics.accuracy,
                "speed": curr_metrics.speed - prev_metrics.speed,
                "quality": curr_metrics.quality - prev_metrics.quality,
                "coherence": curr_metrics.coherence - prev_metrics.coherence,
                "efficiency": curr_metrics.efficiency - prev_metrics.efficiency
            }
            
            # Calculate overall improvement score
            overall_improvement = np.mean(list(improvements.values()))
            
            # Try to correlate with strategy changes
            await self._correlate_with_strategies(
                improvements, overall_improvement, curr_metrics, active_strategies
            )
    
    async def _correlate_with_strategies(self, improvements: Dict[str, float],
                                       overall_improvement: float,
                                       current_metrics: 'PerformanceMetrics',
                                       active_strategies: Dict[str, 'OptimizationStrategy']) -> None:
        """Correlate performance improvements with strategy usage"""
        
        # Find the most recently used strategy (simplified heuristic)
        most_used_strategy = max(active_strategies.values(), 
                               key=lambda s: s.usage_count)
        
        # Record feedback entry
        feedback_entry = FeedbackEntry(
            feedback_type=FeedbackType.AUTOMATED,
            strategy_name=most_used_strategy.name,
            performance_before={},  # Would need previous state
            performance_after={
                "accuracy": current_metrics.accuracy,
                "speed": current_metrics.speed,
                "quality": current_metrics.quality,
                "coherence": current_metrics.coherence,
                "efficiency": current_metrics.efficiency
            },
            improvement=overall_improvement,
            timestamp=current_metrics.timestamp,
            context=current_metrics.context
        )
        
        self.feedback_history.append(feedback_entry)
        self.strategy_improvements[most_used_strategy.name].append(overall_improvement)
    
    async def _detect_learning_patterns(self) -> None:
        """Detect patterns in performance improvements"""
        if len(self.feedback_history) < self.pattern_detection_window:
            return
        
        recent_feedback = list(self.feedback_history)[-self.pattern_detection_window:]
        
        # Pattern 1: Strategy effectiveness over time
        strategy_trends = defaultdict(list)
        for feedback in recent_feedback:
            strategy_trends[feedback.strategy_name].append(feedback.improvement)
        
        for strategy_name, improvements in strategy_trends.items():
            if len(improvements) >= 5:
                # Calculate trend
                x = np.arange(len(improvements))
                trend = np.polyfit(x, improvements, 1)[0]
                
                pattern_key = f"trend_{strategy_name}"
                self.learning_patterns[pattern_key] = {
                    "type": "effectiveness_trend",
                    "strategy": strategy_name,
                    "trend": trend,
                    "confidence": len(improvements) / self.pattern_detection_window,
                    "last_updated": time.time()
                }
        
        # Pattern 2: Context-specific performance
        context_performance = defaultdict(lambda: defaultdict(list))
        for feedback in recent_feedback:
            context_type = feedback.context.get("system_load", "unknown")
            context_performance[context_type][feedback.strategy_name].append(feedback.improvement)
        
        for context_type, strategy_perf in context_performance.items():
            for strategy_name, improvements in strategy_perf.items():
                if len(improvements) >= 3:
                    avg_improvement = np.mean(improvements)
                    pattern_key = f"context_{context_type}_{strategy_name}"
                    self.learning_patterns[pattern_key] = {
                        "type": "context_performance",
                        "context": context_type,
                        "strategy": strategy_name,
                        "avg_improvement": avg_improvement,
                        "sample_size": len(improvements),
                        "last_updated": time.time()
                    }
    
    async def _generate_adaptation_rules(self) -> None:
        """Generate adaptation rules based on learned patterns"""
        new_rules = []
        
        # Rule generation from effectiveness trends
        for pattern_key, pattern in self.learning_patterns.items():
            if pattern["type"] == "effectiveness_trend":
                strategy_name = pattern["strategy"]
                trend = pattern["trend"]
                confidence = pattern["confidence"]
                
                if trend > 0.01 and confidence > 0.3:
                    # Strategy is improving - increase its priority
                    rule = {
                        "type": "increase_priority",
                        "strategy": strategy_name,
                        "adjustment": min(trend * 10, 0.2),
                        "confidence": confidence,
                        "reason": f"Positive trend detected: {trend:.4f}"
                    }
                    new_rules.append(rule)
                
                elif trend < -0.01 and confidence > 0.3:
                    # Strategy is declining - decrease its priority
                    rule = {
                        "type": "decrease_priority",
                        "strategy": strategy_name,
                        "adjustment": max(trend * 10, -0.2),
                        "confidence": confidence,
                        "reason": f"Negative trend detected: {trend:.4f}"
                    }
                    new_rules.append(rule)
        
        # Rule generation from context performance
        context_rules = defaultdict(list)
        for pattern_key, pattern in self.learning_patterns.items():
            if pattern["type"] == "context_performance":
                context = pattern["context"]
                strategy = pattern["strategy"]
                avg_improvement = pattern["avg_improvement"]
                sample_size = pattern["sample_size"]
                
                if sample_size >= 3:
                    context_rules[context].append((strategy, avg_improvement))
        
        # Generate context-specific rules
        for context, strategy_performances in context_rules.items():
            if len(strategy_performances) > 1:
                # Sort by performance
                strategy_performances.sort(key=lambda x: x[1], reverse=True)
                best_strategy, best_perf = strategy_performances[0]
                
                if best_perf > 0.02:  # Significant improvement
                    rule = {
                        "type": "context_preference",
                        "context": context,
                        "preferred_strategy": best_strategy,
                        "performance_advantage": best_perf,
                        "confidence": min(len(strategy_performances) / 5, 1.0),
                        "reason": f"Best performer in {context} context"
                    }
                    new_rules.append(rule)
        
        # Add new rules with confidence filtering
        for rule in new_rules:
            if rule["confidence"] > 0.4:  # Only high-confidence rules
                self.adaptation_rules.append(rule)
        
        # Limit rule count to prevent over-adaptation
        if len(self.adaptation_rules) > 20:
            # Keep only the most confident rules
            self.adaptation_rules.sort(key=lambda r: r["confidence"], reverse=True)
            self.adaptation_rules = self.adaptation_rules[:20]
    
    async def _apply_learned_optimizations(self, active_strategies: Dict[str, 'OptimizationStrategy']) -> None:
        """Apply learned optimizations to active strategies"""
        
        for rule in self.adaptation_rules:
            strategy_name = rule.get("strategy")
            if not strategy_name or strategy_name not in active_strategies:
                continue
            
            strategy = active_strategies[strategy_name]
            
            if rule["type"] == "increase_priority":
                # Increase strategy effectiveness score
                adjustment = rule["adjustment"] * self.learning_rate
                strategy.effectiveness_score = min(strategy.effectiveness_score + adjustment, 1.0)
                
            elif rule["type"] == "decrease_priority":
                # Decrease strategy effectiveness score
                adjustment = abs(rule["adjustment"]) * self.learning_rate
                strategy.effectiveness_score = max(strategy.effectiveness_score - adjustment, 0.0)
                
            elif rule["type"] == "context_preference":
                # This would be handled by the strategy selector
                # Store preference for context-aware selection
                pass
    
    def add_user_feedback(self, strategy_name: str, rating: float, 
                         context: Dict[str, Any]) -> None:
        """Add explicit user feedback"""
        feedback_entry = FeedbackEntry(
            feedback_type=FeedbackType.USER,
            strategy_name=strategy_name,
            performance_before={},
            performance_after={},
            improvement=rating - 0.5,  # Convert 0-1 rating to improvement score
            timestamp=time.time(),
            context=context
        )
        
        self.feedback_history.append(feedback_entry)
        self.strategy_improvements[strategy_name].append(rating - 0.5)
    
    def add_system_feedback(self, strategy_name: str, performance_metrics: Dict[str, float],
                          improvement_score: float, context: Dict[str, Any]) -> None:
        """Add system-generated feedback"""
        feedback_entry = FeedbackEntry(
            feedback_type=FeedbackType.SYSTEM,
            strategy_name=strategy_name,
            performance_before={},
            performance_after=performance_metrics,
            improvement=improvement_score,
            timestamp=time.time(),
            context=context
        )
        
        self.feedback_history.append(feedback_entry)
        self.strategy_improvements[strategy_name].append(improvement_score)
    
    def get_strategy_learning_summary(self, strategy_name: str) -> Dict[str, Any]:
        """Get learning summary for a specific strategy"""
        improvements = self.strategy_improvements.get(strategy_name, [])
        
        if not improvements:
            return {"strategy": strategy_name, "no_data": True}
        
        recent_improvements = improvements[-20:]
        
        return {
            "strategy": strategy_name,
            "total_feedback_entries": len(improvements),
            "recent_avg_improvement": np.mean(recent_improvements),
            "improvement_trend": np.polyfit(range(len(recent_improvements)), recent_improvements, 1)[0] if len(recent_improvements) > 2 else 0,
            "best_improvement": max(improvements),
            "worst_improvement": min(improvements),
            "consistency": 1 - np.std(recent_improvements) if len(recent_improvements) > 1 else 0,
            "learning_patterns": [
                pattern for pattern_key, pattern in self.learning_patterns.items()
                if pattern.get("strategy") == strategy_name
            ]
        }
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get comprehensive feedback system summary"""
        return {
            "total_feedback_entries": len(self.feedback_history),
            "feedback_by_type": {
                feedback_type.value: len([f for f in self.feedback_history if f.feedback_type == feedback_type])
                for feedback_type in FeedbackType
            },
            "strategies_with_feedback": list(self.strategy_improvements.keys()),
            "learning_patterns_detected": len(self.learning_patterns),
            "active_adaptation_rules": len(self.adaptation_rules),
            "learning_rate": self.learning_rate,
            "last_analysis_time": self.last_analysis_time,
            "recent_patterns": [
                {
                    "type": pattern["type"],
                    "strategy": pattern.get("strategy", "N/A"),
                    "confidence": pattern.get("confidence", 0),
                    "last_updated": pattern["last_updated"]
                }
                for pattern in list(self.learning_patterns.values())[-5:]
            ]
        }