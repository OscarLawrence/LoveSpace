"""
Code Quality Analysis Engine
"""

import os
import ast
from typing import Dict, List, Tuple
from .quality_metrics import *


class CodeAnalyzer:
    def __init__(self):
        self.complexity_thresholds = {
            'function': 10,
            'class': 20,
            'file': 200
        }
    
    def analyze_file(self, file_path: str) -> FileQualityMetric:
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return FileQualityMetric(file_path, 0, 0, 0, 0.0, 0.0, 0.0)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return FileQualityMetric(file_path, 0, 0, 0, 100.0, 0.0, 0.0)
        
        line_count = len(content.splitlines())
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        complexity_score = self._calculate_file_complexity(tree)
        documentation_ratio = self._calculate_documentation_ratio(content)
        
        return FileQualityMetric(
            file_path=file_path,
            line_count=line_count,
            function_count=len(functions),
            class_count=len(classes),
            complexity_score=complexity_score,
            documentation_ratio=documentation_ratio,
            test_coverage=0.0
        )
    
    def analyze_function_complexity(self, file_path: str) -> List[CodeComplexityMetric]:
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        complexity_metrics = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_function_complexity(node)
                line_count = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 1
                param_count = len(node.args.args)
                nesting_depth = self._calculate_nesting_depth(node)
                
                complexity_metrics.append(CodeComplexityMetric(
                    file_path=file_path,
                    function_name=node.name,
                    complexity_score=complexity,
                    line_count=line_count,
                    parameter_count=param_count,
                    nesting_depth=nesting_depth
                ))
        
        return complexity_metrics
    
    def _calculate_file_complexity(self, tree: ast.AST) -> float:
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        complexity = 1
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_nesting_depth(self, func_node: ast.FunctionDef) -> int:
        max_depth = 0
        
        def calculate_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                current_depth += 1
            
            for child in ast.iter_child_nodes(node):
                calculate_depth(child, current_depth)
        
        calculate_depth(func_node)
        return max_depth
    
    def _calculate_documentation_ratio(self, content: str) -> float:
        lines = content.splitlines()
        doc_lines = 0
        code_lines = 0
        
        in_docstring = False
        docstring_delimiter = None
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                continue
            
            if stripped.startswith('#'):
                doc_lines += 1
            elif '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                    docstring_delimiter = '"""' if '"""' in stripped else "'''"
                    doc_lines += 1
                elif docstring_delimiter in stripped:
                    in_docstring = False
                    doc_lines += 1
                else:
                    doc_lines += 1
            elif in_docstring:
                doc_lines += 1
            else:
                code_lines += 1
        
        total_lines = doc_lines + code_lines
        return doc_lines / total_lines if total_lines > 0 else 0.0
    
    def get_file_size_violations(self, directory: str = ".") -> List[str]:
        violations = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            line_count = len(f.readlines())
                        
                        if line_count > self.complexity_thresholds['file']:
                            violations.append(f"{file_path} ({line_count} lines)")
                    except Exception:
                        continue
        
        return violations
    
    def get_complexity_violations(self, directory: str = ".") -> List[str]:
        violations = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    complexity_metrics = self.analyze_function_complexity(file_path)
                    
                    for metric in complexity_metrics:
                        if metric.complexity_score > self.complexity_thresholds['function']:
                            violations.append(f"{file_path}:{metric.function_name} (complexity: {metric.complexity_score})")
        
        return violations