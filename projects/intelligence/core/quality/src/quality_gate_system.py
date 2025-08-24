"""
Quality Gate System
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from .quality_metrics import *
from .code_analyzer import CodeAnalyzer


class QualityGateSystem:
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.quality_standards = {
            'max_file_lines': 200,
            'max_function_complexity': 10,
            'min_documentation_ratio': 0.2,
            'max_function_parameters': 5,
            'max_nesting_depth': 4
        }
    
    def run_all_quality_gates(self, target_directory: str = ".") -> List[QualityGateResult]:
        results = []
        
        results.append(self.file_size_gate(target_directory))
        results.append(self.complexity_gate(target_directory))
        results.append(self.documentation_gate(target_directory))
        results.append(self.structure_gate(target_directory))
        
        return results
    
    def file_size_gate(self, directory: str = ".") -> QualityGateResult:
        violations = self.code_analyzer.get_file_size_violations(directory)
        
        total_files = self._count_python_files(directory)
        violation_count = len(violations)
        
        score = max(0.0, (total_files - violation_count) / total_files) if total_files > 0 else 1.0
        passed = violation_count == 0
        
        metrics = [
            QualityMetric(
                name="file_size_compliance",
                value=score,
                threshold=1.0,
                status="pass" if passed else "fail",
                description=f"{violation_count} files exceed {self.quality_standards['max_file_lines']} lines"
            )
        ]
        
        recommendations = []
        if violation_count > 0:
            recommendations.append(f"Refactor {violation_count} large files into smaller modules")
            recommendations.append("Consider extracting classes or functions into separate files")
        
        return QualityGateResult(
            gate_name="File Size Gate",
            passed=passed,
            score=score,
            metrics=metrics,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def complexity_gate(self, directory: str = ".") -> QualityGateResult:
        violations = self.code_analyzer.get_complexity_violations(directory)
        
        total_functions = self._count_functions(directory)
        violation_count = len(violations)
        
        score = max(0.0, (total_functions - violation_count) / total_functions) if total_functions > 0 else 1.0
        passed = violation_count == 0
        
        metrics = [
            QualityMetric(
                name="complexity_compliance",
                value=score,
                threshold=1.0,
                status="pass" if passed else "fail",
                description=f"{violation_count} functions exceed complexity threshold"
            )
        ]
        
        recommendations = []
        if violation_count > 0:
            recommendations.append("Refactor complex functions into smaller, focused functions")
            recommendations.append("Consider using design patterns to reduce complexity")
        
        return QualityGateResult(
            gate_name="Complexity Gate",
            passed=passed,
            score=score,
            metrics=metrics,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def documentation_gate(self, directory: str = ".") -> QualityGateResult:
        total_ratio = 0.0
        file_count = 0
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_metric = self.code_analyzer.analyze_file(file_path)
                    total_ratio += file_metric.documentation_ratio
                    file_count += 1
        
        avg_documentation_ratio = total_ratio / file_count if file_count > 0 else 0.0
        passed = avg_documentation_ratio >= self.quality_standards['min_documentation_ratio']
        
        metrics = [
            QualityMetric(
                name="documentation_ratio",
                value=avg_documentation_ratio,
                threshold=self.quality_standards['min_documentation_ratio'],
                status="pass" if passed else "warn",
                description=f"Average documentation ratio: {avg_documentation_ratio:.2f}"
            )
        ]
        
        recommendations = []
        if not passed:
            recommendations.append("Add more docstrings and comments to improve documentation")
            recommendations.append("Focus on documenting complex functions and classes")
        
        return QualityGateResult(
            gate_name="Documentation Gate",
            passed=passed,
            score=avg_documentation_ratio,
            metrics=metrics,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def structure_gate(self, directory: str = ".") -> QualityGateResult:
        violations = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    complexity_metrics = self.code_analyzer.analyze_function_complexity(file_path)
                    
                    for metric in complexity_metrics:
                        if metric.parameter_count > self.quality_standards['max_function_parameters']:
                            violations.append(f"{file_path}:{metric.function_name} has {metric.parameter_count} parameters")
                        
                        if metric.nesting_depth > self.quality_standards['max_nesting_depth']:
                            violations.append(f"{file_path}:{metric.function_name} has nesting depth {metric.nesting_depth}")
        
        total_functions = self._count_functions(directory)
        violation_count = len(violations)
        
        score = max(0.0, (total_functions - violation_count) / total_functions) if total_functions > 0 else 1.0
        passed = violation_count == 0
        
        metrics = [
            QualityMetric(
                name="structure_compliance",
                value=score,
                threshold=1.0,
                status="pass" if passed else "warn",
                description=f"{violation_count} structure violations found"
            )
        ]
        
        recommendations = []
        if violation_count > 0:
            recommendations.append("Reduce function parameter counts by using data classes or configuration objects")
            recommendations.append("Reduce nesting depth by extracting nested logic into separate functions")
        
        return QualityGateResult(
            gate_name="Structure Gate",
            passed=passed,
            score=score,
            metrics=metrics,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def _count_python_files(self, directory: str) -> int:
        count = 0
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            count += len([f for f in files if f.endswith('.py')])
        return count
    
    def _count_functions(self, directory: str) -> int:
        count = 0
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_metric = self.code_analyzer.analyze_file(file_path)
                    count += file_metric.function_count
        return count
    
    def generate_quality_report(self, directory: str = ".") -> Dict:
        results = self.run_all_quality_gates(directory)
        
        total_score = sum(result.score for result in results) / len(results) if results else 0.0
        passed_gates = sum(1 for result in results if result.passed)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": total_score,
            "gates_passed": passed_gates,
            "total_gates": len(results),
            "passed": passed_gates == len(results),
            "gate_results": [
                {
                    "name": result.gate_name,
                    "passed": result.passed,
                    "score": result.score,
                    "recommendations": result.recommendations
                }
                for result in results
            ]
        }
        
        return report
    
    def save_quality_report(self, directory: str = ".", output_file: str = "quality_report.json"):
        report = self.generate_quality_report(directory)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_file