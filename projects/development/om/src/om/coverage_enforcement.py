"""Documentation Coverage Enforcement System.

Ensures comprehensive documentation coverage with quality gates.
Legacy compatibility module - imports from new modular structure.
"""

from .coverage.data_models import CoverageMetrics, QualityIssue
from .coverage.analyzer import CoverageAnalyzer
from .coverage.quality_gate import QualityGate
from .coverage.reporter import CoverageReporter

__all__ = ['CoverageMetrics', 'QualityIssue', 'CoverageAnalyzer', 'QualityGate', 'CoverageReporter']