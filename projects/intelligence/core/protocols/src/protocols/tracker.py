"""
Performance Tracker - Historical performance tracking and baseline management
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import numpy as np
from pathlib import Path

from .collector import MetricType, MetricPoint


@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison"""
    metric_type: MetricType
    baseline_value: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    created_at: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceDrift:
    """Detected performance drift"""
    metric_type: MetricType
    baseline_value: float
    current_value: float
    drift_magnitude: float
    drift_direction: str  # "positive", "negative"
    detected_at: float
    confidence: float


class PerformanceTracker:
    """Historical performance tracking and drift detection"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("performance_data")
        self.storage_path.mkdir(exist_ok=True)
        
        # Performance history
        self.performance_history: Dict[str, deque] = {}
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.drift_history: List[PerformanceDrift] = []
        
        # Tracking configuration
        self.history_retention_days = 30
        self.baseline_update_interval = 3600  # 1 hour
        self.drift_threshold = 0.1  # 10% change
        self.min_baseline_samples = 100
        
        # Load existing data
        self._load_historical_data()
    
    def track_performance(self, metric_point: MetricPoint) -> None:
        """Track a performance metric point"""
        series_key = self._create_series_key(metric_point.metric_type, metric_point.tags)
        
        # Initialize history if needed
        if series_key not in self.performance_history:
            self.performance_history[series_key] = deque(maxlen=10000)
        
        # Add to history
        self.performance_history[series_key].append(metric_point)
        
        # Check for drift
        drift = self._detect_drift(metric_point, series_key)
        if drift:
            self.drift_history.append(drift)
        
        # Update baseline if needed
        self._update_baseline_if_needed(series_key)
    
    def establish_baseline(self, metric_type: MetricType, 
                          tags: Optional[Dict[str, str]] = None,
                          force_update: bool = False) -> Optional[PerformanceBaseline]:
        """Establish performance baseline from historical data"""
        if tags is None:
            tags = {}
        
        series_key = self._create_series_key(metric_type, tags)
        
        # Check if baseline already exists and is recent
        if not force_update and series_key in self.baselines:
            baseline = self.baselines[series_key]
            if time.time() - baseline.created_at < self.baseline_update_interval:
                return baseline
        
        # Get historical data
        if series_key not in self.performance_history:
            return None
        
        history = list(self.performance_history[series_key])
        if len(history) < self.min_baseline_samples:
            return None
        
        # Use recent stable period for baseline
        recent_history = history[-self.min_baseline_samples:]
        values = [point.value for point in recent_history]
        
        # Calculate baseline statistics
        baseline_value = np.median(values)  # Use median for robustness
        std_dev = np.std(values)
        confidence_interval = (
            baseline_value - 1.96 * std_dev,
            baseline_value + 1.96 * std_dev
        )
        
        baseline = PerformanceBaseline(
            metric_type=metric_type,
            baseline_value=baseline_value,
            confidence_interval=confidence_interval,
            sample_size=len(values),
            created_at=time.time(),
            tags=tags
        )
        
        self.baselines[series_key] = baseline
        self._save_baseline(baseline, series_key)
        
        return baseline
    
    def _detect_drift(self, metric_point: MetricPoint, series_key: str) -> Optional[PerformanceDrift]:
        """Detect performance drift from baseline"""
        if series_key not in self.baselines:
            return None
        
        baseline = self.baselines[series_key]
        current_value = metric_point.value
        baseline_value = baseline.baseline_value
        
        # Calculate drift magnitude
        if baseline_value == 0:
            return None
        
        drift_magnitude = abs(current_value - baseline_value) / abs(baseline_value)
        
        # Check if drift exceeds threshold
        if drift_magnitude < self.drift_threshold:
            return None
        
        # Determine drift direction
        drift_direction = "positive" if current_value > baseline_value else "negative"
        
        # Calculate confidence based on how far outside confidence interval
        ci_lower, ci_upper = baseline.confidence_interval
        if current_value < ci_lower:
            confidence = min((ci_lower - current_value) / (ci_lower - baseline_value), 1.0)
        elif current_value > ci_upper:
            confidence = min((current_value - ci_upper) / (baseline_value - ci_upper), 1.0)
        else:
            confidence = 0.0
        
        return PerformanceDrift(
            metric_type=metric_point.metric_type,
            baseline_value=baseline_value,
            current_value=current_value,
            drift_magnitude=drift_magnitude,
            drift_direction=drift_direction,
            detected_at=metric_point.timestamp,
            confidence=confidence
        )
    
    def _update_baseline_if_needed(self, series_key: str) -> None:
        """Update baseline if enough time has passed"""
        if series_key not in self.baselines:
            return
        
        baseline = self.baselines[series_key]
        if time.time() - baseline.created_at > self.baseline_update_interval:
            # Extract metric type and tags from series key
            metric_type_str = series_key.split(':')[0]
            metric_type = MetricType(metric_type_str)
            
            # Parse tags from series key
            tag_str = series_key.split(':', 1)[1] if ':' in series_key else ""
            tags = {}
            if tag_str:
                for tag_pair in tag_str.split(','):
                    if '=' in tag_pair:
                        k, v = tag_pair.split('=', 1)
                        tags[k] = v
            
            self.establish_baseline(metric_type, tags, force_update=True)
    
    def get_performance_trend(self, metric_type: MetricType,
                            tags: Optional[Dict[str, str]] = None,
                            window_hours: float = 24.0) -> Dict[str, Any]:
        """Get performance trend analysis"""
        if tags is None:
            tags = {}
        
        series_key = self._create_series_key(metric_type, tags)
        
        if series_key not in self.performance_history:
            return {"error": "No historical data available"}
        
        # Get data within time window
        current_time = time.time()
        cutoff_time = current_time - (window_hours * 3600)
        
        history = list(self.performance_history[series_key])
        windowed_data = [
            point for point in history
            if point.timestamp >= cutoff_time
        ]
        
        if len(windowed_data) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate trend
        timestamps = [point.timestamp for point in windowed_data]
        values = [point.value for point in windowed_data]
        
        # Normalize timestamps for trend calculation
        time_normalized = np.array(timestamps) - timestamps[0]
        trend_slope, trend_intercept = np.polyfit(time_normalized, values, 1)
        
        # Calculate trend strength (R²)
        predicted_values = trend_slope * time_normalized + trend_intercept
        ss_res = np.sum((values - predicted_values) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            "metric_type": metric_type.value,
            "tags": tags,
            "window_hours": window_hours,
            "data_points": len(windowed_data),
            "trend_slope": trend_slope,
            "trend_direction": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
            "trend_strength": r_squared,
            "current_value": values[-1],
            "average_value": np.mean(values),
            "value_range": (np.min(values), np.max(values)),
            "volatility": np.std(values)
        }
    
    def get_drift_summary(self, hours_back: float = 24.0) -> Dict[str, Any]:
        """Get summary of detected performance drifts"""
        current_time = time.time()
        cutoff_time = current_time - (hours_back * 3600)
        
        recent_drifts = [
            drift for drift in self.drift_history
            if drift.detected_at >= cutoff_time
        ]
        
        if not recent_drifts:
            return {"total_drifts": 0, "hours_back": hours_back}
        
        # Analyze drifts by metric type
        drifts_by_metric = {}
        for drift in recent_drifts:
            metric_key = drift.metric_type.value
            if metric_key not in drifts_by_metric:
                drifts_by_metric[metric_key] = []
            drifts_by_metric[metric_key].append(drift)
        
        # Calculate drift statistics
        drift_stats = {}
        for metric_key, drifts in drifts_by_metric.items():
            magnitudes = [d.drift_magnitude for d in drifts]
            confidences = [d.confidence for d in drifts]
            
            drift_stats[metric_key] = {
                "count": len(drifts),
                "avg_magnitude": np.mean(magnitudes),
                "max_magnitude": np.max(magnitudes),
                "avg_confidence": np.mean(confidences),
                "positive_drifts": len([d for d in drifts if d.drift_direction == "positive"]),
                "negative_drifts": len([d for d in drifts if d.drift_direction == "negative"])
            }
        
        return {
            "total_drifts": len(recent_drifts),
            "hours_back": hours_back,
            "drifts_by_metric": drift_stats,
            "most_recent_drift": {
                "metric_type": recent_drifts[-1].metric_type.value,
                "magnitude": recent_drifts[-1].drift_magnitude,
                "direction": recent_drifts[-1].drift_direction,
                "detected_at": recent_drifts[-1].detected_at
            } if recent_drifts else None
        }
    
    def _create_series_key(self, metric_type: MetricType, tags: Dict[str, str]) -> str:
        """Create unique key for metric series"""
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_type.value}:{tag_str}"
    
    def _save_baseline(self, baseline: PerformanceBaseline, series_key: str) -> None:
        """Save baseline to persistent storage"""
        baseline_file = self.storage_path / f"baseline_{series_key.replace(':', '_').replace(',', '_')}.json"
        
        baseline_data = {
            "metric_type": baseline.metric_type.value,
            "baseline_value": baseline.baseline_value,
            "confidence_interval": baseline.confidence_interval,
            "sample_size": baseline.sample_size,
            "created_at": baseline.created_at,
            "tags": baseline.tags
        }
        
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
    
    def _load_historical_data(self) -> None:
        """Load historical baselines from storage"""
        if not self.storage_path.exists():
            return
        
        for baseline_file in self.storage_path.glob("baseline_*.json"):
            try:
                with open(baseline_file, 'r') as f:
                    baseline_data = json.load(f)
                
                metric_type = MetricType(baseline_data["metric_type"])
                baseline = PerformanceBaseline(
                    metric_type=metric_type,
                    baseline_value=baseline_data["baseline_value"],
                    confidence_interval=tuple(baseline_data["confidence_interval"]),
                    sample_size=baseline_data["sample_size"],
                    created_at=baseline_data["created_at"],
                    tags=baseline_data["tags"]
                )
                
                series_key = self._create_series_key(metric_type, baseline.tags)
                self.baselines[series_key] = baseline
                
            except Exception as e:
                print(f"Error loading baseline from {baseline_file}: {e}")
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """Get comprehensive tracking summary"""
        total_points = sum(len(history) for history in self.performance_history.values())
        
        return {
            "total_series": len(self.performance_history),
            "total_data_points": total_points,
            "established_baselines": len(self.baselines),
            "detected_drifts": len(self.drift_history),
            "recent_drifts_24h": len([
                d for d in self.drift_history
                if time.time() - d.detected_at < 86400
            ]),
            "configuration": {
                "history_retention_days": self.history_retention_days,
                "baseline_update_interval": self.baseline_update_interval,
                "drift_threshold": self.drift_threshold,
                "min_baseline_samples": self.min_baseline_samples
            },
            "storage_path": str(self.storage_path)
        }