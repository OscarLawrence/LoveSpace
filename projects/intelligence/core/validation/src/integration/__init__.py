"""Integration module for OM workflow hooks"""

from ..auto_halt_controller import AutoHaltController
from ..logical_coherence_validator import LogicalCoherenceValidator
from ..prerequisite_checker import PrerequisiteChecker
from ..token_efficiency_optimizer import TokenEfficiencyOptimizer
from ..validation_models import ValidationResult

__all__ = ["OMIntegration"]
