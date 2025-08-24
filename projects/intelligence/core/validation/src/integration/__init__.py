"""Integration module for OM workflow hooks"""

from ..logical_coherence_validator import LogicalCoherenceValidator
from ..prerequisite_checker import PrerequisiteChecker  
from ..token_efficiency_optimizer import TokenEfficiencyOptimizer
from ..auto_halt_controller import AutoHaltController
from ..validation_models import ValidationResult

__all__ = [
    'OMIntegration'
]
