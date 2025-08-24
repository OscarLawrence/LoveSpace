"""AST and code analysis patterns."""

from typing import List
from ..db_manager import Pattern


def get_ast_patterns() -> List[Pattern]:
    """Get AST-related patterns."""
    return [
        Pattern(
            name="ast_visitor_pattern",
            language="python",
            pattern_type="ast",
            code_snippet="""
class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'args': [arg.arg for arg in node.args.args]
        })
        self.generic_visit(node)
""",
            usage_context="AST traversal for code analysis and extraction",
            dependencies=["ast"],
            success_count=35
        ),
        Pattern(
            name="ast_transformer_pattern",
            language="python",
            pattern_type="ast",
            code_snippet="""
class CodeTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Add logging to every function
        log_call = ast.parse('logger.info(f"Calling {}")'.format(node.name)).body[0]
        node.body.insert(0, log_call)
        return node
""",
            usage_context="AST transformation for code modification",
            dependencies=["ast"],
            success_count=20
        ),
        Pattern(
            name="syntax_error_recovery",
            language="python",
            pattern_type="parsing",
            code_snippet="""
def safe_parse(source_code, filename='<string>'):
    try:
        return ast.parse(source_code, filename=filename)
    except SyntaxError as e:
        # Try to fix common issues
        lines = source_code.split('\\n')
        if e.lineno and e.lineno <= len(lines):
            # Remove problematic line and try again
            lines.pop(e.lineno - 1)
            try:
                return ast.parse('\\n'.join(lines), filename=filename)
            except SyntaxError:
                return None
    return None
""",
            usage_context="Robust parsing with error recovery",
            dependencies=["ast"],
            success_count=28
        ),
        Pattern(
            name="docstring_extraction",
            language="python",
            pattern_type="parsing",
            code_snippet="""
def extract_docstrings(tree):
    docstrings = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings[node.name] = docstring
    return docstrings
""",
            usage_context="Documentation extraction from source code",
            dependencies=["ast"],
            success_count=25
        ),
        Pattern(
            name="import_analysis",
            language="python",
            pattern_type="parsing",
            code_snippet="""
def analyze_imports(tree):
    imports = {'standard': [], 'third_party': [], 'local': []}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                categorize_import(alias.name, imports)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                categorize_import(node.module, imports)
    return imports
""",
            usage_context="Import dependency analysis",
            dependencies=["ast"],
            success_count=22
        ),
        Pattern(
            name="complexity_analysis",
            language="python",
            pattern_type="metrics",
            code_snippet="""
class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
""",
            usage_context="Cyclomatic complexity calculation",
            dependencies=["ast"],
            success_count=18
        ),
        Pattern(
            name="variable_scope_analysis",
            language="python",
            pattern_type="analysis",
            code_snippet="""
def analyze_variable_scope(tree):
    scopes = {}
    current_scope = 'global'
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            current_scope = node.name
            scopes[current_scope] = {'variables': [], 'parameters': [arg.arg for arg in node.args.args]}
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    scopes.setdefault(current_scope, {'variables': []})['variables'].append(target.id)
    return scopes
""",
            usage_context="Variable scope and binding analysis",
            dependencies=["ast"],
            success_count=15
        ),
        Pattern(
            name="code_generation",
            language="python",
            pattern_type="generation",
            code_snippet="""
def generate_function_ast(name, args, body_statements):
    return ast.FunctionDef(
        name=name,
        args=ast.arguments(
            args=[ast.arg(arg=arg, annotation=None) for arg in args],
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=body_statements,
        decorator_list=[],
        returns=None
    )
""",
            usage_context="Programmatic AST generation",
            dependencies=["ast"],
            success_count=12
        ),
        Pattern(
            name="source_code_formatting",
            language="python",
            pattern_type="formatting",
            code_snippet="""
def format_source_code(tree):
    # Convert AST back to source code
    import astor
    return astor.to_source(tree)

def apply_black_formatting(source_code):
    import black
    return black.format_str(source_code, mode=black.FileMode())
""",
            usage_context="Code formatting and AST-to-source conversion",
            dependencies=["astor", "black"],
            success_count=16
        ),
        Pattern(
            name="dependency_graph_builder",
            language="python",
            pattern_type="analysis",
            code_snippet="""
def build_dependency_graph(modules):
    graph = {}
    for module_path in modules:
        with open(module_path) as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module)
        
        graph[module_path] = imports
    return graph
""",
            usage_context="Module dependency graph construction",
            dependencies=["ast"],
            success_count=24
        )
    ]