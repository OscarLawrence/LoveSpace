"""Code parsing and AST analysis for populating knowledge database."""

from .python_parser import PythonCodeParser
try:
    from .sphinx_parser import SphinxCodeParser, create_enhanced_parser
except ImportError:
    # Optional dependency - sphinx not available
    SphinxCodeParser = create_enhanced_parser = None

__version__ = "0.1.0"
__all__ = ["PythonCodeParser", "SphinxCodeParser", "create_enhanced_parser"]