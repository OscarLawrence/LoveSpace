"""
Orchestration System Package
Master coordination system for AI Performance Optimization
"""

from .configuration_manager import ConfigurationManager
from .data_models import ServiceInfo, ServiceStatus
from .health_monitor import HealthMonitor
from .orchestrator_engine import OrchestratorEngine
from .service_discovery import ServiceDiscovery

# Main class for backward compatibility
SystemOrchestrator = OrchestratorEngine

__all__ = [
    'SystemOrchestrator',
    'OrchestratorEngine',
    'ServiceDiscovery',
    'HealthMonitor', 
    'ConfigurationManager',
    'ServiceStatus',
    'ServiceInfo'
]