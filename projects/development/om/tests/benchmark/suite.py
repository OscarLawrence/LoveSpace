"""
Main benchmark suite for context injection testing
"""

from typing import Dict, List
from .runner import BenchmarkRunner
from .reporter import BenchmarkReporter
from .data_models import BenchmarkResult


class ContextInjectionBenchmark:
    """Benchmark suite for context injection quality."""
    
    def __init__(self):
        self.runner = BenchmarkRunner()
        self.reporter = BenchmarkReporter()
    
    def run_benchmark(self, limit: int = 5) -> List[BenchmarkResult]:
        """Run complete benchmark suite."""
        return self.runner.run_benchmark(limit)
    
    def generate_report(self, results: List[BenchmarkResult]) -> Dict:
        """Generate comprehensive benchmark report."""
        return self.reporter.generate_report(results)
    
    def save_report(self, report: Dict, output_path: str = "context_injection_benchmark_report.json"):
        """Save benchmark report to file."""
        self.reporter.save_report(report, output_path)
    
    def close(self):
        """Close benchmark resources."""
        self.runner.close()
