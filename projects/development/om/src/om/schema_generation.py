"""Schema Auto-Generation System.

Generates JSON schemas and type documentation from Python type hints.
Legacy compatibility module - imports from new modular structure.
"""

from .schema.data_models import TypeSchema
from .schema.documentation_generator import TypeDocumentationGenerator
from .schema.generator import SchemaGenerator
from .schema.type_analyzer import TypeAnalyzer

__all__ = ['TypeSchema', 'TypeAnalyzer', 'SchemaGenerator', 'TypeDocumentationGenerator']