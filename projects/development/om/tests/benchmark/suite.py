"""
Main benchmark suite for context injection testing
"""

from .data_models import BenchmarkResult
from .reporter import BenchmarkReporter
from .runner import BenchmarkRunner


class ContextInjectionBenchmark:
    """Benchmark suite for context injection quality."""

    def __init__(self):
        self.runner = BenchmarkRunner()
        self.reporter = BenchmarkReporter()

    def run_benchmark(self, limit: int = 5) -> list[BenchmarkResult]:
        """Run complete benchmark suite."""
        return self.runner.run_benchmark(limit)

    def generate_report(self, results: list[BenchmarkResult]) -> dict:
        """Generate comprehensive benchmark report."""
        return self.reporter.generate_report(results)

    def save_report(
        self, report: dict, output_path: str = "context_injection_benchmark_report.json"
    ):
        """Save benchmark report to file."""
        self.reporter.save_report(report, output_path)

    def close(self):
        """Close benchmark resources."""
        self.runner.close()
