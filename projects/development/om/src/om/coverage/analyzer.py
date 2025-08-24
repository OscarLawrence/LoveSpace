"""
Documentation coverage analyzer
"""

import ast
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import asdict

from .data_models import CoverageMetrics, QualityIssue


class CoverageAnalyzer:
    """Analyzes documentation coverage across codebase."""
    
    def __init__(self):
        self.coverage_rules = {
            'require_module_docs': True,
            'require_class_docs': True,
            'require_public_method_docs': True,
            'require_function_docs': True,
            'allow_private_undocumented': True,
            'min_docstring_length': 10,
            'require_parameter_docs': True,
            'require_return_docs': True,
            'max_complexity_without_docs': 5,
            'quality_threshold': 7.0,
            'max_issues_per_file': 10
        }
    
    def analyze_coverage(self, source_dir: Path, patterns: List[str] = None) -> CoverageMetrics:
        """Analyze documentation coverage for source directory."""
        if patterns is None:
            patterns = ['**/*.py']
        
        all_issues = []
        total_elements = 0
        documented_elements = 0
        missing_docs = []
        
        # Find all Python files
        python_files = []
        for pattern in patterns:
            python_files.extend(source_dir.glob(pattern))
        
        # Analyze each file
        for file_path in python_files:
            try:
                file_metrics = self._analyze_file_coverage(file_path)
                total_elements += file_metrics['total']
                documented_elements += file_metrics['documented']
                missing_docs.extend(file_metrics['missing'])
                all_issues.extend(file_metrics['issues'])
            except Exception as e:
                all_issues.append(QualityIssue(
                    element_name=file_path.name,
                    element_type='file',
                    issue_type='parse_error',
                    severity='error',
                    description=f"Failed to parse file: {e}",
                    file_path=str(file_path),
                    line_number=1
                ))
        
        # Calculate metrics
        coverage_percentage = (documented_elements / total_elements * 100) if total_elements > 0 else 0
        quality_score = self._calculate_quality_score(all_issues, total_elements)
        
        return CoverageMetrics(
            total_elements=total_elements,
            documented_elements=documented_elements,
            coverage_percentage=coverage_percentage,
            missing_docs=missing_docs,
            quality_score=quality_score,
            issues=[asdict(issue) for issue in all_issues]
        )
    
    def _analyze_file_coverage(self, file_path: Path) -> Dict[str, Any]:
        """Analyze documentation coverage for single file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        
        total = 0
        documented = 0
        missing = []
        issues = []
        
        # Check module-level documentation
        module_doc = ast.get_docstring(tree)
        total += 1
        if module_doc and len(module_doc.strip()) >= self.coverage_rules['min_docstring_length']:
            documented += 1
        else:
            missing.append(f"{file_path.name}:module")
            if self.coverage_rules['require_module_docs']:
                issues.append(QualityIssue(
                    element_name=file_path.stem,
                    element_type='module',
                    issue_type='missing_documentation',
                    severity='warning',
                    description='Module lacks documentation',
                    file_path=str(file_path),
                    line_number=1
                ))
        
        # Analyze classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_metrics = self._analyze_class_coverage(node, file_path)
                total += class_metrics['total']
                documented += class_metrics['documented']
                missing.extend(class_metrics['missing'])
                issues.extend(class_metrics['issues'])
            
            elif isinstance(node, ast.FunctionDef):
                # Skip nested functions
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                          if any(child is node for child in ast.walk(parent))):
                    func_metrics = self._analyze_function_coverage(node, file_path)
                    total += func_metrics['total']
                    documented += func_metrics['documented']
                    missing.extend(func_metrics['missing'])
                    issues.extend(func_metrics['issues'])
        
        return {
            'total': total,
            'documented': documented,
            'missing': missing,
            'issues': issues
        }
    
    def _analyze_class_coverage(self, node: ast.ClassDef, file_path: Path) -> Dict[str, Any]:
        """Analyze class documentation coverage."""
        total = 1  # Count the class itself
        documented = 0
        missing = []
        issues = []
        
        # Check class docstring
        class_doc = ast.get_docstring(node)
        if class_doc and len(class_doc.strip()) >= self.coverage_rules['min_docstring_length']:
            documented += 1
        else:
            missing.append(f"{file_path.name}:{node.name}")
            if self.coverage_rules['require_class_docs']:
                issues.append(QualityIssue(
                    element_name=node.name,
                    element_type='class',
                    issue_type='missing_documentation',
                    severity='warning',
                    description='Class lacks documentation',
                    file_path=str(file_path),
                    line_number=node.lineno
                ))
        
        # Analyze methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_metrics = self._analyze_function_coverage(item, file_path, is_method=True)
                total += method_metrics['total']
                documented += method_metrics['documented']
                missing.extend(method_metrics['missing'])
                issues.extend(method_metrics['issues'])
        
        return {
            'total': total,
            'documented': documented,
            'missing': missing,
            'issues': issues
        }
    
    def _analyze_function_coverage(self, node: ast.FunctionDef, file_path: Path, is_method: bool = False) -> Dict[str, Any]:
        """Analyze function/method documentation coverage."""
        total = 1
        documented = 0
        missing = []
        issues = []
        
        # Skip private functions if allowed
        if (node.name.startswith('_') and not node.name.startswith('__') and 
            self.coverage_rules['allow_private_undocumented']):
            return {'total': 0, 'documented': 0, 'missing': [], 'issues': []}
        
        # Check function docstring
        func_doc = ast.get_docstring(node)
        if func_doc and len(func_doc.strip()) >= self.coverage_rules['min_docstring_length']:
            documented += 1
        else:
            element_name = f"{node.name}" if not is_method else f"method:{node.name}"
            missing.append(f"{file_path.name}:{element_name}")
            
            required = (self.coverage_rules['require_function_docs'] or 
                       (is_method and self.coverage_rules['require_public_method_docs']))
            
            if required:
                issues.append(QualityIssue(
                    element_name=node.name,
                    element_type='method' if is_method else 'function',
                    issue_type='missing_documentation',
                    severity='warning',
                    description=f"{'Method' if is_method else 'Function'} lacks documentation",
                    file_path=str(file_path),
                    line_number=node.lineno
                ))
        
        return {
            'total': total,
            'documented': documented,
            'missing': missing,
            'issues': issues
        }
    
    def _calculate_quality_score(self, issues: List[QualityIssue], total_elements: int) -> float:
        """Calculate overall quality score."""
        if total_elements == 0:
            return 10.0
        
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        
        # Penalty system: errors are worth more penalty than warnings
        penalty = (error_count * 2.0 + warning_count * 0.5) / total_elements
        score = max(0.0, 10.0 - penalty * 10.0)
        
        return round(score, 1)
