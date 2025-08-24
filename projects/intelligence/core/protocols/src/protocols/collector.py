"""
Metrics Collector - Real-time metric collection infrastructure
Multi-dimensional performance data collection
"""

import asyncio
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
from enum import Enum


class MetricType(Enum):
    """Types of metrics that can be collected"""
    ACCURACY = "accuracy"
    SPEED = "speed"
    QUALITY = "quality"
    COHERENCE = "coherence"
    EFFICIENCY = "efficiency"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class MetricPoint:
    """Individual metric data point"""
    metric_type: MetricType
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time series of metric points"""
    metric_type: MetricType
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Real-time metrics collection system"""
    
    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        self.metrics_buffer: Dict[str, MetricSeries] = {}
        self.collection_active = False
        self.collection_interval = 1.0
        
        # Collection callbacks
        self.metric_callbacks: Dict[MetricType, List[Callable]] = defaultdict(list)
        self.collection_hooks: List[Callable] = []
        
        # Threading for real-time collection
        self.collection_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Performance tracking
        self.collection_stats = {
            "total_points_collected": 0,
            "collection_errors": 0,
            "last_collection_time": 0.0,
            "collection_rate": 0.0
        }
    
    def start_collection(self) -> None:
        """Start real-time metrics collection"""
        if self.collection_active:
            return
        
        self.collection_active = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
    
    def stop_collection(self) -> None:
        """Stop metrics collection"""
        self.collection_active = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5.0)
    
    def _collection_loop(self) -> None:
        """Main collection loop running in separate thread"""
        last_collection = time.time()
        
        while self.collection_active:
            try:
                current_time = time.time()
                
                # Execute collection hooks
                for hook in self.collection_hooks:
                    try:
                        hook(current_time)
                    except Exception as e:
                        self.collection_stats["collection_errors"] += 1
                        print(f"Collection hook error: {e}")
                
                # Update collection rate
                time_delta = current_time - last_collection
                if time_delta > 0:
                    self.collection_stats["collection_rate"] = 1.0 / time_delta
                
                self.collection_stats["last_collection_time"] = current_time
                last_collection = current_time
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.collection_stats["collection_errors"] += 1
                print(f"Collection loop error: {e}")
                time.sleep(1.0)
    
    def collect_metric(self, metric_type: MetricType, value: float,
                      tags: Optional[Dict[str, str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Collect a single metric point"""
        if tags is None:
            tags = {}
        if metadata is None:
            metadata = {}
        
        metric_point = MetricPoint(
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            tags=tags,
            metadata=metadata
        )
        
        # Create series key from metric type and tags
        series_key = self._create_series_key(metric_type, tags)
        
        with self.lock:
            if series_key not in self.metrics_buffer:
                self.metrics_buffer[series_key] = MetricSeries(
                    metric_type=metric_type,
                    tags=tags
                )
            
            self.metrics_buffer[series_key].points.append(metric_point)
            self.collection_stats["total_points_collected"] += 1
        
        # Execute callbacks
        for callback in self.metric_callbacks[metric_type]:
            try:
                callback(metric_point)
            except Exception as e:
                print(f"Metric callback error: {e}")
    
    def collect_batch_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """Collect multiple metrics in batch"""
        for metric_data in metrics:
            try:
                metric_type = MetricType(metric_data["type"])
                value = float(metric_data["value"])
                tags = metric_data.get("tags", {})
                metadata = metric_data.get("metadata", {})
                
                self.collect_metric(metric_type, value, tags, metadata)
                
            except Exception as e:
                self.collection_stats["collection_errors"] += 1
                print(f"Batch metric collection error: {e}")
    
    def register_callback(self, metric_type: MetricType, callback: Callable) -> None:
        """Register callback for specific metric type"""
        self.metric_callbacks[metric_type].append(callback)
    
    def register_collection_hook(self, hook: Callable) -> None:
        """Register hook to be called during each collection cycle"""
        self.collection_hooks.append(hook)
    
    def get_metric_series(self, metric_type: MetricType,
                         tags: Optional[Dict[str, str]] = None) -> Optional[MetricSeries]:
        """Get metric series for specific type and tags"""
        if tags is None:
            tags = {}
        
        series_key = self._create_series_key(metric_type, tags)
        
        with self.lock:
            return self.metrics_buffer.get(series_key)
    
    def get_recent_metrics(self, metric_type: MetricType, 
                          count: int = 100,
                          tags: Optional[Dict[str, str]] = None) -> List[MetricPoint]:
        """Get recent metric points"""
        series = self.get_metric_series(metric_type, tags)
        if not series:
            return []
        
        with self.lock:
            return list(series.points)[-count:]
    
    def get_metric_statistics(self, metric_type: MetricType,
                            tags: Optional[Dict[str, str]] = None,
                            window_seconds: float = 300.0) -> Dict[str, float]:
        """Get statistical summary of metrics within time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        recent_points = self.get_recent_metrics(metric_type, 1000, tags)
        windowed_points = [
            p for p in recent_points 
            if p.timestamp >= cutoff_time
        ]
        
        if not windowed_points:
            return {}
        
        values = [p.value for p in windowed_points]
        
        return {
            "count": len(values),
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99),
            "rate": len(values) / window_seconds
        }
    
    def _create_series_key(self, metric_type: MetricType, tags: Dict[str, str]) -> str:
        """Create unique key for metric series"""
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_type.value}:{tag_str}"
    
    def clear_metrics(self, metric_type: Optional[MetricType] = None) -> None:
        """Clear collected metrics"""
        with self.lock:
            if metric_type is None:
                self.metrics_buffer.clear()
            else:
                keys_to_remove = [
                    key for key in self.metrics_buffer.keys()
                    if key.startswith(metric_type.value + ":")
                ]
                for key in keys_to_remove:
                    del self.metrics_buffer[key]
    
    def export_metrics(self, format_type: str = "json") -> Any:
        """Export collected metrics in specified format"""
        with self.lock:
            if format_type == "json":
                return {
                    "metrics": {
                        series_key: {
                            "metric_type": series.metric_type.value,
                            "tags": series.tags,
                            "points": [
                                {
                                    "value": point.value,
                                    "timestamp": point.timestamp,
                                    "tags": point.tags,
                                    "metadata": point.metadata
                                }
                                for point in series.points
                            ]
                        }
                        for series_key, series in self.metrics_buffer.items()
                    },
                    "stats": self.collection_stats
                }
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """Get comprehensive collection summary"""
        with self.lock:
            series_count = len(self.metrics_buffer)
            total_points = sum(len(series.points) for series in self.metrics_buffer.values())
            
            metric_type_counts = defaultdict(int)
            for series in self.metrics_buffer.values():
                metric_type_counts[series.metric_type.value] += len(series.points)
        
        return {
            "collection_active": self.collection_active,
            "total_series": series_count,
            "total_points": total_points,
            "points_by_type": dict(metric_type_counts),
            "collection_stats": self.collection_stats.copy(),
            "buffer_utilization": total_points / (series_count * self.buffer_size) if series_count > 0 else 0,
            "collection_interval": self.collection_interval,
            "registered_callbacks": {
                metric_type.value: len(callbacks)
                for metric_type, callbacks in self.metric_callbacks.items()
            },
            "collection_hooks": len(self.collection_hooks)
        }