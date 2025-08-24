"""Sphinx Auto-Generation Infrastructure.

Generates comprehensive documentation from code without manual docstrings.
Implements docless architecture where code = documentation.
"""

from .docs import CodeAnalyzer, CodeElement, SphinxGenerator, DocumentationBuilder
from .docs.documentation_builder import batch_parse_with_sphinx

__all__ = [
    'CodeAnalyzer', 
    'CodeElement', 
    'SphinxGenerator', 
    'DocumentationBuilder',
    'batch_parse_with_sphinx'
]