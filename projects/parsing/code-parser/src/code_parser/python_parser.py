"""Python AST parser for extracting functions, classes, and patterns."""

import ast
import hashlib
from pathlib import Path
from typing import Iterator, Optional, Union

try:
    from knowledge.db_manager import ContextDB, Function, Class, Pattern
except ImportError:
    # Fallback for development/testing
    ContextDB = Function = Class = Pattern = None


class PythonCodeParser:
    """Parse Python files and extract code elements for knowledge database."""
    
    def __init__(self, db: ContextDB):
        self.db = db
    
    def parse_file(self, file_path: Path) -> dict:
        """Parse a Python file and store elements in knowledge DB.
        
        Returns counts of extracted elements.
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            return {"error": 1, "functions": 0, "classes": 0}
        
        counts = {"functions": 0, "classes": 0, "patterns": 0}
        
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func = self._extract_function(node, file_path, content)
                if func:
                    self.db.add_function(func)
                    counts["functions"] += 1
                    
            elif isinstance(node, ast.ClassDef):
                cls = self._extract_class(node, file_path)
                if cls:
                    self.db.add_class(cls)
                    counts["classes"] += 1
        
        # Extract patterns (common code structures)
        patterns = self._extract_patterns(tree, file_path)
        for pattern in patterns:
            self.db.add_pattern(pattern)
            counts["patterns"] += 1
        
        return counts
    
    def _extract_function(self, node: ast.FunctionDef, file_path: Path, content: str) -> Optional['Function']:
        """Extract function information from AST node."""
        # Get function parameters
        params = []
        for arg in node.args.args:
            param = {"name": arg.arg}
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            params.append(param)
        
        # Get return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # Get docstring
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) 
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        # Generate body hash for change detection
        body_lines = content.split('\n')[node.lineno-1:node.end_lineno]
        body_hash = hashlib.md5('\n'.join(body_lines).encode()).hexdigest()[:8]
        
        return Function(
            name=node.name,
            language="python",
            file_path=str(file_path.relative_to(Path.cwd())),
            line_number=node.lineno,
            params=params,
            return_type=return_type,
            docstring=docstring,
            body_hash=body_hash
        )
    
    def _extract_class(self, node: ast.ClassDef, file_path: Path) -> Optional['Class']:
        """Extract class information from AST node."""
        # Get methods
        methods = []
        properties = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                properties.append(item.target.id)
        
        # Get docstring
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) 
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        return Class(
            name=node.name,
            language="python",
            file_path=str(file_path.relative_to(Path.cwd())),
            line_number=node.lineno,
            methods=methods,
            properties=properties,
            docstring=docstring
        )
    
    def _extract_patterns(self, tree: ast.AST, file_path: Path) -> list:
        """Extract common code patterns from AST."""
        patterns = []
        
        # Pattern: CLI with Click
        if self._has_click_pattern(tree):
            patterns.append(Pattern(
                name="click_cli",
                language="python",
                pattern_type="cli",
                code_snippet="@click.command()\ndef command():\n    pass",
                usage_context="CLI command definition with Click",
                dependencies=["click"]
            ))
        
        # Pattern: DuckDB usage
        if self._has_duckdb_pattern(tree):
            patterns.append(Pattern(
                name="duckdb_query",
                language="python", 
                pattern_type="database",
                code_snippet="conn = duckdb.connect()\nresult = conn.execute(query).fetchall()",
                usage_context="DuckDB database operations",
                dependencies=["duckdb"]
            ))
        
        return patterns
    
    def _has_click_pattern(self, tree: ast.AST) -> bool:
        """Check if file uses Click decorators."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if (isinstance(decorator.value, ast.Name) 
                            and decorator.value.id == "click"):
                            return True
        return False
    
    def _has_duckdb_pattern(self, tree: ast.AST) -> bool:
        """Check if file uses DuckDB."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "duckdb":
                        return True
            elif isinstance(node, ast.ImportFrom):
                if node.module == "duckdb":
                    return True
        return False


class WorkspaceParser:
    """Parse entire workspace and populate knowledge database."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db = ContextDB(db_path)
        self.python_parser = PythonCodeParser(self.db)
    
    def parse_workspace(self, root_path: Path = None) -> dict[str, int]:
        """Parse all Python files in workspace."""
        if root_path is None:
            root_path = Path.cwd()
        
        total_counts = {"files": 0, "functions": 0, "classes": 0, "patterns": 0, "errors": 0}
        
        # Find all Python files
        python_files = list(root_path.rglob("*.py"))
        
        # Filter out common exclusions
        excluded_patterns = {".venv", "__pycache__", ".git", "build", "dist", ".pytest_cache"}
        python_files = [
            f for f in python_files 
            if not any(pattern in str(f) for pattern in excluded_patterns)
        ]
        
        for file_path in python_files:
            counts = self.python_parser.parse_file(file_path)
            total_counts["files"] += 1
            
            for key in ["functions", "classes", "patterns"]:
                if key in counts:
                    total_counts[key] += counts[key]
            
            if "error" in counts:
                total_counts["errors"] += counts["error"]
        
        return total_counts
    
    def close(self) -> None:
        """Close database connection."""
        self.db.close()