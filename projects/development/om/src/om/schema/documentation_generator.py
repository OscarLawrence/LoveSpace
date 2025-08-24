"""
Type documentation generation
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class TypeDocumentationGenerator:
    """Generates type documentation from schemas."""
    
    def generate_markdown_docs(self, schemas: Dict[str, Any], title: str = "Type Documentation") -> str:
        """Generate Markdown documentation from schemas."""
        lines = [f"# {title}", ""]
        
        for name, schema in schemas.items():
            lines.extend(self._generate_type_markdown(name, schema))
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_type_markdown(self, name: str, schema: Dict[str, Any]) -> List[str]:
        """Generate Markdown for a single type."""
        lines = [f"## {name}", ""]
        
        if 'parameters' in schema:
            # Function schema
            lines.append("### Parameters")
            lines.append("")
            
            params = schema['parameters']
            if params.get('properties'):
                for param_name, param_schema in params['properties'].items():
                    required = " (required)" if param_name in params.get('required', []) else ""
                    param_type = param_schema.get('type', 'unknown')
                    lines.append(f"- **{param_name}**{required}: `{param_type}`")
                    
                    if 'description' in param_schema:
                        lines.append(f"  - {param_schema['description']}")
            else:
                lines.append("No parameters.")
            
            lines.append("")
            
            if schema.get('returns'):
                lines.append("### Returns")
                lines.append("")
                return_type = schema['returns'].get('type', 'unknown')
                lines.append(f"Returns: `{return_type}`")
                lines.append("")
        
        else:
            # Class/object schema
            if schema.get('properties'):
                lines.append("### Properties")
                lines.append("")
                
                for prop_name, prop_schema in schema['properties'].items():
                    required = " (required)" if prop_name in schema.get('required', []) else ""
                    prop_type = prop_schema.get('type', 'unknown')
                    lines.append(f"- **{prop_name}**{required}: `{prop_type}`")
                    
                    if 'description' in prop_schema:
                        lines.append(f"  - {prop_schema['description']}")
                
                lines.append("")
        
        return lines
    
    def generate_json_schema_file(self, schemas: Dict[str, Any], output_path: Path):
        """Generate JSON Schema file."""
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Generated Type Schemas",
            "definitions": schemas
        }
        
        with open(output_path, 'w') as f:
            json.dump(json_schema, f, indent=2)
    
    def generate_openapi_schema(self, schemas: Dict[str, Any], title: str = "API") -> Dict[str, Any]:
        """Generate OpenAPI schema from type schemas."""
        openapi_schema = {
            "openapi": "3.0.3",
            "info": {
                "title": title,
                "version": "1.0.0",
                "description": "Generated API documentation"
            },
            "components": {
                "schemas": schemas
            }
        }
        
        return openapi_schema
