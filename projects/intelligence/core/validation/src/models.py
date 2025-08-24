"""Core data models for validation system - 150 LOC max"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Set
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


class HaltReason(Enum):
    """Reasons for execution halt"""
    LOGICAL_CONTRADICTION = "logical_contradiction"
    MISSING_CONTEXT = "missing_context"
    TOKEN_LIMIT = "token_limit"
    CRITICAL_ERROR = "critical_error"
    USER_REQUEST = "user_request"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    status: ValidationStatus
    message: str
    score: float = 0.0
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class ContradictionReport:
    """Report of logical contradictions found"""
    statement_a: str
    statement_b: str
    contradiction_type: str
    confidence: float
    context: str
    line_numbers: Optional[List[int]] = None
    
    def __post_init__(self):
        if self.line_numbers is None:
            self.line_numbers = []


@dataclass
class ContextCompleteness:
    """Context completeness assessment"""
    required_elements: Set[str]
    present_elements: Set[str]
    missing_elements: Set[str]
    completeness_score: float
    critical_missing: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.critical_missing is None:
            self.critical_missing = []
        self.missing_elements = self.required_elements - self.present_elements


@dataclass
class TokenAnalysis:
    """Token usage analysis"""
    total_tokens: int
    estimated_tokens: int
    efficiency_score: float
    optimization_suggestions: List[str]
    cost_estimate: float = 0.0
    
    def __post_init__(self):
        if not self.optimization_suggestions:
            self.optimization_suggestions = []


@dataclass
class HaltEvent:
    """Execution halt event"""
    reason: HaltReason
    message: str
    timestamp: str
    context: Dict[str, Any]
    recoverable: bool = True
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class CoherenceScore:
    """Logical coherence scoring"""
    overall_score: float
    contradiction_penalty: float
    completeness_bonus: float
    pattern_consistency: float
    confidence_level: float
    breakdown: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.breakdown is None:
            self.breakdown = {}


@dataclass
class PatternMatch:
    """Pattern matching result"""
    pattern_id: str
    match_confidence: float
    matched_text: str
    context_span: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationSession:
    """Validation session state"""
    session_id: str
    start_time: str
    current_context: str
    validation_results: List[ValidationResult]
    halt_events: List[HaltEvent]
    token_usage: TokenAnalysis
    active: bool = True
    
    def __post_init__(self):
        if not self.validation_results:
            self.validation_results = []
        if not self.halt_events:
            self.halt_events = []


class ValidationConfig:
    """Configuration for validation system"""
    
    def __init__(self):
        self.max_token_limit = 100000
        self.halt_on_contradiction = True
        self.completeness_threshold = 0.7
        self.confidence_threshold = 0.8
        self.enable_pattern_matching = True
        self.auto_optimize_tokens = True
        self.log_validation_events = True


# Validation registry for tracking active validations
validation_registry: Dict[str, ValidationSession] = {}


def create_validation_session(session_id: str, context: str) -> ValidationSession:
    """Create new validation session"""
    from datetime import datetime
    
    session = ValidationSession(
        session_id=session_id,
        start_time=datetime.now().isoformat(),
        current_context=context,
        validation_results=[],
        halt_events=[],
        token_usage=TokenAnalysis(0, 0, 1.0, [])
    )
    
    validation_registry[session_id] = session
    return session


def get_validation_session(session_id: str) -> Optional[ValidationSession]:
    """Get existing validation session"""
    return validation_registry.get(session_id)


def close_validation_session(session_id: str) -> None:
    """Close and remove validation session"""
    if session_id in validation_registry:
        validation_registry[session_id].active = False
        del validation_registry[session_id]
