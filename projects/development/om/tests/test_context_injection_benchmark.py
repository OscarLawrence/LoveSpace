"""
Comprehensive benchmark suite for context injection quality validation.
Tests semantic similarity, relevance scoring, and output consistency.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

from .benchmark import ContextInjectionBenchmark

# Legacy compatibility imports
from .benchmark.data_models import BenchmarkQuery, BenchmarkResult
from .benchmark.suite import ContextInjectionBenchmark

__all__ = ['BenchmarkQuery', 'BenchmarkResult', 'ContextInjectionBenchmark']


def test_context_injection_benchmark():
    """Test the context injection benchmark suite."""
    if not PYTEST_AVAILABLE:
        return
    
    benchmark = ContextInjectionBenchmark()
    
    try:
        # Run benchmark with small limit for testing
        results = benchmark.run_benchmark(limit=3)
        
        # Generate report
        report = benchmark.generate_report(results)
        
        # Basic validation
        assert len(results) > 0
        assert "summary" in report
        assert "total_tests" in report["summary"]
        
        print(f"Benchmark completed: {report['summary']['total_tests']} tests")
        print(f"Pass rate: {report['summary']['pass_rate']:.2%}")
        
    finally:
        benchmark.close()


if __name__ == "__main__":
    # Run benchmark directly
    benchmark = ContextInjectionBenchmark()
    
    try:
        print("Running context injection benchmark...")
        results = benchmark.run_benchmark(limit=5)
        report = benchmark.generate_report(results)
        benchmark.save_report(report)
        
        print(f"\nBenchmark Results:")
        print(f"Total tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Pass rate: {report['summary']['pass_rate']:.2%}")
        print(f"Average precision: {report['summary']['avg_precision']:.3f}")
        print(f"Average recall: {report['summary']['avg_recall']:.3f}")
        print(f"Average similarity: {report['summary']['avg_similarity']:.3f}")
        
    finally:
        benchmark.close()