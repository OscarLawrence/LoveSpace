"""Test AI protocol functionality."""

from protocols.ai_protocol import AITask, CodeSpec, Priority, ProtocolBuilder, TaskType


def test_task_type_enum() -> None:
    """Test TaskType enum values."""
    assert TaskType.CODE_GENERATION.value == "code_generation"
    assert TaskType.CODE_ANALYSIS.value == "code_analysis"
    assert TaskType.CODE_REFACTOR.value == "code_refactor"


def test_ai_task_creation() -> None:
    """Test AITask creation with basic fields."""
    task = AITask(task_type=TaskType.CODE_GENERATION, priority=Priority.HIGH)

    assert task.task_type == TaskType.CODE_GENERATION
    assert task.priority == Priority.HIGH
    assert task.task_id is not None


def test_protocol_builder() -> None:
    """Test ProtocolBuilder fluent interface."""
    builder = ProtocolBuilder()
    task = (
        builder.task_type(TaskType.CODE_GENERATION)
        .code_spec("test_function", "python")
        .priority(Priority.HIGH)
        .target_agent("test-agent")
        .build()
    )

    assert task.task_type == TaskType.CODE_GENERATION
    assert task.priority == Priority.HIGH
    assert task.target_agent == "test-agent"
    assert isinstance(task.spec, CodeSpec)
    assert task.spec.name == "test_function"


def test_task_serialization() -> None:
    """Test task can be serialized to dict."""
    task = AITask(task_type=TaskType.CODE_ANALYSIS, priority=Priority.NORMAL)

    task_dict = task.to_dict()
    assert isinstance(task_dict, dict)
    assert task_dict["task_type"] == "code_analysis"
    assert task_dict["priority"] == "normal"
