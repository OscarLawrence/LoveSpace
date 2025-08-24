"""Enhanced patterns module."""

from .cli_patterns import get_cli_patterns
from .ast_patterns import get_ast_patterns
from .database_patterns import get_database_patterns
from .error_handling_patterns import get_error_handling_patterns
from .testing_patterns import get_testing_patterns
from .api_patterns import get_api_patterns

def get_enhanced_patterns():
    """Get all enhanced patterns."""
    patterns = []
    patterns.extend(get_cli_patterns())
    patterns.extend(get_ast_patterns())
    patterns.extend(get_database_patterns())
    patterns.extend(get_error_handling_patterns())
    patterns.extend(get_testing_patterns())
    patterns.extend(get_api_patterns())
    return patterns