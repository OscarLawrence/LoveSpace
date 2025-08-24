"""
Data models for integration management
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ProjectIntegration:
    """Integration configuration for a project"""

    project_name: str
    project_path: Path
    integration_hooks: list[str]
    data_collection_enabled: bool = True
    optimization_enabled: bool = True
    monitoring_level: str = "standard"  # minimal, standard, detailed
    custom_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationStatus:
    """Status of workspace integration"""

    total_projects: int
    integrated_projects: int
    active_collectors: int
    optimization_active: bool
    last_update: float
    errors: list[str] = field(default_factory=list)
