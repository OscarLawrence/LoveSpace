"""
Context database manager using DuckDB for code knowledge storage.
Provides simple CRUD operations for functions, classes, and patterns.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import duckdb

from .schema import CREATE_SCHEMA


@dataclass
class Function:
    name: str
    language: str
    file_path: str
    line_number: int
    params: list[dict[str, str]] | None = None
    return_type: str | None = None
    docstring: str | None = None
    body_hash: str | None = None
    id: int | None = None


@dataclass
class Class:
    name: str
    language: str
    file_path: str
    line_number: int
    methods: list[str] | None = None
    properties: list[str] | None = None
    docstring: str | None = None
    id: int | None = None


@dataclass
class Pattern:
    name: str
    language: str
    pattern_type: str
    code_snippet: str
    usage_context: str | None = None
    dependencies: list[str] | None = None
    success_count: int = 0
    id: int | None = None


class ContextDB:
    """Simple DuckDB-based context database."""

    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = duckdb.connect(str(self.db_path))
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        self.conn.execute(CREATE_SCHEMA)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()

    # Function operations
    def add_function(self, func: Function) -> int:
        """Add function to database."""
        query = """
        INSERT INTO functions (
            name, language, file_path, line_number, params, return_type, docstring, body_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
        """
        params_json = json.dumps(func.params) if func.params else None

        result = self.conn.execute(
            query,
            [
                func.name,
                func.language,
                func.file_path,
                func.line_number,
                params_json,
                func.return_type,
                func.docstring,
                func.body_hash,
            ],
        ).fetchone()

        return int(result[0]) if result else 0

    def get_function(self, func_id: int) -> Function | None:
        """Get function by ID."""
        query = "SELECT * FROM functions WHERE id = ?"
        result = self.conn.execute(query, [func_id]).fetchone()

        if not result:
            return None

        return Function(
            id=result[0],
            name=result[1],
            language=result[2],
            file_path=result[3],
            line_number=result[4],
            params=json.loads(result[5]) if result[5] else None,
            return_type=result[6],
            docstring=result[7],
            body_hash=result[8],
        )

    def find_functions(
        self, name: str | None = None, language: str | None = None
    ) -> list[Function]:
        """Find functions by name or language."""
        conditions = []
        params = []

        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        if language:
            conditions.append("language = ?")
            params.append(language)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM functions WHERE {where_clause}"

        results = self.conn.execute(query, params).fetchall()

        functions = []
        for row in results:
            functions.append(
                Function(
                    id=row[0],
                    name=row[1],
                    language=row[2],
                    file_path=row[3],
                    line_number=row[4],
                    params=json.loads(row[5]) if row[5] else None,
                    return_type=row[6],
                    docstring=row[7],
                    body_hash=row[8],
                )
            )

        return functions

    # Class operations
    def add_class(self, cls: Class) -> int:
        """Add class to database."""
        query = """
        INSERT INTO classes (name, language, file_path, line_number, methods, properties, docstring)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
        """
        methods_json = json.dumps(cls.methods) if cls.methods else None
        properties_json = json.dumps(cls.properties) if cls.properties else None

        result = self.conn.execute(
            query,
            [
                cls.name,
                cls.language,
                cls.file_path,
                cls.line_number,
                methods_json,
                properties_json,
                cls.docstring,
            ],
        ).fetchone()

        return int(result[0]) if result else 0

    def find_classes(self, name: str | None = None, language: str | None = None) -> list[Class]:
        """Find classes by name or language."""
        conditions = []
        params = []

        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        if language:
            conditions.append("language = ?")
            params.append(language)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM classes WHERE {where_clause}"

        results = self.conn.execute(query, params).fetchall()

        classes = []
        for row in results:
            classes.append(
                Class(
                    id=row[0],
                    name=row[1],
                    language=row[2],
                    file_path=row[3],
                    line_number=row[4],
                    methods=json.loads(row[5]) if row[5] else None,
                    properties=json.loads(row[6]) if row[6] else None,
                    docstring=row[7],
                )
            )

        return classes

    # Pattern operations
    def add_pattern(self, pattern: Pattern) -> int:
        """Add code pattern to database."""
        query = """
        INSERT INTO patterns (
            name, language, pattern_type, code_snippet, usage_context, dependencies, success_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
        """
        deps_json = json.dumps(pattern.dependencies) if pattern.dependencies else None

        result = self.conn.execute(
            query,
            [
                pattern.name,
                pattern.language,
                pattern.pattern_type,
                pattern.code_snippet,
                pattern.usage_context,
                deps_json,
                pattern.success_count,
            ],
        ).fetchone()

        return int(result[0]) if result else 0

    def find_patterns(
        self, pattern_type: str | None = None, language: str | None = None
    ) -> list[Pattern]:
        """Find patterns by type or language."""
        conditions = []
        params = []

        if pattern_type:
            conditions.append("pattern_type = ?")
            params.append(pattern_type)
        if language:
            conditions.append("language = ?")
            params.append(language)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM patterns WHERE {where_clause} ORDER BY success_count DESC"

        results = self.conn.execute(query, params).fetchall()

        patterns = []
        for row in results:
            patterns.append(
                Pattern(
                    id=row[0],
                    name=row[1],
                    language=row[2],
                    pattern_type=row[3],
                    code_snippet=row[4],
                    usage_context=row[5],
                    dependencies=json.loads(row[6]) if row[6] else None,
                    success_count=row[7],
                )
            )

        return patterns

    # Relationship operations
    def add_relationship(
        self, from_type: str, from_id: int, to_type: str, to_id: int, rel_type: str
    ) -> None:
        """Add relationship between code elements."""
        query = """
        INSERT INTO relationships (from_type, from_id, to_type, to_id, relationship_type)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(query, [from_type, from_id, to_type, to_id, rel_type])

    def get_relationships(self, from_type: str, from_id: int) -> list[tuple[str, int, str]]:
        """Get all relationships from a code element."""
        query = """
        SELECT to_type, to_id, relationship_type
        FROM relationships
        WHERE from_type = ? AND from_id = ?
        """
        rows = self.conn.execute(query, [from_type, from_id]).fetchall()
        return [(str(row[0]), int(row[1]), str(row[2])) for row in rows]

    # Utility methods
    def get_stats(self) -> dict[str, int]:
        """Get database statistics."""
        stats = {}

        tables = ["functions", "classes", "patterns", "relationships"]
        for table in tables:
            result = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            if result:
                stats[table] = result[0]

        return stats
