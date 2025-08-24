"""
Benchmark evaluation logic
"""

from typing import List
from .data_models import BenchmarkQuery


class BenchmarkEvaluator:
    """Evaluates benchmark results and calculates metrics"""
    
    def calculate_precision(self, functions_found: List[str], patterns_found: List[str], 
                           docs_found: List[str], query_spec: BenchmarkQuery) -> float:
        """Calculate precision: relevant results / total results."""
        total_found = len(functions_found) + len(patterns_found) + len(docs_found)
        if total_found == 0:
            return 1.0 if not query_spec.expected_functions and not query_spec.expected_patterns else 0.0
        
        relevant_found = 0
        
        # Check function relevance
        for func in functions_found:
            if any(expected in func.lower() for expected in query_spec.expected_functions):
                relevant_found += 1
        
        # Check pattern relevance
        for pattern in patterns_found:
            if any(expected in pattern.lower() for expected in query_spec.expected_patterns):
                relevant_found += 1
        
        # Check docs relevance (when implemented)
        for doc in docs_found:
            if any(keyword in doc.lower() for keyword in query_spec.expected_docs_keywords):
                relevant_found += 1
        
        return relevant_found / total_found
    
    def calculate_recall(self, functions_found: List[str], patterns_found: List[str],
                        docs_found: List[str], query_spec: BenchmarkQuery) -> float:
        """Calculate recall: relevant results found / total relevant results."""
        total_expected = len(query_spec.expected_functions) + len(query_spec.expected_patterns)
        if total_expected == 0:
            return 1.0
        
        relevant_found = 0
        
        # Check if expected functions were found
        for expected_func in query_spec.expected_functions:
            if any(expected_func in func.lower() for func in functions_found):
                relevant_found += 1
        
        # Check if expected patterns were found
        for expected_pattern in query_spec.expected_patterns:
            if any(expected_pattern in pattern.lower() for pattern in patterns_found):
                relevant_found += 1
        
        return relevant_found / total_expected
    
    def evaluate_test_success(self, query_spec: BenchmarkQuery, functions_found: List[str],
                             patterns_found: List[str], docs_found: List[str],
                             avg_similarity: float, precision: float, recall: float,
                             errors: List[str]) -> bool:
        """Determine if a test passed based on multiple criteria."""
        if errors:
            return False
        
        # For empty or non-existent queries, expect low similarity
        if not query_spec.expected_functions and not query_spec.expected_patterns:
            return avg_similarity <= query_spec.min_similarity_threshold
        
        # For real queries, check multiple criteria
        criteria_met = 0
        total_criteria = 4
        
        # Criterion 1: Minimum similarity threshold
        if avg_similarity >= query_spec.min_similarity_threshold:
            criteria_met += 1
        
        # Criterion 2: Precision above 30%
        if precision >= 0.3:
            criteria_met += 1
        
        # Criterion 3: Recall above 20%
        if recall >= 0.2:
            criteria_met += 1
        
        # Criterion 4: At least one relevant result found
        if functions_found or patterns_found or docs_found:
            criteria_met += 1
        
        # Pass if at least 3 out of 4 criteria are met
        return criteria_met >= 3
