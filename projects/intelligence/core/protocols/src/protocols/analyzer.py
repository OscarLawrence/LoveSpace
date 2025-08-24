"""
Metrics Analyzer - Advanced performance analysis and insights
"""

import time
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats
from collections import defaultdict
from dataclasses import dataclass

from .collector import MetricType, MetricPoint, MetricSeries


@dataclass
class PerformanceInsight:
    """Performance analysis insight"""
    insight_type: str
    metric_type: MetricType
    description: str
    severity: str  # "low", "medium", "high", "critical"
    confidence: float
    recommendation: str
    supporting_data: Dict[str, Any]


class MetricsAnalyzer:
    """Advanced performance analysis and insights generation"""
    
    def __init__(self):
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_ttl = 300.0  # 5 minutes
        self.insights_history: List[PerformanceInsight] = []
    
    def analyze_performance_patterns(self, metrics_data: Dict[str, MetricSeries]) -> Dict[str, Any]:
        """Comprehensive performance pattern analysis"""
        analysis_results = {
            "timestamp": time.time(),
            "patterns": {},
            "anomalies": {},
            "correlations": {},
            "insights": []
        }
        
        # Pattern detection
        for series_key, series in metrics_data.items():
            if len(series.points) < 10:
                continue
            
            patterns = self._detect_patterns(series)
            if patterns:
                analysis_results["patterns"][series_key] = patterns
        
        # Anomaly detection
        anomalies = self._detect_anomalies(metrics_data)
        analysis_results["anomalies"] = anomalies
        
        # Correlation analysis
        correlations = self._analyze_correlations(metrics_data)
        analysis_results["correlations"] = correlations
        
        # Generate insights
        insights = self._generate_insights(metrics_data, analysis_results)
        analysis_results["insights"] = insights
        
        return analysis_results
    
    def _detect_patterns(self, series: MetricSeries) -> Dict[str, Any]:
        """Detect patterns in metric series"""
        if len(series.points) < 10:
            return {}
        
        values = [point.value for point in series.points]
        timestamps = [point.timestamp for point in series.points]
        
        patterns = {}
        
        # Trend detection
        trend = self._detect_trend(values, timestamps)
        if trend:
            patterns["trend"] = trend
        
        # Seasonality detection
        seasonality = self._detect_seasonality(values, timestamps)
        if seasonality:
            patterns["seasonality"] = seasonality
        
        # Cycle detection
        cycles = self._detect_cycles(values)
        if cycles:
            patterns["cycles"] = cycles
        
        # Volatility analysis
        volatility = self._analyze_volatility(values)
        patterns["volatility"] = volatility
        
        return patterns
    
    def _detect_trend(self, values: List[float], timestamps: List[float]) -> Optional[Dict[str, Any]]:
        """Detect trend in time series"""
        if len(values) < 5:
            return None
        
        # Normalize timestamps
        time_normalized = np.array(timestamps) - timestamps[0]
        
        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_normalized, values)
        
        # Determine trend significance
        if abs(r_value) < 0.3 or p_value > 0.05:
            return None
        
        trend_type = "increasing" if slope > 0 else "decreasing"
        strength = abs(r_value)
        
        return {
            "type": trend_type,
            "slope": slope,
            "strength": strength,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "confidence": 1 - p_value
        }
    
    def _detect_seasonality(self, values: List[float], timestamps: List[float]) -> Optional[Dict[str, Any]]:
        """Detect seasonal patterns"""
        if len(values) < 20:
            return None
        
        # Simple seasonality detection using autocorrelation
        # Check for patterns at different lags
        max_lag = min(len(values) // 4, 50)
        autocorrelations = []
        
        for lag in range(1, max_lag):
            if lag >= len(values):
                break
            
            # Calculate autocorrelation at this lag
            corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
            if not np.isnan(corr):
                autocorrelations.append((lag, corr))
        
        if not autocorrelations:
            return None
        
        # Find strongest autocorrelation
        best_lag, best_corr = max(autocorrelations, key=lambda x: abs(x[1]))
        
        if abs(best_corr) < 0.4:
            return None
        
        # Estimate period from timestamps
        if len(timestamps) > best_lag:
            period_seconds = (timestamps[best_lag] - timestamps[0])
            period_hours = period_seconds / 3600
        else:
            period_hours = None
        
        return {
            "lag": best_lag,
            "correlation": best_corr,
            "period_hours": period_hours,
            "strength": abs(best_corr)
        }
    
    def _detect_cycles(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Detect cyclical patterns using FFT"""
        if len(values) < 20:
            return None
        
        try:
            # Remove trend
            detrended = stats.detrend(values)
            
            # Apply FFT
            fft = np.fft.fft(detrended)
            freqs = np.fft.fftfreq(len(detrended))
            
            # Find dominant frequencies
            power = np.abs(fft) ** 2
            dominant_freq_idx = np.argmax(power[1:len(power)//2]) + 1
            dominant_freq = freqs[dominant_freq_idx]
            
            if abs(dominant_freq) < 0.01:  # Very low frequency
                return None
            
            cycle_length = 1 / abs(dominant_freq)
            power_ratio = power[dominant_freq_idx] / np.sum(power)
            
            return {
                "dominant_frequency": dominant_freq,
                "cycle_length": cycle_length,
                "power_ratio": power_ratio,
                "strength": power_ratio
            }
        
        except Exception:
            return None
    
    def _analyze_volatility(self, values: List[float]) -> Dict[str, Any]:
        """Analyze volatility characteristics"""
        if len(values) < 2:
            return {"volatility": 0.0}
        
        # Calculate various volatility measures
        std_dev = np.std(values)
        mean_val = np.mean(values)
        
        # Coefficient of variation
        cv = std_dev / mean_val if mean_val != 0 else float('inf')
        
        # Rolling volatility (if enough data)
        rolling_volatility = []
        if len(values) >= 10:
            window_size = min(10, len(values) // 2)
            for i in range(window_size, len(values)):
                window_std = np.std(values[i-window_size:i])
                rolling_volatility.append(window_std)
        
        return {
            "standard_deviation": std_dev,
            "coefficient_of_variation": cv,
            "volatility_level": "high" if cv > 0.3 else "medium" if cv > 0.1 else "low",
            "rolling_volatility": rolling_volatility,
            "volatility_trend": self._analyze_volatility_trend(rolling_volatility) if rolling_volatility else None
        }
    
    def _analyze_volatility_trend(self, rolling_volatility: List[float]) -> str:
        """Analyze trend in volatility"""
        if len(rolling_volatility) < 3:
            return "stable"
        
        # Simple trend in volatility
        x = np.arange(len(rolling_volatility))
        slope, _, _, p_value, _ = stats.linregress(x, rolling_volatility)
        
        if p_value > 0.05:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _detect_anomalies(self, metrics_data: Dict[str, MetricSeries]) -> Dict[str, List[Dict[str, Any]]]:
        """Detect anomalies in metrics using statistical methods"""
        anomalies = {}
        
        for series_key, series in metrics_data.items():
            if len(series.points) < 10:
                continue
            
            values = [point.value for point in series.points]
            timestamps = [point.timestamp for point in series.points]
            
            series_anomalies = []
            
            # Z-score based anomaly detection
            z_scores = np.abs(stats.zscore(values))
            z_threshold = 3.0
            
            for i, (z_score, value, timestamp) in enumerate(zip(z_scores, values, timestamps)):
                if z_score > z_threshold:
                    series_anomalies.append({
                        "type": "statistical_outlier",
                        "index": i,
                        "value": value,
                        "timestamp": timestamp,
                        "z_score": z_score,
                        "severity": "high" if z_score > 4 else "medium"
                    })
            
            # IQR based anomaly detection
            q1, q3 = np.percentile(values, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                if value < lower_bound or value > upper_bound:
                    # Check if already detected by z-score
                    if not any(a["index"] == i for a in series_anomalies):
                        series_anomalies.append({
                            "type": "iqr_outlier",
                            "index": i,
                            "value": value,
                            "timestamp": timestamp,
                            "bounds": (lower_bound, upper_bound),
                            "severity": "medium"
                        })
            
            if series_anomalies:
                anomalies[series_key] = series_anomalies
        
        return anomalies
    
    def _analyze_correlations(self, metrics_data: Dict[str, MetricSeries]) -> Dict[str, Any]:
        """Analyze correlations between different metrics"""
        correlations = {}
        
        # Get metric types with sufficient data
        metric_series = {}
        for series_key, series in metrics_data.items():
            if len(series.points) >= 10:
                metric_series[series_key] = series
        
        if len(metric_series) < 2:
            return correlations
        
        # Calculate pairwise correlations
        series_keys = list(metric_series.keys())
        for i in range(len(series_keys)):
            for j in range(i + 1, len(series_keys)):
                key1, key2 = series_keys[i], series_keys[j]
                
                correlation = self._calculate_correlation(
                    metric_series[key1], metric_series[key2]
                )
                
                if correlation and abs(correlation["correlation"]) > 0.3:
                    pair_key = f"{key1}_{key2}"
                    correlations[pair_key] = correlation
        
        return correlations
    
    def _calculate_correlation(self, series1: MetricSeries, series2: MetricSeries) -> Optional[Dict[str, Any]]:
        """Calculate correlation between two metric series"""
        # Align timestamps (simple approach - use overlapping time window)
        timestamps1 = [p.timestamp for p in series1.points]
        timestamps2 = [p.timestamp for p in series2.points]
        
        min_time = max(min(timestamps1), min(timestamps2))
        max_time = min(max(timestamps1), max(timestamps2))
        
        if max_time <= min_time:
            return None
        
        # Get values in overlapping window
        values1 = [p.value for p in series1.points if min_time <= p.timestamp <= max_time]
        values2 = [p.value for p in series2.points if min_time <= p.timestamp <= max_time]
        
        if len(values1) < 5 or len(values2) < 5:
            return None
        
        # Calculate correlation
        try:
            correlation, p_value = stats.pearsonr(values1, values2)
            
            return {
                "correlation": correlation,
                "p_value": p_value,
                "sample_size": min(len(values1), len(values2)),
                "significance": "significant" if p_value < 0.05 else "not_significant",
                "strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.3 else "weak"
            }
        except Exception:
            return None
    
    def _generate_insights(self, metrics_data: Dict[str, MetricSeries], 
                          analysis_results: Dict[str, Any]) -> List[PerformanceInsight]:
        """Generate actionable insights from analysis"""
        insights = []
        
        # Analyze patterns for insights
        for series_key, patterns in analysis_results["patterns"].items():
            series = metrics_data[series_key]
            
            # Trend insights
            if "trend" in patterns:
                trend = patterns["trend"]
                if trend["strength"] > 0.7:
                    severity = "high" if trend["strength"] > 0.9 else "medium"
                    
                    if trend["type"] == "decreasing":
                        insight = PerformanceInsight(
                            insight_type="performance_decline",
                            metric_type=series.metric_type,
                            description=f"Strong declining trend detected in {series.metric_type.value}",
                            severity=severity,
                            confidence=trend["confidence"],
                            recommendation="Investigate root cause and implement corrective measures",
                            supporting_data=trend
                        )
                        insights.append(insight)
        
        # Anomaly insights
        for series_key, anomalies in analysis_results["anomalies"].items():
            if len(anomalies) > 3:  # Multiple anomalies
                series = metrics_data[series_key]
                
                insight = PerformanceInsight(
                    insight_type="frequent_anomalies",
                    metric_type=series.metric_type,
                    description=f"Multiple anomalies detected in {series.metric_type.value}",
                    severity="medium",
                    confidence=0.8,
                    recommendation="Review system stability and consider implementing monitoring alerts",
                    supporting_data={"anomaly_count": len(anomalies)}
                )
                insights.append(insight)
        
        # Correlation insights
        for pair_key, correlation in analysis_results["correlations"].items():
            if correlation["strength"] == "strong" and correlation["significance"] == "significant":
                insight = PerformanceInsight(
                    insight_type="strong_correlation",
                    metric_type=MetricType.ACCURACY,  # Generic
                    description=f"Strong correlation found between metrics: {pair_key}",
                    severity="low",
                    confidence=1 - correlation["p_value"],
                    recommendation="Consider leveraging this relationship for predictive optimization",
                    supporting_data=correlation
                )
                insights.append(insight)
        
        return insights
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive analysis summary"""
        return {
            "cache_entries": len(self.analysis_cache),
            "cache_ttl": self.cache_ttl,
            "insights_generated": len(self.insights_history),
            "recent_insights": [
                {
                    "type": insight.insight_type,
                    "metric": insight.metric_type.value,
                    "severity": insight.severity,
                    "confidence": insight.confidence
                }
                for insight in self.insights_history[-10:]
            ]
        }