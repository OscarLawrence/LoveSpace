"""Workflow Automation for Agent Task Management.

Automates common development workflows with intelligent task orchestration.
Legacy compatibility module - imports from new modular structure.
"""

from .workflow.data_models import WorkflowStep, Workflow
from .workflow.engine import WorkflowEngine
from .workflow.templates import WorkflowTemplates

__all__ = ['WorkflowStep', 'Workflow', 'WorkflowEngine', 'WorkflowTemplates']