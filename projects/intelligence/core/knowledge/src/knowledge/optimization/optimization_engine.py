"""
Real-Time Optimization Engine - Legacy compatibility module
Imports from new modular structure
"""

from .data_models import (
    OptimizationContext,
    OptimizationDecision,
    OptimizationObjective,
)
from .engine import RealTimeOptimizationEngine

__all__ = ['OptimizationObjective', 'OptimizationContext', 'OptimizationDecision', 'RealTimeOptimizationEngine']