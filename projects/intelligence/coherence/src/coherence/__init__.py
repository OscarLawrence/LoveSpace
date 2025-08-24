"""
Coherence Engine - Real-time logical consistency validation for MomoAI.

This is the foundation that enables building truly coherent AI tools.
"""

from .integration import (
    UnifiedCoherenceEngine,
    get_coherence_engine,
    start_coherence_monitoring,
    validate_reasoning,
    validate_statement,
)
from .monitor import (
    CoherenceEvent,
    CoherenceMonitor,
    get_global_monitor,
    start_global_monitoring,
    validate_with_monitoring,
)
from .validator import (
    CoherenceLevel,
    CoherenceResult,
    LogicalCoherenceValidator,
    create_coherence_validator,
)

__version__ = "0.1.0"

# Convenience exports for easy usage
__all__ = [
    # Core classes
    "LogicalCoherenceValidator",
    "CoherenceMonitor",
    "UnifiedCoherenceEngine",
    # Data classes
    "CoherenceResult",
    "CoherenceLevel",
    "CoherenceEvent",
    # Factory functions
    "create_coherence_validator",
    "get_coherence_engine",
    "get_global_monitor",
    # Convenience functions
    "validate_statement",
    "validate_reasoning",
    "validate_with_monitoring",
    "start_coherence_monitoring",
    "start_global_monitoring",
]
