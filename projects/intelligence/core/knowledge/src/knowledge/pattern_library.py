"""Code pattern library for knowledge base population."""

from typing import List, Dict
from .db_manager import ContextDB, Pattern


class PatternLibrary:
    """Library of common code patterns for AI development."""
    
    def __init__(self):
        self.patterns = self._define_patterns()
    
    def _define_patterns(self) -> List[Dict]:
        """Define comprehensive code patterns."""
        return [
            # CLI Patterns
            {
                "name": "click_command_basic",
                "pattern_type": "cli",
                "code_snippet": """@click.command()
@click.argument('input_file')
@click.option('--output', '-o', help='Output file')
def process(input_file, output):
    \"\"\"Process input file.\"\"\"
    pass""",
                "usage_context": "Basic Click command with argument and option",
                "dependencies": ["click"],
                "success_count": 10
            },
            {
                "name": "click_group_commands",
                "pattern_type": "cli",
                "code_snippet": """@click.group()
def main():
    \"\"\"Main command group.\"\"\"
    pass

@main.command()
def subcommand():
    \"\"\"Subcommand.\"\"\"
    pass""",
                "usage_context": "Click command groups for complex CLI tools",
                "dependencies": ["click"],
                "success_count": 8
            },
            
            # AST/Code Parsing Patterns
            {
                "name": "ast_function_visitor",
                "pattern_type": "ast",
                "code_snippet": """class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'args': [arg.arg for arg in node.args.args]
        })
        self.generic_visit(node)""",
                "usage_context": "Extract function definitions from Python AST",
                "dependencies": ["ast"],
                "success_count": 15
            },
            {
                "name": "ast_class_extractor",
                "pattern_type": "ast",
                "code_snippet": """def extract_classes(source_code):
    tree = ast.parse(source_code)
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'line': node.lineno,
                'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            })
    return classes""",
                "usage_context": "Extract class definitions and methods from code",
                "dependencies": ["ast"],
                "success_count": 12
            },
            
            # Database/Storage Patterns
            {
                "name": "duckdb_connection_manager",
                "pattern_type": "database",
                "code_snippet": """class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
    
    def __enter__(self):
        self.conn = duckdb.connect(self.db_path)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()""",
                "usage_context": "Context manager for DuckDB connections",
                "dependencies": ["duckdb"],
                "success_count": 9
            },
            {
                "name": "batch_insert_pattern",
                "pattern_type": "database",
                "code_snippet": """def batch_insert(conn, table, data, batch_size=1000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        placeholders = ','.join(['?' * len(batch[0])])
        sql = f"INSERT INTO {table} VALUES ({placeholders})"
        conn.executemany(sql, batch)""",
                "usage_context": "Efficient batch insertion for large datasets",
                "dependencies": ["duckdb"],
                "success_count": 7
            },
            
            # Error Handling Patterns
            {
                "name": "retry_with_backoff",
                "pattern_type": "error_handling",
                "code_snippet": """import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)""",
                "usage_context": "Retry failed operations with exponential backoff",
                "dependencies": ["time", "random"],
                "success_count": 11
            },
            {
                "name": "context_error_handler",
                "pattern_type": "error_handling",
                "code_snippet": """from contextlib import contextmanager

@contextmanager
def handle_errors(operation_name):
    try:
        yield
    except FileNotFoundError:
        print(f"File not found during {operation_name}")
    except PermissionError:
        print(f"Permission denied during {operation_name}")
    except Exception as e:
        print(f"Unexpected error in {operation_name}: {e}")""",
                "usage_context": "Context manager for consistent error handling",
                "dependencies": ["contextlib"],
                "success_count": 6
            },
            
            # Async Patterns
            {
                "name": "async_batch_processor",
                "pattern_type": "async",
                "code_snippet": """import asyncio

async def process_batch(items, batch_size=10):
    semaphore = asyncio.Semaphore(batch_size)
    
    async def process_item(item):
        async with semaphore:
            # Process item
            await asyncio.sleep(0.1)  # Simulate work
            return f"processed_{item}"
    
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)""",
                "usage_context": "Process items concurrently with rate limiting",
                "dependencies": ["asyncio"],
                "success_count": 8
            },
            
            # Validation Patterns
            {
                "name": "pydantic_model_validation",
                "pattern_type": "validation",
                "code_snippet": """from pydantic import BaseModel, validator

class DataModel(BaseModel):
    name: str
    age: int
    email: str
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v""",
                "usage_context": "Data validation with Pydantic models",
                "dependencies": ["pydantic"],
                "success_count": 13
            },
            
            # File Processing Patterns
            {
                "name": "safe_file_processor",
                "pattern_type": "file_processing",
                "code_snippet": """from pathlib import Path

def process_files_safely(directory, pattern="*.py"):
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} not found")
    
    results = []
    for file_path in directory.glob(pattern):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                results.append({'file': str(file_path), 'size': len(content)})
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return results""",
                "usage_context": "Safely process multiple files with error handling",
                "dependencies": ["pathlib"],
                "success_count": 9
            },
            
            # Caching Patterns
            {
                "name": "simple_lru_cache",
                "pattern_type": "caching",
                "code_snippet": """from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param):
    # Simulate expensive operation
    result = sum(range(param * 1000))
    return result

# Clear cache when needed
# expensive_computation.cache_clear()""",
                "usage_context": "Simple LRU caching for expensive functions",
                "dependencies": ["functools"],
                "success_count": 10
            },
            
            # Testing Patterns
            {
                "name": "pytest_fixture_pattern",
                "pattern_type": "testing",
                "code_snippet": """import pytest

@pytest.fixture
def sample_data():
    return {'key': 'value', 'items': [1, 2, 3]}

@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path

def test_with_fixtures(sample_data, temp_file):
    assert sample_data['key'] == 'value'
    assert temp_file.read_text() == "test content" """,
                "usage_context": "Pytest fixtures for test data and temporary files",
                "dependencies": ["pytest"],
                "success_count": 12
            },
            
            # Configuration Patterns
            {
                "name": "environment_config",
                "pattern_type": "configuration",
                "code_snippet": """import os
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    api_key: str
    debug: bool = False
    
    @classmethod
    def from_env(cls):
        return cls(
            database_url=os.getenv('DATABASE_URL', 'sqlite:///default.db'),
            api_key=os.getenv('API_KEY', ''),
            debug=os.getenv('DEBUG', 'false').lower() == 'true'
        )""",
                "usage_context": "Environment-based configuration with defaults",
                "dependencies": ["os", "dataclasses"],
                "success_count": 8
            }
        ]
    
    def populate_knowledge_base(self, db: ContextDB) -> int:
        """Populate knowledge base with code patterns."""
        patterns_added = 0
        
        for pattern_data in self.patterns:
            try:
                pattern = Pattern(
                    name=pattern_data["name"],
                    language="python",
                    pattern_type=pattern_data["pattern_type"],
                    code_snippet=pattern_data["code_snippet"],
                    usage_context=pattern_data["usage_context"],
                    dependencies=pattern_data["dependencies"],
                    success_count=pattern_data["success_count"]
                )
                
                pattern_id = db.add_pattern(pattern)
                if pattern_id:
                    patterns_added += 1
                    
            except Exception as e:
                print(f"Error adding pattern {pattern_data['name']}: {e}")
        
        return patterns_added
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Dict]:
        """Get patterns filtered by type."""
        return [p for p in self.patterns if p["pattern_type"] == pattern_type]
    
    def get_pattern_types(self) -> List[str]:
        """Get all available pattern types."""
        return list(set(p["pattern_type"] for p in self.patterns))