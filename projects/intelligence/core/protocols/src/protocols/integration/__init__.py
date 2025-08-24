"""
Integration management package
"""

from .data_models import IntegrationStatus, ProjectIntegration
from .hook_factory import HookFactory
from .manager import IntegrationManager
from .project_discovery import ProjectDiscovery
from .system_manager import SystemManager

__all__ = [
    'ProjectIntegration',
    'IntegrationStatus',
    'IntegrationManager',
    'ProjectDiscovery',
    'HookFactory',
    'SystemManager'
]