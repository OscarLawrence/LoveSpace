"""
Real-Time Optimization Engine - Legacy compatibility module
Imports from new modular structure
"""

from .data_models import OptimizationObjective, OptimizationContext, OptimizationDecision
from .engine import RealTimeOptimizationEngine

__all__ = ['OptimizationObjective', 'OptimizationContext', 'OptimizationDecision', 'RealTimeOptimizationEngine']