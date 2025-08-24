"""
Performance Monitor - Real-time performance measurement
Collects multi-dimensional metrics for AI optimization
"""

import asyncio
import time
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from collections import deque


@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    disk_io: float
    network_io: float
    timestamp: float


class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self):
        self.metrics_buffer: deque = deque(maxlen=100)
        self.system_metrics: deque = deque(maxlen=50)
        self.monitoring_active = False
        
        # Performance tracking
        self.task_start_times: Dict[str, float] = {}
        self.task_durations: Dict[str, List[float]] = {}
        self.accuracy_scores: List[float] = []
        self.quality_scores: List[float] = []
        
        # Baseline measurements
        self.baseline_cpu = 0.0
        self.baseline_memory = 0.0
        self.baseline_response_time = 0.0
    
    async def start_monitoring(self) -> None:
        """Start performance monitoring"""
        self.monitoring_active = True
        await asyncio.gather(
            self._system_monitoring_loop(),
            self._performance_calculation_loop()
        )
    
    async def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self.monitoring_active = False
    
    async def _system_monitoring_loop(self) -> None:
        """Monitor system resource usage"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_io=disk_io.read_bytes + disk_io.write_bytes if disk_io else 0,
                    network_io=network_io.bytes_sent + network_io.bytes_recv if network_io else 0,
                    timestamp=time.time()
                )
                
                self.system_metrics.append(metrics)
                await asyncio.sleep(2.0)
                
            except Exception as e:
                print(f"System monitoring error: {e}")
                await asyncio.sleep(5.0)
    
    async def _performance_calculation_loop(self) -> None:
        """Calculate performance metrics"""
        while self.monitoring_active:
            try:
                # Update baseline measurements
                self._update_baselines()
                
                await asyncio.sleep(5.0)
                
            except Exception as e:
                print(f"Performance calculation error: {e}")
                await asyncio.sleep(10.0)
    
    def start_task(self, task_id: str) -> None:
        """Start timing a task"""
        self.task_start_times[task_id] = time.time()
    
    def end_task(self, task_id: str, accuracy: Optional[float] = None,
                quality: Optional[float] = None) -> float:
        """End timing a task and record metrics"""
        if task_id not in self.task_start_times:
            return 0.0
        
        duration = time.time() - self.task_start_times[task_id]
        
        # Record task duration
        if task_id not in self.task_durations:
            self.task_durations[task_id] = []
        self.task_durations[task_id].append(duration)
        
        # Record quality metrics
        if accuracy is not None:
            self.accuracy_scores.append(accuracy)
        if quality is not None:
            self.quality_scores.append(quality)
        
        # Clean up
        del self.task_start_times[task_id]
        
        return duration
    
    async def collect_metrics(self) -> 'PerformanceMetrics':
        """Collect comprehensive performance metrics"""
        from .optimizer import PerformanceMetrics
        
        # Calculate speed metrics
        speed = self._calculate_speed_metric()
        
        # Calculate accuracy metrics
        accuracy = self._calculate_accuracy_metric()
        
        # Calculate quality metrics
        quality = self._calculate_quality_metric()
        
        # Calculate coherence metrics
        coherence = self._calculate_coherence_metric()
        
        # Calculate efficiency metrics
        efficiency = self._calculate_efficiency_metric()
        
        return PerformanceMetrics(
            accuracy=accuracy,
            speed=speed,
            quality=quality,
            coherence=coherence,
            efficiency=efficiency,
            timestamp=time.time(),
            context=self._get_context_info()
        )
    
    def _calculate_speed_metric(self) -> float:
        """Calculate speed performance metric"""
        if not self.task_durations:
            return 0.0
        
        # Calculate average task completion rate
        all_durations = []
        for durations in self.task_durations.values():
            all_durations.extend(durations[-10:])  # Last 10 tasks
        
        if not all_durations:
            return 0.0
        
        avg_duration = np.mean(all_durations)
        
        # Convert to operations per second (normalized)
        if avg_duration > 0:
            ops_per_second = 1.0 / avg_duration
            # Normalize to 0-100 scale (assuming 1 op/sec = 100 points)
            return min(ops_per_second * 100, 1000.0)
        
        return 0.0
    
    def _calculate_accuracy_metric(self) -> float:
        """Calculate accuracy performance metric"""
        if not self.accuracy_scores:
            return 0.0
        
        # Use recent accuracy scores with exponential weighting
        recent_scores = self.accuracy_scores[-20:]
        if not recent_scores:
            return 0.0
        
        weights = np.exp(np.linspace(-1, 0, len(recent_scores)))
        return float(np.average(recent_scores, weights=weights))
    
    def _calculate_quality_metric(self) -> float:
        """Calculate quality performance metric"""
        if not self.quality_scores:
            return 0.0
        
        # Use recent quality scores with exponential weighting
        recent_scores = self.quality_scores[-20:]
        if not recent_scores:
            return 0.0
        
        weights = np.exp(np.linspace(-1, 0, len(recent_scores)))
        return float(np.average(recent_scores, weights=weights))
    
    def _calculate_coherence_metric(self) -> float:
        """Calculate coherence performance metric"""
        # Coherence based on consistency of performance
        if len(self.accuracy_scores) < 5:
            return 0.0
        
        recent_accuracy = self.accuracy_scores[-10:]
        recent_quality = self.quality_scores[-10:] if self.quality_scores else [0.5] * 10
        
        # Calculate variance (lower variance = higher coherence)
        accuracy_variance = np.var(recent_accuracy) if recent_accuracy else 1.0
        quality_variance = np.var(recent_quality) if recent_quality else 1.0
        
        # Convert variance to coherence score (0-1)
        accuracy_coherence = max(0, 1 - accuracy_variance)
        quality_coherence = max(0, 1 - quality_variance)
        
        return (accuracy_coherence + quality_coherence) / 2
    
    def _calculate_efficiency_metric(self) -> float:
        """Calculate efficiency performance metric"""
        if not self.system_metrics:
            return 0.0
        
        # Get recent system metrics
        recent_metrics = list(self.system_metrics)[-10:]
        
        # Calculate resource efficiency
        avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
        avg_memory = np.mean([m.memory_percent for m in recent_metrics])
        
        # Efficiency is inverse of resource usage (normalized)
        cpu_efficiency = max(0, (100 - avg_cpu) / 100)
        memory_efficiency = max(0, (100 - avg_memory) / 100)
        
        # Combine with task completion efficiency
        task_efficiency = self._calculate_task_efficiency()
        
        return (cpu_efficiency + memory_efficiency + task_efficiency) / 3
    
    def _calculate_task_efficiency(self) -> float:
        """Calculate task completion efficiency"""
        if not self.task_durations:
            return 0.0
        
        # Compare current performance to baseline
        current_avg_duration = self._get_current_avg_duration()
        
        if self.baseline_response_time > 0 and current_avg_duration > 0:
            efficiency = self.baseline_response_time / current_avg_duration
            return min(efficiency, 2.0) / 2.0  # Normalize to 0-1
        
        return 0.5  # Default efficiency
    
    def _get_current_avg_duration(self) -> float:
        """Get current average task duration"""
        all_recent_durations = []
        for durations in self.task_durations.values():
            all_recent_durations.extend(durations[-5:])
        
        return np.mean(all_recent_durations) if all_recent_durations else 0.0
    
    def _update_baselines(self) -> None:
        """Update baseline performance measurements"""
        if self.system_metrics:
            recent_metrics = list(self.system_metrics)[-20:]
            self.baseline_cpu = np.mean([m.cpu_percent for m in recent_metrics])
            self.baseline_memory = np.mean([m.memory_percent for m in recent_metrics])
        
        if self.task_durations:
            all_durations = []
            for durations in self.task_durations.values():
                all_durations.extend(durations)
            
            if all_durations:
                self.baseline_response_time = np.mean(all_durations)
    
    def _get_context_info(self) -> Dict[str, Any]:
        """Get current context information"""
        context = {
            "active_tasks": len(self.task_start_times),
            "total_completed_tasks": sum(len(durations) for durations in self.task_durations.values()),
            "system_load": "normal"
        }
        
        # Determine system load
        if self.system_metrics:
            recent_cpu = np.mean([m.cpu_percent for m in list(self.system_metrics)[-5:]])
            recent_memory = np.mean([m.memory_percent for m in list(self.system_metrics)[-5:]])
            
            if recent_cpu > 80 or recent_memory > 85:
                context["system_load"] = "high"
            elif recent_cpu > 60 or recent_memory > 70:
                context["system_load"] = "medium"
        
        return context
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        return {
            "monitoring_active": self.monitoring_active,
            "metrics_collected": len(self.metrics_buffer),
            "system_metrics_collected": len(self.system_metrics),
            "active_tasks": len(self.task_start_times),
            "completed_tasks": {
                task_id: len(durations) 
                for task_id, durations in self.task_durations.items()
            },
            "baseline_metrics": {
                "cpu": self.baseline_cpu,
                "memory": self.baseline_memory,
                "response_time": self.baseline_response_time
            },
            "recent_performance": {
                "avg_accuracy": np.mean(self.accuracy_scores[-10:]) if self.accuracy_scores else 0,
                "avg_quality": np.mean(self.quality_scores[-10:]) if self.quality_scores else 0,
                "avg_duration": self._get_current_avg_duration()
            }
        }