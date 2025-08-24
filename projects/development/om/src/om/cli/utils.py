"""CLI utility functions and lazy imports."""

# Lazy import flags - actual imports happen when needed
DOCS_PARSER_AVAILABLE = None
CODE_PARSER_AVAILABLE = None
MEMORY_AVAILABLE = None

def _check_docs_parser():
    """Lazy check for docs parser availability."""
    global DOCS_PARSER_AVAILABLE 
    if DOCS_PARSER_AVAILABLE is None:
        try:
            # Check actual available functionality
            from docs_parser.search import DocumentationSearcher
            from docs_parser.universal_parser import UniversalParser
            DOCS_PARSER_AVAILABLE = True
        except ImportError:
            DOCS_PARSER_AVAILABLE = False
    return DOCS_PARSER_AVAILABLE

def _check_code_parser():
    """Lazy check for code parser availability."""
    global CODE_PARSER_AVAILABLE
    if CODE_PARSER_AVAILABLE is None:
        try:
            # Only check essential components
            from code_parser.python_parser import PythonCodeParser
            from knowledge.db_manager import ContextDB
            CODE_PARSER_AVAILABLE = True
        except ImportError:
            CODE_PARSER_AVAILABLE = False
    return CODE_PARSER_AVAILABLE

def _check_memory():
    """Lazy check for memory system availability."""
    global MEMORY_AVAILABLE
    if MEMORY_AVAILABLE is None:
        try:
            # Check only core memory components
            from om.memory_integration import MemoryIntegration
            from om.session_manager import SessionManager
            MEMORY_AVAILABLE = True
        except ImportError:
            MEMORY_AVAILABLE = False
    return MEMORY_AVAILABLE