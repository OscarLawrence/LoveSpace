"""
Class schema generation
"""

import ast
from typing import Dict, Any

from .type_analyzer import TypeAnalyzer
from .function_schema_generator import FunctionSchemaGenerator


class ClassSchemaGenerator:
    """Generates JSON schemas for classes"""
    
    def __init__(self):
        self.analyzer = TypeAnalyzer()
        self.function_generator = FunctionSchemaGenerator()
    
    def generate_class_schema(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Generate JSON schema for class."""
        schema = {
            'type': 'object',
            'title': class_node.name,
            'properties': {},
            'required': []
        }
        
        # Find __init__ method for constructor parameters
        init_method = None
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_method = item
                break
        
        if init_method:
            init_schema = self.function_generator.generate_function_schema(init_method)
            schema.update(init_schema['parameters'])
        
        # Find class attributes with type annotations
        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_name = item.target.id
                
                try:
                    annotation_str = ast.unparse(item.annotation)
                    type_schema = self.analyzer._analyze_string_annotation(annotation_str)
                    schema['properties'][attr_name] = type_schema.properties
                except:
                    schema['properties'][attr_name] = {'type': 'string'}
        
        return schema
