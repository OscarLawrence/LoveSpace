"""
Data models for context injection benchmarks
"""

from typing import List
from dataclasses import dataclass


@dataclass
class BenchmarkQuery:
    """Test query with expected results for validation."""
    query: str
    expected_functions: List[str]  # Function names that should appear
    expected_patterns: List[str]   # Pattern types that should appear
    expected_docs_keywords: List[str]  # Keywords that should appear in docs
    min_similarity_threshold: float = 0.3  # Minimum similarity score
    description: str = ""


@dataclass
class BenchmarkResult:
    """Results from a benchmark test."""
    query: str
    functions_found: List[str]
    patterns_found: List[str]
    docs_found: List[str]
    similarity_scores: List[float]
    precision: float  # How many found results were relevant
    recall: float     # How many relevant results were found
    avg_similarity: float
    passed: bool
    errors: List[str]
