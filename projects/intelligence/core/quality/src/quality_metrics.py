"""
Quality Metrics and Data Models
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class QualityMetric:
    name: str
    value: float
    threshold: float
    status: str
    description: str


@dataclass
class QualityGateResult:
    gate_name: str
    passed: bool
    score: float
    metrics: List[QualityMetric]
    recommendations: List[str]
    timestamp: str


@dataclass
class CodeComplexityMetric:
    file_path: str
    function_name: str
    complexity_score: int
    line_count: int
    parameter_count: int
    nesting_depth: int


@dataclass
class FileQualityMetric:
    file_path: str
    line_count: int
    function_count: int
    class_count: int
    complexity_score: float
    documentation_ratio: float
    test_coverage: float