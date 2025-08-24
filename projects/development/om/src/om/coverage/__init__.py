"""
Documentation coverage enforcement package
"""

from .data_models import CoverageMetrics, QualityIssue
from .analyzer import CoverageAnalyzer
from .quality_gate import QualityGate
from .reporter import CoverageReporter

__all__ = [
    'CoverageMetrics',
    'QualityIssue',
    'CoverageAnalyzer',
    'QualityGate',
    'CoverageReporter'
]
