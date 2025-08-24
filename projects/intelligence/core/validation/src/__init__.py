"""Validation system - micro modules"""

# Core models
from .models import (
    ValidationStatus, HaltReason, ValidationResult, ContradictionReport,
    ContextCompleteness, TokenAnalysis, HaltEvent, CoherenceScore,
    PatternMatch, ValidationSession, ValidationConfig,
    create_validation_session, get_validation_session, close_validation_session
)

# Validation components
from .contradiction_detector import ContradictionDetector
from .context_validator import ContextValidator
from .token_analyzer import TokenAnalyzer
from .halt_controller import HaltController
from .coherence_scorer import CoherenceScorer
from .pattern_matcher import PatternMatcher

# Integration
from .integration.om_hooks import OMIntegration

# Legacy components (to be split)
from .logical_coherence_validator import LogicalCoherenceValidator
from .prerequisite_checker import PrerequisiteChecker
from .token_efficiency_optimizer import TokenEfficiencyOptimizer
from .auto_halt_controller import AutoHaltController

__all__ = [
    # New micro modules
    'ValidationStatus', 'HaltReason', 'ValidationResult', 'ContradictionReport',
    'ContextCompleteness', 'TokenAnalysis', 'HaltEvent', 'CoherenceScore',
    'PatternMatch', 'ValidationSession', 'ValidationConfig',
    'create_validation_session', 'get_validation_session', 'close_validation_session',
    'ContradictionDetector', 'ContextValidator', 'TokenAnalyzer',
    'HaltController', 'CoherenceScorer', 'PatternMatcher',
    'OMIntegration',
    
    # Legacy (to be split)
    'LogicalCoherenceValidator', 'PrerequisiteChecker', 
    'TokenEfficiencyOptimizer', 'AutoHaltController'
]
