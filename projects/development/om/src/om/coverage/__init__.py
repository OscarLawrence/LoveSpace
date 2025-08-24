"""
Documentation coverage enforcement package
"""

from .analyzer import CoverageAnalyzer
from .data_models import CoverageMetrics, QualityIssue
from .quality_gate import QualityGate
from .reporter import CoverageReporter

__all__ = [
    "CoverageMetrics",
    "QualityIssue",
    "CoverageAnalyzer",
    "QualityGate",
    "CoverageReporter",
]
