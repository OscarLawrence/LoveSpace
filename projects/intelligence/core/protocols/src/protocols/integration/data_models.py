"""
Data models for integration management
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectIntegration:
    """Integration configuration for a project"""
    project_name: str
    project_path: Path
    integration_hooks: List[str]
    data_collection_enabled: bool = True
    optimization_enabled: bool = True
    monitoring_level: str = "standard"  # minimal, standard, detailed
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationStatus:
    """Status of workspace integration"""
    total_projects: int
    integrated_projects: int
    active_collectors: int
    optimization_active: bool
    last_update: float
    errors: List[str] = field(default_factory=list)
