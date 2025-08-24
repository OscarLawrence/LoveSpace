"""
Data models for workflow automation
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkflowStep:
    """Represents a step in an automated workflow."""
    name: str
    description: str
    command: str
    scopes: List[str]
    dependencies: List[str] = field(default_factory=list)
    timeout_minutes: int = 30
    retry_count: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Represents an automated workflow."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    triggers: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
