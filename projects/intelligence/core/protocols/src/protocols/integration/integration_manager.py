"""
Integration Manager - Legacy compatibility module
Imports from new modular structure
"""

from .data_models import IntegrationStatus, ProjectIntegration
from .manager import IntegrationManager

__all__ = ['ProjectIntegration', 'IntegrationStatus', 'IntegrationManager']