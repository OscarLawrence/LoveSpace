"""
Data models for validation system components.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum


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
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: float = 0.0


@dataclass
class PrerequisiteStatus:
    """Status of prerequisite validation."""
    name: str
    satisfied: bool
    description: str
    missing_items: List[str]
    satisfaction_score: float


@dataclass
class TokenAnalysis:
    """Token usage analysis and optimization suggestions."""
    current_tokens: int
    estimated_tokens: int
    budget_remaining: int
    efficiency_score: float
    optimization_suggestions: List[str]
    projected_savings: int


@dataclass
class HaltEvent:
    """Records an execution halt event."""
    reason: HaltReason
    description: str
    timestamp: str
    context: Dict[str, Any]
    recovery_suggestions: List[str]


@dataclass
class ValidationResult:
    """Complete validation result for a request."""
    is_valid: bool
    coherence_issues: List[CoherenceIssue]
    prerequisite_status: List[PrerequisiteStatus]
    token_analysis: TokenAnalysis
    halt_events: List[HaltEvent]
    overall_score: float
    recommendations: List[str]
