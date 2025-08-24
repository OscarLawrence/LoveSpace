"""Validation system - micro modules"""

# Core models
from .auto_halt_controller import AutoHaltController
from .coherence_scorer import CoherenceScorer
from .context_validator import ContextValidator

# Validation components
from .contradiction_detector import ContradictionDetector
from .halt_controller import HaltController

# Integration
from .integration.om_hooks import OMIntegration

# Legacy components (to be split)
from .logical_coherence_validator import LogicalCoherenceValidator
from .models import (
    CoherenceScore,
    ContextCompleteness,
    ContradictionReport,
    HaltEvent,
    HaltReason,
    PatternMatch,
    TokenAnalysis,
    ValidationConfig,
    ValidationResult,
    ValidationSession,
    ValidationStatus,
    close_validation_session,
    create_validation_session,
    get_validation_session,
)
from .pattern_matcher import PatternMatcher
from .prerequisite_checker import PrerequisiteChecker
from .token_analyzer import TokenAnalyzer
from .token_efficiency_optimizer import TokenEfficiencyOptimizer

__all__ = [
    # New micro modules
    "ValidationStatus",
    "HaltReason",
    "ValidationResult",
    "ContradictionReport",
    "ContextCompleteness",
    "TokenAnalysis",
    "HaltEvent",
    "CoherenceScore",
    "PatternMatch",
    "ValidationSession",
    "ValidationConfig",
    "create_validation_session",
    "get_validation_session",
    "close_validation_session",
    "ContradictionDetector",
    "ContextValidator",
    "TokenAnalyzer",
    "HaltController",
    "CoherenceScorer",
    "PatternMatcher",
    "OMIntegration",
    # Legacy (to be split)
    "LogicalCoherenceValidator",
    "PrerequisiteChecker",
    "TokenEfficiencyOptimizer",
    "AutoHaltController",
]
