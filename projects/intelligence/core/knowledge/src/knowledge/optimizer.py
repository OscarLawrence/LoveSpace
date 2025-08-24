"""
Core AI Performance Optimizer
Multi-dimensional performance monitoring and optimization
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque

from .performance_monitor import PerformanceMonitor
from .strategy_selector import StrategySelector
from .feedback_loop import FeedbackLoop


class OptimizationMode(Enum):
    """Optimization modes for different scenarios"""
    ACCURACY = "accuracy"
    SPEED = "speed"
    QUALITY = "quality"
    BALANCED = "balanced"
    ADAPTIVE = "adaptive"


@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    accuracy: float = 0.0
    speed: float = 0.0  # operations per second
    quality: float = 0.0
    coherence: float = 0.0
    efficiency: float = 0.0
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationStrategy:
    """Strategy configuration for optimization"""
    name: str
    parameters: Dict[str, Any]
    priority_weights: Dict[str, float]
    adaptation_rate: float = 0.1
    effectiveness_score: float = 0.0
    usage_count: int = 0


class AIOptimizer:
    """
    Core AI Performance Optimization System
    Provides multi-dimensional performance monitoring and real-time optimization
    """
    
    def __init__(self, mode: OptimizationMode = OptimizationMode.ADAPTIVE):
        self.mode = mode
        self.performance_monitor = PerformanceMonitor()
        self.strategy_selector = StrategySelector()
        self.feedback_loop = FeedbackLoop()
        
        # Performance tracking
        self.metrics_history: deque = deque(maxlen=1000)
        self.current_metrics = PerformanceMetrics()
        self.baseline_metrics: Optional[PerformanceMetrics] = None
        
        # Strategy management
        self.active_strategies: Dict[str, OptimizationStrategy] = {}
        self.strategy_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Optimization state
        self.optimization_active = False
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.05
        self.performance_targets = {
            "accuracy": 0.95,
            "speed": 100.0,
            "quality": 0.90,
            "coherence": 0.85,
            "efficiency": 0.80
        }
        
        # Initialize default strategies
        self._initialize_strategies()
    
    def _initialize_strategies(self) -> None:
        """Initialize default optimization strategies"""
        strategies = [
            OptimizationStrategy(
                name="high_accuracy",
                parameters={"temperature": 0.1, "top_p": 0.8, "max_tokens": 2048},
                priority_weights={"accuracy": 0.4, "quality": 0.3, "coherence": 0.3}
            ),
            OptimizationStrategy(
                name="high_speed",
                parameters={"temperature": 0.3, "top_p": 0.9, "max_tokens": 1024},
                priority_weights={"speed": 0.5, "efficiency": 0.3, "accuracy": 0.2}
            ),
            OptimizationStrategy(
                name="balanced",
                parameters={"temperature": 0.2, "top_p": 0.85, "max_tokens": 1536},
                priority_weights={"accuracy": 0.25, "speed": 0.25, "quality": 0.25, "efficiency": 0.25}
            ),
            OptimizationStrategy(
                name="quality_focused",
                parameters={"temperature": 0.15, "top_p": 0.75, "max_tokens": 2560},
                priority_weights={"quality": 0.4, "coherence": 0.3, "accuracy": 0.3}
            )
        ]
        
        for strategy in strategies:
            self.active_strategies[strategy.name] = strategy
    
    async def start_optimization(self) -> None:
        """Start the optimization system"""
        self.optimization_active = True
        await asyncio.gather(
            self._optimization_loop(),
            self._monitoring_loop(),
            self._adaptation_loop()
        )
    
    async def stop_optimization(self) -> None:
        """Stop the optimization system"""
        self.optimization_active = False
    
    async def _optimization_loop(self) -> None:
        """Main optimization loop"""
        while self.optimization_active:
            try:
                # Collect current performance metrics
                current_metrics = await self.performance_monitor.collect_metrics()
                self.current_metrics = current_metrics
                self.metrics_history.append(current_metrics)
                
                # Determine if optimization is needed
                if self._needs_optimization(current_metrics):
                    # Select optimal strategy
                    strategy = await self.strategy_selector.select_strategy(
                        current_metrics, self.active_strategies, self.mode
                    )
                    
                    # Apply optimization
                    await self._apply_optimization(strategy, current_metrics)
                
                await asyncio.sleep(1.0)  # Optimization cycle interval
                
            except Exception as e:
                print(f"Optimization loop error: {e}")
                await asyncio.sleep(5.0)
    
    async def _monitoring_loop(self) -> None:
        """Performance monitoring loop"""
        while self.optimization_active:
            try:
                # Update performance baselines
                if len(self.metrics_history) >= 10:
                    self._update_baseline()
                
                # Detect performance drift
                drift_detected = self._detect_performance_drift()
                if drift_detected:
                    await self._handle_performance_drift()
                
                await asyncio.sleep(5.0)  # Monitoring interval
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                await asyncio.sleep(10.0)
    
    async def _adaptation_loop(self) -> None:
        """Strategy adaptation loop"""
        while self.optimization_active:
            try:
                # Update strategy effectiveness scores
                self._update_strategy_effectiveness()
                
                # Adapt strategies based on performance
                await self._adapt_strategies()
                
                # Learn from feedback
                await self.feedback_loop.process_feedback(
                    self.metrics_history, self.active_strategies
                )
                
                await asyncio.sleep(10.0)  # Adaptation interval
                
            except Exception as e:
                print(f"Adaptation loop error: {e}")
                await asyncio.sleep(15.0)
    
    def _needs_optimization(self, metrics: PerformanceMetrics) -> bool:
        """Determine if optimization is needed based on current metrics"""
        if not self.baseline_metrics:
            return True
        
        # Check if any metric is below target
        for metric_name, target in self.performance_targets.items():
            current_value = getattr(metrics, metric_name, 0.0)
            if current_value < target:
                return True
        
        # Check for significant performance degradation
        accuracy_drop = self.baseline_metrics.accuracy - metrics.accuracy
        speed_drop = self.baseline_metrics.speed - metrics.speed
        quality_drop = self.baseline_metrics.quality - metrics.quality
        
        return (accuracy_drop > self.adaptation_threshold or 
                speed_drop > self.adaptation_threshold or
                quality_drop > self.adaptation_threshold)
    
    async def _apply_optimization(self, strategy: OptimizationStrategy, 
                                metrics: PerformanceMetrics) -> None:
        """Apply selected optimization strategy"""
        try:
            # Record strategy usage
            strategy.usage_count += 1
            
            # Apply strategy parameters
            optimization_params = self._calculate_optimization_params(strategy, metrics)
            
            # Notify system of optimization changes
            await self._broadcast_optimization_update(strategy, optimization_params)
            
            # Track strategy application
            self.strategy_performance[strategy.name].append(
                self._calculate_strategy_score(metrics, strategy)
            )
            
        except Exception as e:
            print(f"Error applying optimization: {e}")
    
    def _calculate_optimization_params(self, strategy: OptimizationStrategy, 
                                     metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Calculate specific optimization parameters"""
        params = strategy.parameters.copy()
        
        # Adaptive parameter adjustment based on current performance
        if metrics.accuracy < self.performance_targets["accuracy"]:
            params["temperature"] *= 0.9  # Lower temperature for higher accuracy
            params["top_p"] *= 0.95
        
        if metrics.speed < self.performance_targets["speed"]:
            params["max_tokens"] = min(params.get("max_tokens", 1024), 1024)
            params["temperature"] *= 1.1  # Higher temperature for speed
        
        if metrics.quality < self.performance_targets["quality"]:
            params["max_tokens"] = max(params.get("max_tokens", 1536), 1536)
            params["temperature"] *= 0.95
        
        return params
    
    async def _broadcast_optimization_update(self, strategy: OptimizationStrategy,
                                           params: Dict[str, Any]) -> None:
        """Broadcast optimization updates to connected systems"""
        update = {
            "strategy": strategy.name,
            "parameters": params,
            "timestamp": time.time(),
            "mode": self.mode.value
        }
        
        # This would integrate with the protocols system for distribution
        # await self.protocol_manager.broadcast_optimization_update(update)
        pass
    
    def _update_baseline(self) -> None:
        """Update performance baseline from recent metrics"""
        if len(self.metrics_history) < 10:
            return
        
        recent_metrics = list(self.metrics_history)[-10:]
        
        # Calculate rolling averages
        avg_accuracy = np.mean([m.accuracy for m in recent_metrics])
        avg_speed = np.mean([m.speed for m in recent_metrics])
        avg_quality = np.mean([m.quality for m in recent_metrics])
        avg_coherence = np.mean([m.coherence for m in recent_metrics])
        avg_efficiency = np.mean([m.efficiency for m in recent_metrics])
        
        self.baseline_metrics = PerformanceMetrics(
            accuracy=avg_accuracy,
            speed=avg_speed,
            quality=avg_quality,
            coherence=avg_coherence,
            efficiency=avg_efficiency
        )
    
    def _detect_performance_drift(self) -> bool:
        """Detect significant performance drift"""
        if not self.baseline_metrics or len(self.metrics_history) < 5:
            return False
        
        recent_metrics = list(self.metrics_history)[-5:]
        
        # Calculate recent averages
        recent_accuracy = np.mean([m.accuracy for m in recent_metrics])
        recent_speed = np.mean([m.speed for m in recent_metrics])
        recent_quality = np.mean([m.quality for m in recent_metrics])
        
        # Check for significant drift
        accuracy_drift = abs(self.baseline_metrics.accuracy - recent_accuracy)
        speed_drift = abs(self.baseline_metrics.speed - recent_speed)
        quality_drift = abs(self.baseline_metrics.quality - recent_quality)
        
        drift_threshold = 0.1
        return (accuracy_drift > drift_threshold or 
                speed_drift > drift_threshold or
                quality_drift > drift_threshold)
    
    async def _handle_performance_drift(self) -> None:
        """Handle detected performance drift"""
        print("Performance drift detected - triggering adaptive optimization")
        
        # Force strategy re-evaluation
        await self._adapt_strategies()
        
        # Update learning rate
        self.learning_rate = min(self.learning_rate * 1.2, 0.3)
    
    def _update_strategy_effectiveness(self) -> None:
        """Update effectiveness scores for all strategies"""
        for strategy_name, strategy in self.active_strategies.items():
            if strategy_name in self.strategy_performance:
                scores = self.strategy_performance[strategy_name]
                if scores:
                    # Calculate weighted average with recent bias
                    weights = np.exp(np.linspace(-1, 0, len(scores)))
                    strategy.effectiveness_score = np.average(scores, weights=weights)
    
    async def _adapt_strategies(self) -> None:
        """Adapt strategies based on performance feedback"""
        if not self.baseline_metrics:
            return
        
        for strategy in self.active_strategies.values():
            # Adapt parameters based on effectiveness
            if strategy.effectiveness_score < 0.7:  # Poor performance
                # Reduce temperature for better accuracy
                strategy.parameters["temperature"] *= 0.95
                strategy.parameters["top_p"] *= 0.98
            elif strategy.effectiveness_score > 0.9:  # Excellent performance
                # Slightly increase efficiency
                strategy.parameters["temperature"] *= 1.02
                strategy.parameters["max_tokens"] = max(
                    strategy.parameters.get("max_tokens", 1024) * 0.98, 512
                )
    
    def _calculate_strategy_score(self, metrics: PerformanceMetrics, 
                                strategy: OptimizationStrategy) -> float:
        """Calculate performance score for a strategy"""
        score = 0.0
        total_weight = 0.0
        
        for metric_name, weight in strategy.priority_weights.items():
            metric_value = getattr(metrics, metric_name, 0.0)
            target_value = self.performance_targets.get(metric_name, 1.0)
            
            # Normalize score (0-1 range)
            normalized_score = min(metric_value / target_value, 1.0)
            score += normalized_score * weight
            total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "current_metrics": {
                "accuracy": self.current_metrics.accuracy,
                "speed": self.current_metrics.speed,
                "quality": self.current_metrics.quality,
                "coherence": self.current_metrics.coherence,
                "efficiency": self.current_metrics.efficiency
            },
            "baseline_metrics": {
                "accuracy": self.baseline_metrics.accuracy if self.baseline_metrics else 0,
                "speed": self.baseline_metrics.speed if self.baseline_metrics else 0,
                "quality": self.baseline_metrics.quality if self.baseline_metrics else 0,
                "coherence": self.baseline_metrics.coherence if self.baseline_metrics else 0,
                "efficiency": self.baseline_metrics.efficiency if self.baseline_metrics else 0
            } if self.baseline_metrics else None,
            "active_strategies": {
                name: {
                    "effectiveness_score": strategy.effectiveness_score,
                    "usage_count": strategy.usage_count,
                    "parameters": strategy.parameters
                }
                for name, strategy in self.active_strategies.items()
            },
            "optimization_mode": self.mode.value,
            "optimization_active": self.optimization_active,
            "metrics_history_length": len(self.metrics_history)
        }