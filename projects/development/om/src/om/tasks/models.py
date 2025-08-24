"""Task management data models."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TaskPriority(Enum):
    """Task priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(Enum):
    """Task type enumeration."""

    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    REFACTORING = "refactoring"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"


@dataclass
class TaskContext:
    """Context information for task execution."""

    scopes: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskMetrics:
    """Task execution metrics."""

    estimated_duration: int | None = None  # minutes
    actual_duration: int | None = None
    complexity_score: float = 0.0
    progress_percentage: float = 0.0
    quality_score: float | None = None
    effort_points: int = 1


@dataclass
class Task:
    """Represents a development task."""

    id: str
    title: str
    description: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: datetime | None = None
    assigned_to: str | None = None
    tags: list[str] = field(default_factory=list)
    context: TaskContext = field(default_factory=TaskContext)
    metrics: TaskMetrics = field(default_factory=TaskMetrics)
    subtasks: list[str] = field(default_factory=list)
    parent_task: str | None = None
    notes: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def add_note(self, note: str):
        """Add a note to the task."""
        self.notes.append(f"{datetime.now().isoformat()}: {note}")
        self.updated_at = datetime.now()

    def update_progress(self, percentage: float):
        """Update task progress percentage."""
        self.metrics.progress_percentage = max(0.0, min(100.0, percentage))
        self.updated_at = datetime.now()

        if percentage >= 100.0 and self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.COMPLETED

    def add_subtask(self, subtask_id: str):
        """Add a subtask to this task."""
        if subtask_id not in self.subtasks:
            self.subtasks.append(subtask_id)
            self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status not in [
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ]:
            return datetime.now() > self.due_date
        return False

    def get_age_days(self) -> int:
        """Get task age in days."""
        return (datetime.now() - self.created_at).days
