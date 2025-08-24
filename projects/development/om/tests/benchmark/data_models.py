"""
Data models for context injection benchmarks
"""

from dataclasses import dataclass


@dataclass
class BenchmarkQuery:
    """Test query with expected results for validation."""

    query: str
    expected_functions: list[str]  # Function names that should appear
    expected_patterns: list[str]  # Pattern types that should appear
    expected_docs_keywords: list[str]  # Keywords that should appear in docs
    min_similarity_threshold: float = 0.3  # Minimum similarity score
    description: str = ""


@dataclass
class BenchmarkResult:
    """Results from a benchmark test."""

    query: str
    functions_found: list[str]
    patterns_found: list[str]
    docs_found: list[str]
    similarity_scores: list[float]
    precision: float  # How many found results were relevant
    recall: float  # How many relevant results were found
    avg_similarity: float
    passed: bool
    errors: list[str]
