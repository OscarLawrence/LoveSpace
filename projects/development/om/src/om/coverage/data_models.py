"""
Data models for coverage enforcement
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CoverageMetrics:
    """Documentation coverage metrics."""
    total_elements: int
    documented_elements: int
    coverage_percentage: float
    missing_docs: List[str]
    quality_score: float
    issues: List[str]


@dataclass
class QualityIssue:
    """Documentation quality issue."""
    element_name: str
    element_type: str
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    file_path: str
    line_number: int
