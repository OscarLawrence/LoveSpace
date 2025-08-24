"""
Integration Manager - Legacy compatibility module
Imports from new modular structure
"""

from .data_models import ProjectIntegration, IntegrationStatus
from .manager import IntegrationManager

__all__ = ['ProjectIntegration', 'IntegrationStatus', 'IntegrationManager']