"""
Data models for system orchestration
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


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
    configuration: dict[str, Any]
    dependencies: list[str]
    performance_metrics: dict[str, float]
