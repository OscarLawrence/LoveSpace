"""
Function schema generation
"""

import ast
from typing import Dict, Any

from .type_analyzer import TypeAnalyzer


class FunctionSchemaGenerator:
    """Generates JSON schemas for functions"""
    
    def __init__(self):
        self.analyzer = TypeAnalyzer()
    
    def generate_function_schema(self, func_node: ast.FunctionDef, module_globals: Dict = None) -> Dict[str, Any]:
        """Generate JSON schema for function parameters and return type."""
        schema = {
            'type': 'object',
            'title': f'{func_node.name} Parameters',
            'properties': {},
            'required': []
        }
        
        # Analyze parameters
        for arg in func_node.args.args:
            if arg.arg in ('self', 'cls'):
                continue
            
            param_schema = {'type': 'string'}  # Default
            
            if arg.annotation:
                try:
                    # Convert AST annotation to type schema
                    annotation_str = ast.unparse(arg.annotation)
                    type_schema = self.analyzer._analyze_string_annotation(annotation_str)
                    param_schema = type_schema.properties
                except:
                    param_schema = {'type': 'string', 'description': f'Parameter {arg.arg}'}
            
            schema['properties'][arg.arg] = param_schema
            
            # Check if parameter has default value
            defaults_offset = len(func_node.args.args) - len(func_node.args.defaults)
            arg_index = func_node.args.args.index(arg)
            
            if arg_index < defaults_offset:
                schema['required'].append(arg.arg)
        
        # Analyze return type
        return_schema = None
        if func_node.returns:
            try:
                return_annotation = ast.unparse(func_node.returns)
                return_type_schema = self.analyzer._analyze_string_annotation(return_annotation)
                return_schema = return_type_schema.properties
            except:
                return_schema = {'type': 'object'}
        
        result = {
            'parameters': schema,
            'returns': return_schema
        }
        
        return result
