"""
Main schema generator using modular components
"""

import ast
from pathlib import Path
from typing import Dict, Any

from .data_models import TypeSchema
from .type_analyzer import TypeAnalyzer
from .function_schema_generator import FunctionSchemaGenerator
from .class_schema_generator import ClassSchemaGenerator
from .documentation_generator import TypeDocumentationGenerator


class SchemaGenerator:
    """Generates JSON schemas from Python code."""
    
    def __init__(self):
        self.analyzer = TypeAnalyzer()
        self.function_generator = FunctionSchemaGenerator()
        self.class_generator = ClassSchemaGenerator()
        self.doc_generator = TypeDocumentationGenerator()
        self.schemas: Dict[str, TypeSchema] = {}
    
    def generate_function_schema(self, func_node: ast.FunctionDef, module_globals: Dict = None) -> Dict[str, Any]:
        """Generate JSON schema for function parameters and return type."""
        return self.function_generator.generate_function_schema(func_node, module_globals)
    
    def generate_class_schema(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Generate JSON schema for class."""
        return self.class_generator.generate_class_schema(class_node)
    
    def generate_module_schemas(self, file_path: Path) -> Dict[str, Any]:
        """Generate schemas for all types in a module."""
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        schemas = {}
        
        # Generate schemas for classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_schema = self.generate_class_schema(node)
                schemas[node.name] = class_schema
            
            elif isinstance(node, ast.FunctionDef):
                # Skip nested functions
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                          if any(child is node for child in ast.walk(parent))):
                    func_schema = self.generate_function_schema(node)
                    schemas[node.name] = func_schema
        
        return schemas
    
    def generate_batch_schemas(self, source_dir: Path, output_dir: Path) -> Dict[str, Any]:
        """Generate schemas for all Python files in a directory."""
        output_dir.mkdir(exist_ok=True)
        all_schemas = {}
        
        for py_file in source_dir.rglob("*.py"):
            if py_file.name.startswith('_') and py_file.name != '__init__.py':
                continue
            
            try:
                module_schemas = self.generate_module_schemas(py_file)
                module_name = py_file.stem
                
                if module_schemas:
                    all_schemas[module_name] = module_schemas
                    
                    # Save individual module schema
                    output_file = output_dir / f"{module_name}_schema.json"
                    self.doc_generator.generate_json_schema_file(module_schemas, output_file)
                    
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
        
        return all_schemas
    
    def generate_documentation(self, schemas: Dict[str, Any], title: str = "Type Documentation") -> str:
        """Generate Markdown documentation from schemas."""
        return self.doc_generator.generate_markdown_docs(schemas, title)
