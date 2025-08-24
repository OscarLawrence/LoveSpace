"""
Query interface for agents to find relevant code context.
Provides high-level search methods for AI agents.
"""

from typing import Any

from .db_manager import ContextDB, Function, Pattern


class ContextQuery:
    """High-level query interface for AI agents."""

    def __init__(self, db: ContextDB):
        self.db = db

    def find_auth_patterns(self, language: str | None = None) -> list[Pattern]:
        """Find authentication-related code patterns."""
        return self.db.find_patterns("auth", language)

    def find_database_patterns(self, language: str | None = None) -> list[Pattern]:
        """Find database-related code patterns."""
        return self.db.find_patterns("database", language)

    def find_api_patterns(self, language: str | None = None) -> list[Pattern]:
        """Find API-related code patterns."""
        return self.db.find_patterns("api", language)

    def find_similar_functions(
        self, function_name: str, language: str | None = None
    ) -> list[Function]:
        """Find functions with similar names or purposes."""
        return self.db.find_functions(function_name, language)

    def get_function_context(self, func_id: int) -> dict[str, Any]:
        """Get full context for a function including relationships."""
        func = self.db.get_function(func_id)
        if not func:
            return {}

        relationships = self.db.get_relationships("function", func_id)

        return {
            "function": func,
            "calls": [rel for rel in relationships if rel[2] == "calls"],
            "called_by": self._get_reverse_relationships("function", func_id, "calls"),
            "uses": [rel for rel in relationships if rel[2] == "uses"],
        }

    def find_patterns_by_dependencies(
        self, dependencies: list[str], language: str | None = None
    ) -> list[Pattern]:
        """Find patterns that use specific dependencies."""
        patterns = self.db.find_patterns(language=language)

        matching = []
        for pattern in patterns:
            if pattern.dependencies and any(dep in pattern.dependencies for dep in dependencies):
                matching.append(pattern)

        return matching

    def get_codebase_summary(self, language: str | None = None) -> dict[str, Any]:
        """Get summary statistics for the codebase."""
        stats = self.db.get_stats()

        if language:
            functions = self.db.find_functions(language=language)
            classes = self.db.find_classes(language=language)
            patterns = self.db.find_patterns(language=language)

            return {
                "total_functions": len(functions),
                "total_classes": len(classes),
                "total_patterns": len(patterns),
                "language": language,
                "top_patterns": patterns[:5],  # Most successful patterns
            }

        return stats

    def search_by_keyword(self, keyword: str, language: str | None = None) -> dict[str, list[Any]]:
        """Search functions, classes, and patterns by keyword."""
        results: dict[str, list[Any]] = {"functions": [], "classes": [], "patterns": []}

        # Search functions
        functions = self.db.find_functions(name=keyword, language=language)
        results["functions"] = functions

        # Search classes
        classes = self.db.find_classes(name=keyword, language=language)
        results["classes"] = classes

        # Search patterns by name or usage context
        all_patterns = self.db.find_patterns(language=language)
        matching_patterns = []
        for pattern in all_patterns:
            if keyword.lower() in pattern.name.lower() or (
                pattern.usage_context and keyword.lower() in pattern.usage_context.lower()
            ):
                matching_patterns.append(pattern)
        results["patterns"] = matching_patterns

        return results

    def get_recommended_patterns(
        self, task_type: str, language: str | None = None
    ) -> list[Pattern]:
        """Get recommended patterns for a specific task type."""
        # Map task types to pattern types
        task_mapping = {
            "authentication": "auth",
            "database": "database",
            "api": "api",
            "validation": "validation",
            "testing": "test",
            "logging": "logging",
        }

        pattern_type = task_mapping.get(task_type.lower())
        if pattern_type:
            return self.db.find_patterns(pattern_type, language)

        # Fallback: search by keyword
        return self.search_by_keyword(task_type, language)["patterns"]

    def _get_reverse_relationships(
        self, to_type: str, to_id: int, rel_type: str
    ) -> list[tuple[str, int, str]]:
        """Get relationships pointing to this element."""
        query = """
        SELECT from_type, from_id, relationship_type
        FROM relationships
        WHERE to_type = ? AND to_id = ? AND relationship_type = ?
        """
        result = self.db.conn.execute(query, [to_type, to_id, rel_type]).fetchall()
        return [(str(row[0]), int(row[1]), str(row[2])) for row in result]
