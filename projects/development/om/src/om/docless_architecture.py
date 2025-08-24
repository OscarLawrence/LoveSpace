"""Docless Architecture Implementation.

Code serves as documentation through intelligent analysis and generation.
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import re


@dataclass
class CodeDocumentation:
    """Documentation extracted from code structure."""
    purpose: str
    behavior: str
    parameters: Dict[str, str]
    returns: str
    examples: List[str]
    complexity: str
    dependencies: List[str]


class CodeDocumentationExtractor:
    """Extracts documentation from code without requiring docstrings."""
    
    def __init__(self):
        self.type_patterns = {
            'str': 'string value',
            'int': 'integer value', 
            'float': 'floating point number',
            'bool': 'boolean value',
            'list': 'list of items',
            'dict': 'dictionary mapping',
            'Path': 'file system path',
            'Optional': 'optional value'
        }
    
    def extract_function_docs(self, func_node: ast.FunctionDef, source: str) -> CodeDocumentation:
        """Extract documentation from function definition."""
        # Analyze function name for purpose
        purpose = self._infer_purpose_from_name(func_node.name)
        
        # Analyze parameters
        parameters = {}
        for arg in func_node.args.args:
            param_doc = self._infer_parameter_purpose(arg.arg, arg.annotation)
            parameters[arg.arg] = param_doc
        
        # Analyze return type
        returns = self._infer_return_purpose(func_node.returns)
        
        # Analyze function body for behavior
        behavior = self._analyze_function_behavior(func_node)
        
        # Extract examples from tests or usage
        examples = self._find_usage_examples(func_node.name, source)
        
        # Assess complexity
        complexity = self._assess_complexity(func_node)
        
        # Find dependencies
        dependencies = self._find_dependencies(func_node)
        
        return CodeDocumentation(
            purpose=purpose,
            behavior=behavior,
            parameters=parameters,
            returns=returns,
            examples=examples,
            complexity=complexity,
            dependencies=dependencies
        )
    
    def extract_class_docs(self, class_node: ast.ClassDef, source: str) -> CodeDocumentation:
        """Extract documentation from class definition."""
        purpose = self._infer_purpose_from_name(class_node.name)
        
        # Analyze class structure
        methods = [n.name for n in class_node.body if isinstance(n, ast.FunctionDef)]
        attributes = self._find_class_attributes(class_node)
        
        behavior = f"Provides {len(methods)} methods and {len(attributes)} attributes"
        if methods:
            behavior += f". Key methods: {', '.join(methods[:3])}"
        
        # Find inheritance
        bases = [self._get_name(base) for base in class_node.bases]
        if bases:
            behavior += f". Inherits from: {', '.join(bases)}"
        
        return CodeDocumentation(
            purpose=purpose,
            behavior=behavior,
            parameters={'__init__': 'Class constructor parameters'},
            returns='Class instance',
            examples=self._find_usage_examples(class_node.name, source),
            complexity=self._assess_complexity(class_node),
            dependencies=self._find_dependencies(class_node)
        )
    
    def _infer_purpose_from_name(self, name: str) -> str:
        """Infer purpose from function/class name."""
        # Convert camelCase/PascalCase to words
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
        if not words:
            words = name.split('_')
        
        # Common patterns
        if name.startswith('get_'):
            return f"Retrieves {' '.join(words[1:])}"
        elif name.startswith('set_'):
            return f"Sets {' '.join(words[1:])}"
        elif name.startswith('create_'):
            return f"Creates {' '.join(words[1:])}"
        elif name.startswith('delete_'):
            return f"Deletes {' '.join(words[1:])}"
        elif name.startswith('update_'):
            return f"Updates {' '.join(words[1:])}"
        elif name.startswith('find_'):
            return f"Finds {' '.join(words[1:])}"
        elif name.startswith('parse_'):
            return f"Parses {' '.join(words[1:])}"
        elif name.startswith('generate_'):
            return f"Generates {' '.join(words[1:])}"
        elif name.startswith('validate_'):
            return f"Validates {' '.join(words[1:])}"
        elif name.startswith('is_'):
            return f"Checks if {' '.join(words[1:])}"
        elif name.startswith('has_'):
            return f"Checks if has {' '.join(words[1:])}"
        elif name.endswith('_manager'):
            return f"Manages {' '.join(words[:-1])}"
        elif name.endswith('_handler'):
            return f"Handles {' '.join(words[:-1])}"
        elif name.endswith('_builder'):
            return f"Builds {' '.join(words[:-1])}"
        elif name.endswith('_analyzer'):
            return f"Analyzes {' '.join(words[:-1])}"
        else:
            return f"Handles {' '.join(words)}"
    
    def _infer_parameter_purpose(self, param_name: str, annotation: ast.AST) -> str:
        """Infer parameter purpose from name and type."""
        type_str = self._get_annotation_string(annotation) if annotation else "any"
        
        # Map type to description
        base_type = type_str.split('[')[0]  # Handle generics like List[str]
        type_desc = self.type_patterns.get(base_type, f"{type_str} value")
        
        # Infer from parameter name
        if 'file' in param_name or 'path' in param_name:
            return f"File path ({type_desc})"
        elif 'dir' in param_name:
            return f"Directory path ({type_desc})"
        elif 'name' in param_name:
            return f"Name identifier ({type_desc})"
        elif 'id' in param_name:
            return f"Unique identifier ({type_desc})"
        elif 'config' in param_name:
            return f"Configuration ({type_desc})"
        elif 'option' in param_name:
            return f"Option setting ({type_desc})"
        elif 'flag' in param_name:
            return f"Boolean flag ({type_desc})"
        else:
            return f"{param_name.replace('_', ' ')} ({type_desc})"
    
    def _infer_return_purpose(self, return_annotation: ast.AST) -> str:
        """Infer return value purpose from type annotation."""
        if not return_annotation:
            return "Result of operation"
        
        type_str = self._get_annotation_string(return_annotation)
        
        if type_str == 'bool':
            return "True if successful, False otherwise"
        elif type_str == 'None':
            return "No return value"
        elif type_str.startswith('List'):
            return "List of results"
        elif type_str.startswith('Dict'):
            return "Dictionary of results"
        elif type_str.startswith('Optional'):
            return "Result if found, None otherwise"
        else:
            return f"Returns {type_str}"
    
    def _analyze_function_behavior(self, func_node: ast.FunctionDef) -> str:
        """Analyze function body to understand behavior."""
        behaviors = []
        
        # Count different statement types
        assignments = 0
        conditionals = 0
        loops = 0
        function_calls = 0
        returns = 0
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                assignments += 1
            elif isinstance(node, ast.If):
                conditionals += 1
            elif isinstance(node, (ast.For, ast.While)):
                loops += 1
            elif isinstance(node, ast.Call):
                function_calls += 1
            elif isinstance(node, ast.Return):
                returns += 1
        
        if assignments > 0:
            behaviors.append(f"performs {assignments} assignments")
        if conditionals > 0:
            behaviors.append(f"has {conditionals} conditional branches")
        if loops > 0:
            behaviors.append(f"contains {loops} loops")
        if function_calls > 3:
            behaviors.append(f"makes {function_calls} function calls")
        
        if not behaviors:
            return "Simple operation"
        
        return "Function " + ", ".join(behaviors)
    
    def _find_usage_examples(self, name: str, source: str) -> List[str]:
        """Find usage examples in source code."""
        examples = []
        lines = source.split('\n')
        
        for i, line in enumerate(lines):
            if name in line and ('=' in line or 'assert' in line):
                # Found potential usage
                example_lines = []
                
                # Get context around usage
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                
                for j in range(start, end):
                    if lines[j].strip():
                        example_lines.append(lines[j].strip())
                
                if example_lines:
                    examples.append('\n'.join(example_lines))
        
        return examples[:3]  # Limit to 3 examples
    
    def _assess_complexity(self, node: ast.AST) -> str:
        """Assess code complexity."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        if complexity <= 3:
            return "Low complexity"
        elif complexity <= 7:
            return "Medium complexity"
        else:
            return "High complexity"
    
    def _find_dependencies(self, node: ast.AST) -> List[str]:
        """Find external dependencies used in code."""
        dependencies = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    # Method call like obj.method()
                    if isinstance(child.func.value, ast.Name):
                        dependencies.add(child.func.value.id)
                elif isinstance(child.func, ast.Name):
                    # Function call like func()
                    dependencies.add(child.func.id)
        
        # Filter out built-ins
        builtins = {'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set'}
        return [dep for dep in dependencies if dep not in builtins][:5]
    
    def _find_class_attributes(self, class_node: ast.ClassDef) -> List[str]:
        """Find class attributes."""
        attributes = []
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                attributes.append(node.target.id)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return attributes
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)
    
    def _get_annotation_string(self, node: ast.AST) -> str:
        """Convert annotation AST to string."""
        try:
            return ast.unparse(node)
        except:
            return str(node)


class DoclessSphinxGenerator:
    """Generates Sphinx documentation using docless architecture."""
    
    def __init__(self, extractor: CodeDocumentationExtractor):
        self.extractor = extractor
    
    def generate_rst_for_function(self, func_node: ast.FunctionDef, source: str) -> str:
        """Generate RST documentation for function."""
        docs = self.extractor.extract_function_docs(func_node, source)
        
        rst = f"""
{func_node.name}
{'=' * len(func_node.name)}

**Purpose:** {docs.purpose}

**Behavior:** {docs.behavior}

**Parameters:**

"""
        
        for param, desc in docs.parameters.items():
            rst += f"* ``{param}``: {desc}\n"
        
        rst += f"\n**Returns:** {docs.returns}\n"
        rst += f"\n**Complexity:** {docs.complexity}\n"
        
        if docs.dependencies:
            rst += f"\n**Dependencies:** {', '.join(docs.dependencies)}\n"
        
        if docs.examples:
            rst += "\n**Examples:**\n\n"
            for example in docs.examples:
                rst += f".. code-block:: python\n\n"
                for line in example.split('\n'):
                    rst += f"   {line}\n"
                rst += "\n"
        
        return rst
    
    def generate_rst_for_class(self, class_node: ast.ClassDef, source: str) -> str:
        """Generate RST documentation for class."""
        docs = self.extractor.extract_class_docs(class_node, source)
        
        rst = f"""
{class_node.name}
{'=' * len(class_node.name)}

**Purpose:** {docs.purpose}

**Behavior:** {docs.behavior}

**Complexity:** {docs.complexity}

"""
        
        if docs.dependencies:
            rst += f"**Dependencies:** {', '.join(docs.dependencies)}\n\n"
        
        if docs.examples:
            rst += "**Usage Examples:**\n\n"
            for example in docs.examples:
                rst += f".. code-block:: python\n\n"
                for line in example.split('\n'):
                    rst += f"   {line}\n"
                rst += "\n"
        
        return rst