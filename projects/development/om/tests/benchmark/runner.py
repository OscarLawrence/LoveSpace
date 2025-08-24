"""
Benchmark runner for context injection testing
"""

import numpy as np
from typing import List

from knowledge.db_manager import ContextDB
from knowledge.embeddings import EmbeddingManager
from .data_models import BenchmarkQuery, BenchmarkResult
from .query_definitions import load_benchmark_queries
from .evaluator import BenchmarkEvaluator


class BenchmarkRunner:
    """Runs context injection benchmarks"""
    
    def __init__(self):
        self.db = ContextDB(":memory:")
        self.embedder = EmbeddingManager(self.db)
        self.benchmark_queries = load_benchmark_queries()
        self.evaluator = BenchmarkEvaluator()
    
    def run_benchmark(self, limit: int = 5) -> List[BenchmarkResult]:
        """Run complete benchmark suite."""
        results = []
        
        for query_spec in self.benchmark_queries:
            try:
                result = self._test_single_query(query_spec, limit)
                results.append(result)
            except Exception as e:
                failed_result = BenchmarkResult(
                    query=query_spec.query,
                    functions_found=[],
                    patterns_found=[],
                    docs_found=[],
                    similarity_scores=[],
                    precision=0.0,
                    recall=0.0,
                    avg_similarity=0.0,
                    passed=False,
                    errors=[f"Benchmark execution failed: {e}"]
                )
                results.append(failed_result)
        
        return results
    
    def _test_single_query(self, query_spec: BenchmarkQuery, limit: int) -> BenchmarkResult:
        """Test a single query and calculate metrics."""
        errors = []
        
        # Get similar functions
        try:
            functions = self.embedder.find_similar_functions(query_spec.query, limit)
            functions_found = [f.name for f in functions]
            similarity_scores = []
            
            if functions and query_spec.query:
                query_embedding = self.embedder.embed_query(query_spec.query)
                for func in functions:
                    func_embedding = self.embedder.embed_function(func)
                    similarity = float(
                        np.dot(query_embedding, func_embedding) / 
                        (np.linalg.norm(query_embedding) * np.linalg.norm(func_embedding))
                    )
                    similarity_scores.append(similarity)
        except Exception as e:
            functions_found = []
            similarity_scores = []
            errors.append(f"Function search failed: {e}")
        
        # Get similar patterns
        try:
            patterns = self.embedder.find_similar_patterns(query_spec.query, limit)
            patterns_found = [p.pattern_type for p in patterns]
        except Exception as e:
            patterns_found = []
            errors.append(f"Pattern search failed: {e}")
        
        # Mock docs search (would integrate with actual docs search)
        docs_found = []  # TODO: Integrate with actual docs search
        
        # Calculate metrics
        precision = self.evaluator.calculate_precision(
            functions_found, patterns_found, docs_found, query_spec
        )
        recall = self.evaluator.calculate_recall(
            functions_found, patterns_found, docs_found, query_spec
        )
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        
        # Determine if test passed
        passed = self.evaluator.evaluate_test_success(
            query_spec, functions_found, patterns_found, docs_found, 
            avg_similarity, precision, recall, errors
        )
        
        return BenchmarkResult(
            query=query_spec.query,
            functions_found=functions_found,
            patterns_found=patterns_found,
            docs_found=docs_found,
            similarity_scores=similarity_scores,
            precision=precision,
            recall=recall,
            avg_similarity=avg_similarity,
            passed=passed,
            errors=errors
        )
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
