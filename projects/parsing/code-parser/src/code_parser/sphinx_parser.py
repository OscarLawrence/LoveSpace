"""Sphinx-based Python code parser for enhanced documentation extraction."""

import ast
import importlib.util
import inspect
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter, FunctionDocumenter
from sphinx.util.docutils import docutils_namespace

from knowledge.db_manager import ContextDB, Function, Class, Pattern


class SphinxCodeParser:
    """Enhanced parser using Sphinx autodoc for comprehensive documentation extraction."""
    
    def __init__(self, db: ContextDB):
        self.db = db
        self._temp_dir = None
        self._sphinx_app = None
    
    def _setup_sphinx(self, source_dir: Path) -> Sphinx:
        """Setup Sphinx application for documentation extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create minimal conf.py
            conf_content = '''
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx_autodoc_typehints']
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': True,
    'inherited-members': True,
    'show-inheritance': True,
}
'''
            (temp_path / 'conf.py').write_text(conf_content)
            
            return Sphinx(
                srcdir=str(temp_path),
                confdir=str(temp_path),
                outdir=str(temp_path / '_build'),
                doctreedir=str(temp_path / '_doctrees'),
                buildername='html',
                verbosity=0,
                warning=None,
            )
    
    def parse_file(self, file_path: Path) -> Dict[str, int]:
        """Parse Python file using Sphinx autodoc for enhanced extraction."""
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if not spec or not spec.loader:
                return {"error": 1, "functions": 0, "classes": 0}
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["temp_module"] = module
            spec.loader.exec_module(module)
            
            counts = {"functions": 0, "classes": 0, "patterns": 0}
            
            # Extract functions with Sphinx-enhanced documentation
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if obj.__module__ == module.__name__:
                    func = self._extract_function_with_sphinx(obj, name, file_path)
                    if func:
                        self.db.add_function(func)
                        counts["functions"] += 1
            
            # Extract classes with Sphinx-enhanced documentation
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__:
                    cls = self._extract_class_with_sphinx(obj, name, file_path)
                    if cls:
                        self.db.add_class(cls)
                        counts["classes"] += 1
            
            # Extract patterns using AST analysis
            content = file_path.read_text()
            tree = ast.parse(content)
            patterns = self._extract_enhanced_patterns(tree, file_path, module)
            for pattern in patterns:
                self.db.add_pattern(pattern)
                counts["patterns"] += 1
            
            # Clean up
            if "temp_module" in sys.modules:
                del sys.modules["temp_module"]
            
            return counts
            
        except Exception as e:
            return {"error": 1, "functions": 0, "classes": 0}
    
    def _extract_function_with_sphinx(self, func_obj: Any, name: str, file_path: Path) -> Optional[Function]:
        """Extract function with enhanced documentation using Sphinx."""
        try:
            # Get signature with type hints
            sig = inspect.signature(func_obj)
            
            # Extract docstring with Sphinx processing
            docstring = inspect.getdoc(func_obj) or ""
            
            # Parse parameters with types
            params = []
            for param_name, param in sig.parameters.items():
                param_type = str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
                param_default = str(param.default) if param.default != inspect.Parameter.empty else None
                params.append(f"{param_name}: {param_type}" + (f" = {param_default}" if param_default else ""))
            
            # Get return type
            return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "Any"
            
            # Extract decorators by parsing source
            try:
                source_lines = inspect.getsourcelines(func_obj)[0]
                decorators = []
                for line in source_lines:
                    stripped = line.strip()
                    if stripped.startswith('@'):
                        decorators.append(stripped)
                    elif stripped.startswith('def '):
                        break
            except (OSError, TypeError):
                decorators = []
            
            # Create enhanced function description
            enhanced_desc = f"function:{name}|params:{','.join(params)}|returns:{return_type}|decorators:{','.join(decorators)}"
            
            return Function(
                name=name,
                file_path=str(file_path),
                line_number=func_obj.__code__.co_firstlineno if hasattr(func_obj, '__code__') else 0,
                signature=str(sig),
                docstring=docstring,
                description=enhanced_desc,
                domain=self._classify_function_domain(name, docstring, decorators),
                complexity=self._calculate_function_complexity(func_obj),
                dependencies=self._extract_function_dependencies(func_obj)
            )
            
        except Exception:
            return None
    
    def _extract_class_with_sphinx(self, cls_obj: Any, name: str, file_path: Path) -> Optional[Class]:
        """Extract class with enhanced documentation using Sphinx."""
        try:
            # Get class hierarchy
            mro = [cls.__name__ for cls in cls_obj.__mro__[1:] if cls.__name__ != 'object']
            
            # Extract methods with signatures
            methods = []
            for method_name, method_obj in inspect.getmembers(cls_obj, inspect.isfunction):
                try:
                    sig = inspect.signature(method_obj)
                    methods.append(f"{method_name}{sig}")
                except (ValueError, TypeError):
                    methods.append(method_name)
            
            # Extract class docstring
            docstring = inspect.getdoc(cls_obj) or ""
            
            # Enhanced class description
            enhanced_desc = f"class:{name}|inherits:{','.join(mro)}|methods:{len(methods)}|public_methods:{len([m for m in methods if not m.startswith('_')])}"
            
            return Class(
                name=name,
                file_path=str(file_path),
                line_number=0,  # Would need AST to get accurate line number
                docstring=docstring,
                methods=[m.split('(')[0] for m in methods],
                inheritance=mro,
                description=enhanced_desc,
                domain=self._classify_class_domain(name, docstring, methods),
                interface_complexity=len(methods)
            )
            
        except Exception:
            return None
    
    def _extract_enhanced_patterns(self, tree: ast.AST, file_path: Path, module: Any) -> List[Pattern]:
        """Extract code patterns with enhanced context from Sphinx analysis."""
        patterns = []
        
        # Decorator patterns
        decorator_usage = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorator_usage[decorator.id] = decorator_usage.get(decorator.id, 0) + 1
        
        for decorator, count in decorator_usage.items():
            if count >= 2:  # Multiple uses indicate a pattern
                patterns.append(Pattern(
                    name=f"decorator_{decorator}_pattern",
                    description=f"decorator:{decorator}|usage_count:{count}|pattern_type:decorator",
                    code_example=f"@{decorator}",
                    domain="decorators",
                    complexity="low",
                    file_path=str(file_path)
                ))
        
        # Error handling patterns
        try_except_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Try)])
        if try_except_count > 0:
            patterns.append(Pattern(
                name="error_handling_pattern",
                description=f"error_handling|try_blocks:{try_except_count}|pattern_type:exception_handling",
                code_example="try: ... except Exception: ...",
                domain="error_handling",
                complexity="medium",
                file_path=str(file_path)
            ))
        
        # Async patterns
        async_functions = len([node for node in ast.walk(tree) 
                              if isinstance(node, ast.AsyncFunctionDef)])
        if async_functions > 0:
            patterns.append(Pattern(
                name="async_pattern",
                description=f"async|async_functions:{async_functions}|pattern_type:concurrency",
                code_example="async def func(): await ...",
                domain="async",
                complexity="high",
                file_path=str(file_path)
            ))
        
        return patterns
    
    def _classify_function_domain(self, name: str, docstring: str, decorators: List[str]) -> str:
        """Classify function domain based on enhanced context."""
        # API endpoints
        if any('@app.route' in d or '@api.' in d for d in decorators):
            return "api"
        
        # Testing
        if name.startswith('test_') or 'pytest' in docstring.lower():
            return "testing"
        
        # Database operations
        if any(keyword in name.lower() for keyword in ['save', 'load', 'create', 'update', 'delete', 'query']):
            return "database"
        
        # Async operations
        if any('@async' in d for d in decorators) or 'async' in name:
            return "async"
        
        # Validation
        if 'valid' in name.lower() or 'check' in name.lower():
            return "validation"
        
        return "general"
    
    def _classify_class_domain(self, name: str, docstring: str, methods: List[str]) -> str:
        """Classify class domain based on methods and context."""
        method_names = ' '.join(methods).lower()
        
        if any(keyword in method_names for keyword in ['save', 'load', 'create', 'update', 'delete']):
            return "model"
        elif any(keyword in method_names for keyword in ['get', 'post', 'put', 'delete', 'route']):
            return "api"
        elif any(keyword in method_names for keyword in ['test', 'setup', 'teardown']):
            return "testing"
        elif any(keyword in method_names for keyword in ['parse', 'extract', 'analyze']):
            return "parser"
        
        return "general"
    
    def _calculate_function_complexity(self, func_obj: Any) -> str:
        """Calculate function complexity based on code metrics."""
        try:
            source = inspect.getsource(func_obj)
            
            # Simple heuristics
            lines = len(source.split('\n'))
            if lines < 10:
                return "low"
            elif lines < 30:
                return "medium"
            else:
                return "high"
        except (OSError, TypeError):
            return "unknown"
    
    def _extract_function_dependencies(self, func_obj: Any) -> List[str]:
        """Extract function dependencies from imports and calls."""
        try:
            # This would require more sophisticated AST analysis
            # For now, return empty list
            return []
        except Exception:
            return []


def create_enhanced_parser(db: ContextDB) -> SphinxCodeParser:
    """Factory function to create enhanced Sphinx parser."""
    return SphinxCodeParser(db)