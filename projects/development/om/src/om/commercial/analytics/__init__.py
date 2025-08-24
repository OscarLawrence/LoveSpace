"""Analytics module initialization."""

from .models import UsageMetric, PerformanceMetric, ErrorMetric
from .collector import AnalyticsCollector

# Backward compatibility alias
AnalyticsCollector = AnalyticsCollector

__all__ = [
    "UsageMetric",
    "PerformanceMetric", 
    "ErrorMetric",
    "AnalyticsCollector"
]
