"""Code analysis for documentation generation."""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class CodeElement:
    """Represents a documented code element."""
    name: str
    type: str  # 'module', 'class', 'function', 'method', 'attribute'
    signature: str
    source_file: Path
    line_number: int
    docstring: Optional[str] = None
    annotations: Dict[str, str] = None
    complexity: int = 0
    dependencies: List[str] = None
    examples: List[str] = None
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.examples is None:
            self.examples = []


class CodeAnalyzer:
    """Analyzes Python code to extract documentation elements."""
    
    def __init__(self):
        self.elements: Dict[str, CodeElement] = {}
        self.type_hints: Dict[str, str] = {}
        self.imports: Dict[str, Set[str]] = {}
    
    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze a Python file and extract code elements."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            elements = []
            
            # Extract module-level info
            module_element = self._create_module_element(file_path, tree, source)
            elements.append(module_element)
            
            # Walk AST to find all elements
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    elements.append(self._analyze_class(node, file_path, source))
                elif isinstance(node, ast.FunctionDef):
                    elements.append(self._analyze_function(node, file_path, source))
                elif isinstance(node, ast.AsyncFunctionDef):
                    elements.append(self._analyze_async_function(node, file_path, source))
            
            return elements
            
        except Exception as e:
            # Return minimal element on parse error
            return [CodeElement(
                name=file_path.stem,
                type='module',
                signature=f"module {file_path.stem}",
                source_file=file_path,
                line_number=1,
                docstring=f"Parse error: {e}"
            )]
    
    def _create_module_element(self, file_path: Path, tree: ast.AST, source: str) -> CodeElement:
        """Create module-level documentation element."""
        docstring = ast.get_docstring(tree)
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend([f"{module}.{alias.name}" for alias in node.names])
        
        # Calculate module complexity
        complexity = self._calculate_complexity(tree)
        
        return CodeElement(
            name=file_path.stem,
            type='module',
            signature=f"module {file_path.stem}",
            source_file=file_path,
            line_number=1,
            docstring=docstring or f"Module: {file_path.stem}",
            complexity=complexity,
            dependencies=imports
        )
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path, source: str) -> CodeElement:
        """Analyze a class definition."""
        signature = self._get_class_signature(node)
        docstring = ast.get_docstring(node)
        
        # Extract methods and attributes
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return CodeElement(
            name=node.name,
            type='class',
            signature=signature,
            source_file=file_path,
            line_number=node.lineno,
            docstring=docstring or f"Class: {node.name}",
            complexity=self._calculate_complexity(node),
            dependencies=methods + attributes
        )
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, source: str) -> CodeElement:
        """Analyze a function definition."""
        signature = self._get_function_signature(node)
        docstring = ast.get_docstring(node)
        
        # Extract function dependencies
        dependencies = self._extract_function_dependencies(node)
        
        return CodeElement(
            name=node.name,
            type='function',
            signature=signature,
            source_file=file_path,
            line_number=node.lineno,
            docstring=docstring or f"Function: {node.name}",
            complexity=self._calculate_complexity(node),
            dependencies=dependencies,
            annotations=self._extract_annotations(node)
        )
    
    def _analyze_async_function(self, node: ast.AsyncFunctionDef, file_path: Path, source: str) -> CodeElement:
        """Analyze an async function definition."""
        signature = f"async {self._get_function_signature(node)}"
        docstring = ast.get_docstring(node)
        
        dependencies = self._extract_function_dependencies(node)
        
        return CodeElement(
            name=node.name,
            type='async_function',
            signature=signature,
            source_file=file_path,
            line_number=node.lineno,
            docstring=docstring or f"Async function: {node.name}",
            complexity=self._calculate_complexity(node),
            dependencies=dependencies,
            annotations=self._extract_annotations(node)
        )
    
    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Generate class signature."""
        bases = []
        if node.bases:
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(f"{base.value.id}.{base.attr}")
        
        base_str = f"({', '.join(bases)})" if bases else ""
        return f"class {node.name}{base_str}"
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Generate function signature."""
        args = []
        
        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Default arguments
        defaults = node.args.defaults
        if defaults:
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                arg_index = len(args) - num_defaults + i
                if arg_index >= 0:
                    args[arg_index] += f" = {ast.unparse(default)}"
        
        # Keyword-only arguments
        for arg in node.args.kwonlyargs:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Return annotation
        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {ast.unparse(node.returns)}"
        
        return f"def {node.name}({', '.join(args)}){return_annotation}"
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, 
                                ast.Try, ast.ExceptHandler, ast.AsyncWith, ast.AsyncFor)):
                complexity += 1
        return complexity
    
    def _extract_function_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract function call dependencies."""
        dependencies = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.append(child.func.attr)
        return list(set(dependencies))
    
    def _extract_annotations(self, node: ast.FunctionDef) -> Dict[str, str]:
        """Extract type annotations."""
        annotations = {}
        
        # Argument annotations
        for arg in node.args.args:
            if arg.annotation:
                annotations[arg.arg] = ast.unparse(arg.annotation)
        
        # Return annotation
        if node.returns:
            annotations['return'] = ast.unparse(node.returns)
        
        return annotations