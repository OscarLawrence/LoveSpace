"""
Monitoring Dashboard - Unified monitoring interface
Real-time visualization of workspace performance and optimization
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class DashboardMetric:
    """Dashboard metric display configuration"""
    name: str
    value: float
    unit: str
    trend: str  # "up", "down", "stable"
    status: str  # "good", "warning", "critical"
    last_updated: float


class MonitoringDashboard:
    """Unified monitoring dashboard for workspace integration"""
    
    def __init__(self):
        self.metrics: Dict[str, DashboardMetric] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.performance_history: List[Dict[str, Any]] = []
        
    def update_metric(self, name: str, value: float, unit: str = "", 
                     status: str = "good") -> None:
        """Update dashboard metric"""
        # Determine trend
        trend = "stable"
        if name in self.metrics:
            old_value = self.metrics[name].value
            if value > old_value * 1.05:
                trend = "up"
            elif value < old_value * 0.95:
                trend = "down"
        
        self.metrics[name] = DashboardMetric(
            name=name,
            value=value,
            unit=unit,
            trend=trend,
            status=status,
            last_updated=time.time()
        )
    
    def add_alert(self, alert_type: str, message: str, severity: str = "info") -> None:
        """Add alert to dashboard"""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": time.time()
        }
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "metrics": {name: {
                "value": metric.value,
                "unit": metric.unit,
                "trend": metric.trend,
                "status": metric.status,
                "last_updated": metric.last_updated
            } for name, metric in self.metrics.items()},
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "performance_history": self.performance_history[-50:],  # Last 50 entries
            "dashboard_updated": time.time()
        }