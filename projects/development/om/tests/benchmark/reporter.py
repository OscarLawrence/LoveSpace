"""
Benchmark report generation
"""

import json
from typing import Dict, List
from .data_models import BenchmarkResult


class BenchmarkReporter:
    """Generates reports from benchmark results"""
    
    def generate_report(self, results: List[BenchmarkResult]) -> Dict:
        """Generate comprehensive benchmark report."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        
        avg_precision = sum(r.precision for r in results) / total_tests if total_tests > 0 else 0
        avg_recall = sum(r.recall for r in results) / total_tests if total_tests > 0 else 0
        avg_similarity = sum(r.avg_similarity for r in results) / total_tests if total_tests > 0 else 0
        
        # Identify problematic queries
        failed_queries = [r for r in results if not r.passed]
        low_precision_queries = [r for r in results if r.precision < 0.3]
        low_recall_queries = [r for r in results if r.recall < 0.3]
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "avg_precision": avg_precision,
                "avg_recall": avg_recall,
                "avg_similarity": avg_similarity
            },
            "failed_queries": [
                {
                    "query": r.query,
                    "errors": r.errors,
                    "precision": r.precision,
                    "recall": r.recall,
                    "similarity": r.avg_similarity
                }
                for r in failed_queries
            ],
            "quality_issues": {
                "low_precision": [r.query for r in low_precision_queries],
                "low_recall": [r.query for r in low_recall_queries]
            },
            "detailed_results": [
                {
                    "query": r.query,
                    "passed": r.passed,
                    "precision": r.precision,
                    "recall": r.recall,
                    "avg_similarity": r.avg_similarity,
                    "functions_found": r.functions_found,
                    "patterns_found": r.patterns_found,
                    "errors": r.errors
                }
                for r in results
            ]
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str = "context_injection_benchmark_report.json"):
        """Save benchmark report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Benchmark report saved to {output_path}")
