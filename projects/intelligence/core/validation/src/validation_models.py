"""
Data models for validation system components.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HaltReason(Enum):
    LOGICAL_CONTRADICTION = "logical_contradiction"
    MISSING_PREREQUISITES = "missing_prerequisites"
    TOKEN_BUDGET_EXCEEDED = "token_budget_exceeded"
    QUALITY_THRESHOLD_VIOLATED = "quality_threshold_violated"
    USER_REQUESTED = "user_requested"


@dataclass
class CoherenceIssue:
    """Represents a logical coherence issue detected in a request."""

    issue_type: str
    description: str
    severity: SeverityLevel
    location: str | None = None
    suggested_fix: str | None = None
    confidence: float = 0.0


@dataclass
class PrerequisiteStatus:
    """Status of prerequisite validation."""

    name: str
    satisfied: bool
    description: str
    missing_items: list[str]
    satisfaction_score: float


@dataclass
class TokenAnalysis:
    """Token usage analysis and optimization suggestions."""

    current_tokens: int
    estimated_tokens: int
    budget_remaining: int
    efficiency_score: float
    optimization_suggestions: list[str]
    projected_savings: int


@dataclass
class HaltEvent:
    """Records an execution halt event."""

    reason: HaltReason
    description: str
    timestamp: str
    context: dict[str, Any]
    recovery_suggestions: list[str]


@dataclass
class ValidationResult:
    """Complete validation result for a request."""

    is_valid: bool
    coherence_issues: list[CoherenceIssue]
    prerequisite_status: list[PrerequisiteStatus]
    token_analysis: TokenAnalysis
    halt_events: list[HaltEvent]
    overall_score: float
    recommendations: list[str]
