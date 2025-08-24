"""
Data models for system orchestration
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ServiceStatus(Enum):
    """Service status states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class ServiceInfo:
    """Information about a managed service"""
    service_id: str
    service_type: str
    status: ServiceStatus
    health_score: float
    last_heartbeat: float
    configuration: Dict[str, Any]
    dependencies: List[str]
    performance_metrics: Dict[str, float]