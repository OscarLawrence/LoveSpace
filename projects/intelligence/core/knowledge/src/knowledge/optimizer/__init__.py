"""
Optimizer integration package
"""

from .data_models import PerformancePattern, OptimizationSession
from .pattern_storage import PatternStorage
from .session_manager import SessionManager
from .recommendation_engine import RecommendationEngine
from .memory_consolidation import MemoryConsolidation
from .analysis import PerformanceAnalyzer
from .memory_optimizer import MemoryIntegratedOptimizer

# Import AIOptimizer from parent module
from ..optimizer import AIOptimizer

__all__ = [
    'AIOptimizer',
    'PerformancePattern',
    'OptimizationSession',
    'PatternStorage',
    'SessionManager', 
    'RecommendationEngine',
    'MemoryConsolidation',
    'PerformanceAnalyzer',
    'MemoryIntegratedOptimizer'
]
