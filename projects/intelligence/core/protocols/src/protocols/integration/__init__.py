"""
Integration management package
"""

from .data_models import ProjectIntegration, IntegrationStatus
from .manager import IntegrationManager
from .project_discovery import ProjectDiscovery
from .hook_factory import HookFactory
from .system_manager import SystemManager

__all__ = [
    'ProjectIntegration',
    'IntegrationStatus',
    'IntegrationManager',
    'ProjectDiscovery',
    'HookFactory',
    'SystemManager'
]