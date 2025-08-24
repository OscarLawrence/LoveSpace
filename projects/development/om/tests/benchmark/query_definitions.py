"""
Benchmark query definitions for testing context injection
"""

from typing import List
from .data_models import BenchmarkQuery


def load_benchmark_queries() -> List[BenchmarkQuery]:
    """Define comprehensive test queries covering different domains."""
    return [
        # CLI and Command Processing
        BenchmarkQuery(
            query="parse command line arguments",
            expected_functions=["parse", "command", "cli", "args"],
            expected_patterns=["cli", "command", "parsing"],
            expected_docs_keywords=["click", "argparse", "cli"],
            description="Command line argument parsing"
        ),
        BenchmarkQuery(
            query="workspace status checking",
            expected_functions=["status", "check", "workspace", "stats"],
            expected_patterns=["workspace", "status", "monitoring"],
            expected_docs_keywords=["workspace", "status", "git"],
            description="Workspace management and status"
        ),
        
        # Code Analysis and Parsing
        BenchmarkQuery(
            query="parse Python code",
            expected_functions=["parse", "ast", "python", "code"],
            expected_patterns=["parser", "ast", "python"],
            expected_docs_keywords=["ast", "python", "parsing"],
            description="Python code parsing functionality"
        ),
        BenchmarkQuery(
            query="extract function definitions",
            expected_functions=["extract", "function", "def", "parse"],
            expected_patterns=["extraction", "function", "ast"],
            expected_docs_keywords=["function", "ast", "extraction"],
            description="Function extraction from code"
        ),
        
        # Documentation Processing
        BenchmarkQuery(
            query="search documentation",
            expected_functions=["search", "docs", "find", "query"],
            expected_patterns=["search", "docs", "documentation"],
            expected_docs_keywords=["search", "documentation", "docs"],
            description="Documentation search functionality"
        ),
        BenchmarkQuery(
            query="parse documentation files",
            expected_functions=["parse", "docs", "read", "process"],
            expected_patterns=["parser", "docs", "documentation"],
            expected_docs_keywords=["parsing", "documentation", "files"],
            description="Documentation file processing"
        ),
        
        # Knowledge Management
        BenchmarkQuery(
            query="store code patterns",
            expected_functions=["store", "save", "pattern", "db"],
            expected_patterns=["storage", "pattern", "knowledge"],
            expected_docs_keywords=["storage", "database", "patterns"],
            description="Code pattern storage and management"
        ),
        BenchmarkQuery(
            query="find similar functions",
            expected_functions=["find", "similar", "search", "match"],
            expected_patterns=["similarity", "search", "matching"],
            expected_docs_keywords=["similarity", "search", "embeddings"],
            description="Function similarity search"
        ),
        
        # CLI Tool Development
        BenchmarkQuery(
            query="click command definition",
            expected_functions=["command", "click", "cli", "group"],
            expected_patterns=["cli", "command", "click"],
            expected_docs_keywords=["click", "cli", "command"],
            description="CLI command creation with Click"
        ),
        BenchmarkQuery(
            query="workspace management commands",
            expected_functions=["workspace", "manage", "status", "info"],
            expected_patterns=["workspace", "management", "cli"],
            expected_docs_keywords=["workspace", "management", "cli"],
            description="Workspace management functionality"
        ),
        
        # Testing
        BenchmarkQuery(
            query="unit test creation",
            expected_functions=["test", "assert", "mock", "verify"],
            expected_patterns=["test", "testing", "mock"],
            expected_docs_keywords=["pytest", "testing", "unittest"],
            description="Testing methodologies"
        ),
        BenchmarkQuery(
            query="API integration testing",
            expected_functions=["test", "request", "response", "client"],
            expected_patterns=["test", "api", "integration"],
            expected_docs_keywords=["testing", "api", "integration"],
            description="Integration testing patterns"
        )
    ]
