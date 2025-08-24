#!/usr/bin/env python3
"""
Standalone benchmark runner for context injection quality validation.
Run with: python benchmark_runner.py
"""

import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_context_injection_benchmark import ContextInjectionBenchmark


def main():
    """Run comprehensive context injection benchmarks."""
    print("🔍 Context Injection Quality Benchmark Suite")
    print("=" * 50)
    
    # Initialize benchmark
    try:
        benchmark = ContextInjectionBenchmark()
        print("✅ Benchmark suite initialized")
    except Exception as e:
        print(f"❌ Failed to initialize benchmark: {e}")
        return 1
    
    # Run benchmarks
    print("\n🚀 Running benchmark queries...")
    try:
        results = benchmark.run_benchmark(limit=5)
        print(f"✅ Completed {len(results)} benchmark tests")
    except Exception as e:
        print(f"❌ Benchmark execution failed: {e}")
        benchmark.close()
        return 1
    
    # Generate report
    print("\n📊 Analyzing results...")
    report = benchmark.generate_report(results)
    
    # Display summary
    summary = report['summary']
    print(f"\n📈 BENCHMARK RESULTS")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']} ✅")
    print(f"   Failed: {summary['failed']} ❌")
    print(f"   Pass Rate: {summary['pass_rate']:.1%}")
    print(f"   Average Precision: {summary['avg_precision']:.3f}")
    print(f"   Average Recall: {summary['avg_recall']:.3f}")
    print(f"   Average Similarity: {summary['avg_similarity']:.3f}")
    
    # Quality thresholds
    quality_issues = []
    if summary['pass_rate'] < 0.8:
        quality_issues.append(f"Low pass rate: {summary['pass_rate']:.1%} (target: ≥80%)")
    if summary['avg_precision'] < 0.6:
        quality_issues.append(f"Low precision: {summary['avg_precision']:.3f} (target: ≥0.6)")
    if summary['avg_recall'] < 0.4:
        quality_issues.append(f"Low recall: {summary['avg_recall']:.3f} (target: ≥0.4)")
    
    # Display failed queries
    if report['failed_queries']:
        print(f"\n❌ FAILED QUERIES ({len(report['failed_queries'])})")
        for i, failed in enumerate(report['failed_queries'][:5], 1):  # Show first 5
            print(f"   {i}. '{failed['query']}'")
            print(f"      Precision: {failed['precision']:.3f}, Recall: {failed['recall']:.3f}")
            if failed['errors']:
                print(f"      Errors: {', '.join(failed['errors'])}")
    
    # Display quality issues
    if report['quality_issues']['low_precision']:
        print(f"\n⚠️  LOW PRECISION QUERIES ({len(report['quality_issues']['low_precision'])})")
        for query in report['quality_issues']['low_precision'][:3]:
            print(f"   - '{query}'")
    
    if report['quality_issues']['low_recall']:
        print(f"\n⚠️  LOW RECALL QUERIES ({len(report['quality_issues']['low_recall'])})")
        for query in report['quality_issues']['low_recall'][:3]:
            print(f"   - '{query}'")
    
    # Save detailed report
    report_path = "context_injection_benchmark_report.json"
    benchmark.save_report(report, report_path)
    print(f"\n📄 Detailed report saved: {report_path}")
    
    # Overall assessment
    print(f"\n🎯 QUALITY ASSESSMENT")
    if quality_issues:
        print("❌ QUALITY ISSUES DETECTED:")
        for issue in quality_issues:
            print(f"   - {issue}")
        print("\n🔧 RECOMMENDATIONS:")
        if summary['avg_precision'] < 0.6:
            print("   - Improve embedding model or function/pattern descriptions")
            print("   - Add more specific patterns to knowledge base")
        if summary['avg_recall'] < 0.4:
            print("   - Expand knowledge base with more diverse functions")
            print("   - Improve query preprocessing and expansion")
        if summary['pass_rate'] < 0.8:
            print("   - Review failed test cases and adjust similarity thresholds")
            print("   - Add more training data for underperforming domains")
    else:
        print("✅ QUALITY BENCHMARKS PASSED")
        print("   Context injection system meets quality standards")
    
    # Return appropriate exit code
    benchmark.close()
    return 0 if not quality_issues else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)