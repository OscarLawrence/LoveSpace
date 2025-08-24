"""
Metrics Aggregator - Advanced metric aggregation and analysis
"""

import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from enum import Enum

from .collector import MetricType, MetricPoint, MetricSeries


class AggregationType(Enum):
    """Types of metric aggregations"""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    RATE = "rate"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std"
    VARIANCE = "variance"


@dataclass
class AggregationRule:
    """Rule for metric aggregation"""
    source_metric: MetricType
    aggregation_type: AggregationType
    time_window: float  # seconds
    output_metric: str
    tags_filter: Optional[Dict[str, str]] = None
    percentile_value: Optional[float] = None  # for percentile aggregation


class MetricsAggregator:
    """Advanced metrics aggregation and analysis engine"""
    
    def __init__(self):
        self.aggregation_rules: List[AggregationRule] = []
        self.aggregated_metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.custom_aggregators: Dict[str, Callable] = {}
        
        # Aggregation cache
        self.aggregation_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60.0  # Cache TTL in seconds
    
    def add_aggregation_rule(self, rule: AggregationRule) -> None:
        """Add a new aggregation rule"""
        self.aggregation_rules.append(rule)
    
    def register_custom_aggregator(self, name: str, aggregator_func: Callable) -> None:
        """Register a custom aggregation function"""
        self.custom_aggregators[name] = aggregator_func
    
    def aggregate_metrics(self, metrics_data: Dict[str, MetricSeries]) -> Dict[str, Any]:
        """Perform aggregation on collected metrics"""
        aggregation_results = {}
        current_time = time.time()
        
        for rule in self.aggregation_rules:
            try:
                result = self._apply_aggregation_rule(rule, metrics_data, current_time)
                if result is not None:
                    aggregation_results[rule.output_metric] = result
            except Exception as e:
                print(f"Error applying aggregation rule {rule.output_metric}: {e}")
        
        return aggregation_results
    
    def _apply_aggregation_rule(self, rule: AggregationRule, 
                              metrics_data: Dict[str, MetricSeries],
                              current_time: float) -> Optional[Dict[str, Any]]:
        """Apply a single aggregation rule"""
        # Find matching metric series
        matching_series = []
        for series_key, series in metrics_data.items():
            if series.metric_type != rule.source_metric:
                continue
            
            # Apply tags filter if specified
            if rule.tags_filter:
                if not all(series.tags.get(k) == v for k, v in rule.tags_filter.items()):
                    continue
            
            matching_series.append(series)
        
        if not matching_series:
            return None
        
        # Collect points within time window
        cutoff_time = current_time - rule.time_window
        all_points = []
        
        for series in matching_series:
            windowed_points = [
                point for point in series.points
                if point.timestamp >= cutoff_time
            ]
            all_points.extend(windowed_points)
        
        if not all_points:
            return None
        
        # Apply aggregation
        return self._calculate_aggregation(rule, all_points, current_time)
    
    def _calculate_aggregation(self, rule: AggregationRule, 
                             points: List[MetricPoint],
                             current_time: float) -> Dict[str, Any]:
        """Calculate aggregation value from points"""
        values = [point.value for point in points]
        
        if rule.aggregation_type == AggregationType.SUM:
            result_value = np.sum(values)
        elif rule.aggregation_type == AggregationType.AVERAGE:
            result_value = np.mean(values)
        elif rule.aggregation_type == AggregationType.MEDIAN:
            result_value = np.median(values)
        elif rule.aggregation_type == AggregationType.MIN:
            result_value = np.min(values)
        elif rule.aggregation_type == AggregationType.MAX:
            result_value = np.max(values)
        elif rule.aggregation_type == AggregationType.COUNT:
            result_value = len(values)
        elif rule.aggregation_type == AggregationType.RATE:
            result_value = len(values) / rule.time_window
        elif rule.aggregation_type == AggregationType.PERCENTILE:
            if rule.percentile_value is None:
                raise ValueError("Percentile value required for percentile aggregation")
            result_value = np.percentile(values, rule.percentile_value)
        elif rule.aggregation_type == AggregationType.STANDARD_DEVIATION:
            result_value = np.std(values)
        elif rule.aggregation_type == AggregationType.VARIANCE:
            result_value = np.var(values)
        else:
            raise ValueError(f"Unsupported aggregation type: {rule.aggregation_type}")
        
        return {
            "value": float(result_value),
            "timestamp": current_time,
            "source_metric": rule.source_metric.value,
            "aggregation_type": rule.aggregation_type.value,
            "time_window": rule.time_window,
            "sample_count": len(values),
            "tags_filter": rule.tags_filter or {}
        }
    
    def calculate_composite_metrics(self, metrics_data: Dict[str, MetricSeries]) -> Dict[str, Any]:
        """Calculate composite metrics from multiple sources"""
        composite_results = {}
        
        # Performance Score Composite
        performance_score = self._calculate_performance_score(metrics_data)
        if performance_score is not None:
            composite_results["performance_score"] = performance_score
        
        # Efficiency Ratio
        efficiency_ratio = self._calculate_efficiency_ratio(metrics_data)
        if efficiency_ratio is not None:
            composite_results["efficiency_ratio"] = efficiency_ratio
        
        # Quality Index
        quality_index = self._calculate_quality_index(metrics_data)
        if quality_index is not None:
            composite_results["quality_index"] = quality_index
        
        # Stability Score
        stability_score = self._calculate_stability_score(metrics_data)
        if stability_score is not None:
            composite_results["stability_score"] = stability_score
        
        return composite_results
    
    def _calculate_performance_score(self, metrics_data: Dict[str, MetricSeries]) -> Optional[Dict[str, Any]]:
        """Calculate overall performance score"""
        # Get recent values for key metrics
        accuracy_values = self._get_recent_values(metrics_data, MetricType.ACCURACY)
        speed_values = self._get_recent_values(metrics_data, MetricType.SPEED)
        quality_values = self._get_recent_values(metrics_data, MetricType.QUALITY)
        
        if not all([accuracy_values, speed_values, quality_values]):
            return None
        
        # Normalize and weight metrics
        accuracy_score = np.mean(accuracy_values) * 0.4
        speed_score = min(np.mean(speed_values) / 100.0, 1.0) * 0.3  # Normalize speed
        quality_score = np.mean(quality_values) * 0.3
        
        performance_score = accuracy_score + speed_score + quality_score
        
        return {
            "value": performance_score,
            "timestamp": time.time(),
            "components": {
                "accuracy": accuracy_score,
                "speed": speed_score,
                "quality": quality_score
            },
            "sample_sizes": {
                "accuracy": len(accuracy_values),
                "speed": len(speed_values),
                "quality": len(quality_values)
            }
        }
    
    def _calculate_efficiency_ratio(self, metrics_data: Dict[str, MetricSeries]) -> Optional[Dict[str, Any]]:
        """Calculate efficiency ratio (output/resource usage)"""
        throughput_values = self._get_recent_values(metrics_data, MetricType.THROUGHPUT)
        resource_values = self._get_recent_values(metrics_data, MetricType.RESOURCE_USAGE)
        
        if not throughput_values or not resource_values:
            return None
        
        avg_throughput = np.mean(throughput_values)
        avg_resource_usage = np.mean(resource_values)
        
        if avg_resource_usage == 0:
            return None
        
        efficiency_ratio = avg_throughput / avg_resource_usage
        
        return {
            "value": efficiency_ratio,
            "timestamp": time.time(),
            "avg_throughput": avg_throughput,
            "avg_resource_usage": avg_resource_usage,
            "sample_count": min(len(throughput_values), len(resource_values))
        }
    
    def _calculate_quality_index(self, metrics_data: Dict[str, MetricSeries]) -> Optional[Dict[str, Any]]:
        """Calculate quality index from multiple quality metrics"""
        quality_values = self._get_recent_values(metrics_data, MetricType.QUALITY)
        coherence_values = self._get_recent_values(metrics_data, MetricType.COHERENCE)
        error_rate_values = self._get_recent_values(metrics_data, MetricType.ERROR_RATE)
        
        if not quality_values:
            return None
        
        # Base quality score
        quality_score = np.mean(quality_values)
        
        # Adjust for coherence if available
        if coherence_values:
            coherence_score = np.mean(coherence_values)
            quality_score = (quality_score * 0.7) + (coherence_score * 0.3)
        
        # Penalize for errors if available
        if error_rate_values:
            error_penalty = np.mean(error_rate_values)
            quality_score = quality_score * (1 - error_penalty)
        
        return {
            "value": quality_score,
            "timestamp": time.time(),
            "base_quality": np.mean(quality_values),
            "coherence_adjustment": np.mean(coherence_values) if coherence_values else None,
            "error_penalty": np.mean(error_rate_values) if error_rate_values else None
        }
    
    def _calculate_stability_score(self, metrics_data: Dict[str, MetricSeries]) -> Optional[Dict[str, Any]]:
        """Calculate stability score based on metric variance"""
        stability_metrics = {}
        
        for metric_type in [MetricType.ACCURACY, MetricType.SPEED, MetricType.QUALITY]:
            values = self._get_recent_values(metrics_data, metric_type)
            if values and len(values) > 1:
                # Lower variance = higher stability
                variance = np.var(values)
                mean_value = np.mean(values)
                
                # Coefficient of variation (normalized variance)
                cv = variance / mean_value if mean_value != 0 else float('inf')
                stability = max(0, 1 - cv)  # Convert to stability score
                
                stability_metrics[metric_type.value] = {
                    "stability": stability,
                    "variance": variance,
                    "coefficient_of_variation": cv
                }
        
        if not stability_metrics:
            return None
        
        # Overall stability is average of individual stabilities
        overall_stability = np.mean([m["stability"] for m in stability_metrics.values()])
        
        return {
            "value": overall_stability,
            "timestamp": time.time(),
            "metric_stabilities": stability_metrics
        }
    
    def _get_recent_values(self, metrics_data: Dict[str, MetricSeries], 
                          metric_type: MetricType, window_seconds: float = 300.0) -> List[float]:
        """Get recent values for a specific metric type"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        values = []
        for series in metrics_data.values():
            if series.metric_type == metric_type:
                recent_points = [
                    point for point in series.points
                    if point.timestamp >= cutoff_time
                ]
                values.extend([point.value for point in recent_points])
        
        return values
    
    def get_aggregation_summary(self) -> Dict[str, Any]:
        """Get comprehensive aggregation summary"""
        return {
            "total_rules": len(self.aggregation_rules),
            "custom_aggregators": list(self.custom_aggregators.keys()),
            "cache_entries": len(self.aggregation_cache),
            "cache_ttl": self.cache_ttl,
            "rules_by_type": {
                agg_type.value: len([
                    rule for rule in self.aggregation_rules
                    if rule.aggregation_type == agg_type
                ])
                for agg_type in AggregationType
            }
        }