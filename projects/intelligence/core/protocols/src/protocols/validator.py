"""
Protocol validation system for AI communication.
Ensures task specifications are complete and valid before execution.
"""

from dataclasses import dataclass
from typing import Any

from .ai_protocol import AITask, CodeSpec, FileSpec, QuerySpec, TaskType


@dataclass
class ValidationError:
    """Validation error details."""

    field: str
    message: str
    severity: str = "error"  # error, warning, info


class ProtocolValidator:
    """Validates AI task protocols for completeness and correctness."""

    def __init__(self) -> None:
        self.validation_rules = self._load_validation_rules()

    def validate(self, task: AITask) -> list[ValidationError]:
        """Validate an AI task and return any errors found."""
        errors = []

        # Core task validation
        errors.extend(self._validate_core_fields(task))

        # Spec-specific validation
        if task.spec:
            errors.extend(self._validate_spec(task))
        else:
            errors.append(ValidationError("spec", "Task specification is required"))

        # Context validation
        errors.extend(self._validate_context(task))

        # Cross-field validation
        errors.extend(self._validate_consistency(task))

        return errors

    def _validate_core_fields(self, task: AITask) -> list[ValidationError]:
        """Validate core task fields."""
        errors = []

        if not task.task_id:
            errors.append(ValidationError("task_id", "Task ID is required"))

        if task.timeout and task.timeout <= 0:
            errors.append(ValidationError("timeout", "Timeout must be positive"))

        if task.max_retries < 0:
            errors.append(ValidationError("max_retries", "Max retries cannot be negative"))

        return errors

    def _validate_spec(self, task: AITask) -> list[ValidationError]:
        """Validate task specification based on type."""
        errors = []

        if isinstance(task.spec, CodeSpec):
            errors.extend(self._validate_code_spec(task.spec))
        elif isinstance(task.spec, FileSpec):
            errors.extend(self._validate_file_spec(task.spec))
        elif isinstance(task.spec, QuerySpec):
            errors.extend(self._validate_query_spec(task.spec))

        return errors

    def _validate_code_spec(self, spec: CodeSpec) -> list[ValidationError]:
        """Validate code generation specification."""
        errors = []

        if not spec.name:
            errors.append(ValidationError("spec.name", "Code name is required"))

        if not spec.language:
            errors.append(ValidationError("spec.language", "Programming language is required"))

        # Validate parameter names are unique
        param_names = [p.name for p in spec.params]
        if len(param_names) != len(set(param_names)):
            errors.append(ValidationError("spec.params", "Parameter names must be unique"))

        # Validate parameter types
        for param in spec.params:
            if not param.name:
                errors.append(ValidationError("spec.params", "Parameter name is required"))
            if not param.type:
                errors.append(
                    ValidationError("spec.params", f"Parameter type is required for '{param.name}'")
                )

        # Language-specific validation
        if spec.language == "python":
            errors.extend(self._validate_python_spec(spec))
        elif spec.language == "javascript":
            errors.extend(self._validate_javascript_spec(spec))

        return errors

    def _validate_file_spec(self, spec: FileSpec) -> list[ValidationError]:
        """Validate file operation specification."""
        errors = []

        if not spec.path:
            errors.append(ValidationError("spec.path", "File path is required"))

        valid_operations = ["read", "write", "create", "delete", "move", "copy"]
        if spec.operation not in valid_operations:
            errors.append(
                ValidationError(
                    "spec.operation", f"Invalid operation. Must be one of: {valid_operations}"
                )
            )

        # Operation-specific validation
        if spec.operation in ["write", "create"] and spec.content is None:
            errors.append(
                ValidationError(
                    "spec.content", f"Content is required for {spec.operation} operations"
                )
            )

        if spec.operation in ["move", "copy"] and not spec.target_path:
            errors.append(
                ValidationError(
                    "spec.target_path", f"Target path is required for {spec.operation} operations"
                )
            )

        return errors

    def _validate_query_spec(self, spec: QuerySpec) -> list[ValidationError]:
        """Validate database query specification."""
        errors = []

        if not spec.table:
            errors.append(ValidationError("spec.table", "Table name is required"))

        valid_query_types = ["select", "insert", "update", "delete"]
        if spec.query_type not in valid_query_types:
            errors.append(
                ValidationError(
                    "spec.query_type", f"Invalid query type. Must be one of: {valid_query_types}"
                )
            )

        # Query-specific validation
        if spec.query_type == "select" and not spec.fields:
            errors.append(ValidationError("spec.fields", "Fields are required for SELECT queries"))

        if spec.query_type in ["update", "delete"] and not spec.conditions:
            errors.append(
                ValidationError(
                    "spec.conditions",
                    f"Conditions are required for {spec.query_type.upper()} queries",
                )
            )

        return errors

    def _validate_context(self, task: AITask) -> list[ValidationError]:
        """Validate task context."""
        errors = []

        # Check for required capabilities vs target agent
        if task.capabilities_required and not task.target_agent:
            errors.append(
                ValidationError(
                    "target_agent",
                    "Target agent required when capabilities are specified",
                    "warning",
                )
            )

        return errors

    def _validate_consistency(self, task: AITask) -> list[ValidationError]:
        """Validate cross-field consistency."""
        errors = []

        # Task type vs spec type consistency
        if task.task_type == TaskType.CODE_GENERATION and not isinstance(task.spec, CodeSpec):
            errors.append(ValidationError("task_type", "CODE_GENERATION tasks require CodeSpec"))

        if task.task_type == TaskType.FILE_OPERATION and not isinstance(task.spec, FileSpec):
            errors.append(ValidationError("task_type", "FILE_OPERATION tasks require FileSpec"))

        if task.task_type == TaskType.DATABASE_QUERY and not isinstance(task.spec, QuerySpec):
            errors.append(ValidationError("task_type", "DATABASE_QUERY tasks require QuerySpec"))

        return errors

    def _validate_python_spec(self, spec: CodeSpec) -> list[ValidationError]:
        """Python-specific validation rules."""
        errors = []

        # Python naming conventions
        if not spec.name.islower() and "_" not in spec.name:
            errors.append(
                ValidationError("spec.name", "Python functions should use snake_case", "warning")
            )

        # Python type hints
        python_types = ["str", "int", "float", "bool", "list", "dict", "Any", "Optional", "Union"]
        for param in spec.params:
            if param.type not in python_types and not param.type.startswith(
                ("List[", "Dict[", "Optional[")
            ):
                errors.append(
                    ValidationError("spec.params", f"Unknown Python type: {param.type}", "warning")
                )

        return errors

    def _validate_javascript_spec(self, spec: CodeSpec) -> list[ValidationError]:
        """JavaScript-specific validation rules."""
        errors = []

        # JavaScript naming conventions
        if spec.type == "function" and not spec.name[0].islower():
            errors.append(
                ValidationError("spec.name", "JavaScript functions should use camelCase", "warning")
            )

        if spec.type == "component" and not spec.name[0].isupper():
            errors.append(
                ValidationError("spec.name", "React components should use PascalCase", "warning")
            )

        return errors

    def _load_validation_rules(self) -> dict[str, Any]:
        """Load configurable validation rules."""
        return {
            "max_params": 10,
            "max_name_length": 64,
            "required_languages": ["python", "javascript", "typescript", "sql"],
            "timeout_limits": {"min": 1, "max": 3600},
        }

    def is_valid(self, task: AITask) -> bool:
        """Quick validation check - returns True if no errors."""
        errors = self.validate(task)
        return not any(error.severity == "error" for error in errors)
