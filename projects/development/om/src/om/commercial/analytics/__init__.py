"""Analytics module initialization."""

from .collector import AnalyticsCollector
from .models import ErrorMetric, PerformanceMetric, UsageMetric

# Backward compatibility alias
AnalyticsCollector = AnalyticsCollector

__all__ = [
    "UsageMetric",
    "PerformanceMetric", 
    "ErrorMetric",
    "AnalyticsCollector"
]
