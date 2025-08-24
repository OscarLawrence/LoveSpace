"""
AI Communication Protocol - Structured format for AI-to-AI communication.
Enables precise, unambiguous instruction passing between AI agents.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class TaskType(Enum):
    """Core task types for AI agents."""

    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REFACTOR = "code_refactor"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    DATABASE_QUERY = "database_query"
    FILE_OPERATION = "file_operation"
    SYSTEM_COMMAND = "system_command"


class Priority(Enum):
    """Task priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Parameter:
    """Function or method parameter specification."""

    name: str
    type: str
    required: bool = True
    default: Any | None = None
    description: str | None = None


@dataclass
class ReturnSpec:
    """Return value specification."""

    type: str
    nullable: bool = False
    description: str | None = None


@dataclass
class CodeSpec:
    """Specification for code generation tasks."""

    name: str
    type: Literal["function", "class", "module", "component"]
    language: str
    params: list[Parameter] = field(default_factory=list)
    returns: ReturnSpec | None = None
    requirements: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class FileSpec:
    """File operation specification."""

    path: str
    operation: Literal["read", "write", "create", "delete", "move", "copy"]
    content: str | None = None
    target_path: str | None = None  # For move/copy operations


@dataclass
class QuerySpec:
    """Database query specification."""

    query_type: Literal["select", "insert", "update", "delete"]
    table: str
    fields: list[str] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)
    joins: list[str] = field(default_factory=list)
    limit: int | None = None


@dataclass
class Context:
    """Execution context and environment information."""

    codebase_patterns: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    related_files: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Standardized task execution result."""

    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time: float | None = None


@dataclass
class AITask:
    """Core AI task instruction protocol."""

    # Core identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.CODE_GENERATION
    created_at: datetime = field(default_factory=datetime.now)

    # Task specification
    spec: CodeSpec | FileSpec | QuerySpec | dict[str, Any] | None = None
    context: Context = field(default_factory=Context)

    # Execution metadata
    priority: Priority = Priority.NORMAL
    timeout: int | None = None
    retry_count: int = 0
    max_retries: int = 3

    # Agent targeting
    target_agent: str | None = None
    capabilities_required: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "created_at": self.created_at.isoformat(),
            "spec": self._spec_to_dict(),
            "context": self._context_to_dict(),
            "priority": self.priority.value,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "target_agent": self.target_agent,
            "capabilities_required": self.capabilities_required,
        }

    def _spec_to_dict(self) -> dict[str, Any]:
        """Convert spec to dictionary."""
        if hasattr(self.spec, "__dict__"):
            return self.spec.__dict__
        return self.spec if isinstance(self.spec, dict) else {}

    def _context_to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "codebase_patterns": self.context.codebase_patterns,
            "dependencies": self.context.dependencies,
            "environment": self.context.environment,
            "constraints": self.context.constraints,
            "related_files": self.context.related_files,
        }


class ProtocolBuilder:
    """Builder for creating AI tasks with fluent interface."""

    def __init__(self) -> None:
        self.task = AITask()

    def task_type(self, task_type: TaskType) -> "ProtocolBuilder":
        self.task.task_type = task_type
        return self

    def priority(self, priority: Priority) -> "ProtocolBuilder":
        self.task.priority = priority
        return self

    def target_agent(self, agent: str) -> "ProtocolBuilder":
        self.task.target_agent = agent
        return self

    def code_spec(
        self,
        name: str,
        lang: str,
        type: Literal["function", "class", "module", "component"] = "function",
    ) -> "ProtocolBuilder":
        self.task.spec = CodeSpec(name=name, language=lang, type=type)
        return self

    def file_spec(
        self, path: str, operation: Literal["read", "write", "create", "delete", "move", "copy"]
    ) -> "ProtocolBuilder":
        self.task.spec = FileSpec(path=path, operation=operation)
        return self

    def query_spec(
        self, query_type: Literal["select", "insert", "update", "delete"], table: str
    ) -> "ProtocolBuilder":
        self.task.spec = QuerySpec(query_type=query_type, table=table)
        return self

    def add_param(self, name: str, type: str, required: bool = True) -> "ProtocolBuilder":
        if isinstance(self.task.spec, CodeSpec):
            self.task.spec.params.append(Parameter(name=name, type=type, required=required))
        return self

    def returns(self, type: str, nullable: bool = False) -> "ProtocolBuilder":
        if isinstance(self.task.spec, CodeSpec):
            self.task.spec.returns = ReturnSpec(type=type, nullable=nullable)
        return self

    def context(self, **kwargs: Any) -> "ProtocolBuilder":
        for key, value in kwargs.items():
            if hasattr(self.task.context, key):
                setattr(self.task.context, key, value)
        return self

    def build(self) -> AITask:
        return self.task
