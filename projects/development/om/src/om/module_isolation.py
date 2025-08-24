"""
Module isolation system for focused AI development with separation of concerns.
Creates isolated workspaces per module/task to prevent context pollution.
"""

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

from knowledge.db_manager import ContextDB


@dataclass
class ModuleBoundary:
    module_name: str
    allowed_dependencies: List[str]
    interface_contracts: Dict[str, str]
    isolation_rules: Dict[str, str]


@dataclass
class IsolatedWorkspace:
    id: str
    module_name: str
    task_scope: str
    isolated_files: List[str]
    dependencies: List[str]
    boundaries: Dict[str, str]
    created_at: datetime
    active: bool = True


class ModuleIsolation:
    """Manages module isolation and workspace creation for focused development."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db = ContextDB(db_path)
        self._ensure_memory_tables()
    
    def _ensure_memory_tables(self):
        """Ensure memory tables exist in database."""
        # Tables are created by schema.py, this is just a safety check
        try:
            self.db.conn.execute("SELECT 1 FROM module_workspaces LIMIT 1")
        except Exception:
            # Re-run schema creation if tables don't exist
            from knowledge.schema import CREATE_SCHEMA
            self.db.conn.execute(CREATE_SCHEMA)
    
    def create_isolated_workspace(self, module_name: str, task_scope: str) -> str:
        """Create isolated workspace for module/task with filtered context."""
        workspace_id = f"ws_{module_name}_{uuid.uuid4().hex[:8]}"
        
        # Analyze codebase to find relevant files
        isolated_files = self._find_relevant_files(module_name, task_scope)
        dependencies = self._get_module_dependencies(module_name)
        boundaries = self._get_module_boundaries(module_name)
        
        # Store workspace in database
        query = """
        INSERT INTO module_workspaces (
            id, module_name, task_scope, isolated_files, dependencies, boundaries, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.conn.execute(query, [
            workspace_id,
            module_name,
            task_scope,
            json.dumps(isolated_files),
            json.dumps(dependencies),
            json.dumps(boundaries),
            True
        ])
        
        return workspace_id
    
    def filter_relevant_context(self, module_name: str, task_type: str) -> Dict:
        """Filter codebase to show only relevant files and context."""
        # Get module boundaries
        boundaries = self._get_module_boundaries(module_name)
        
        # Find relevant files based on module scope
        relevant_files = self._find_relevant_files(module_name, task_type)
        
        # Get related functions and classes from knowledge base
        functions = self.db.find_functions()
        classes = self.db.find_classes()
        
        # Filter to module-relevant items
        module_functions = [f for f in functions if self._is_file_relevant(f.file_path, relevant_files)]
        module_classes = [c for c in classes if self._is_file_relevant(c.file_path, relevant_files)]
        
        return {
            "module_name": module_name,
            "task_type": task_type,
            "relevant_files": relevant_files,
            "functions": [{"name": f.name, "file": f.file_path, "line": f.line_number} for f in module_functions],
            "classes": [{"name": c.name, "file": c.file_path, "line": c.line_number} for c in module_classes],
            "boundaries": boundaries
        }
    
    def get_module_dependencies(self, module_name: str) -> List[str]:
        """Get dependencies for a specific module."""
        return self._get_module_dependencies(module_name)
    
    def isolate_codebase_view(self, module_name: str) -> Dict:
        """Create isolated view of codebase for specific module."""
        workspace_id = self.create_isolated_workspace(module_name, "general")
        context = self.filter_relevant_context(module_name, "general")
        
        return {
            "workspace_id": workspace_id,
            "module_context": context,
            "isolation_active": True
        }
    
    def create_focused_documentation(self, module_name: str, task_type: str) -> str:
        """Generate focused documentation for module context."""
        context = self.filter_relevant_context(module_name, task_type)
        
        doc_parts = [
            f"# {module_name} Module Documentation",
            f"Task Type: {task_type}",
            "",
            "## Relevant Files:",
        ]
        
        for file_path in context["relevant_files"]:
            doc_parts.append(f"- {file_path}")
        
        if context["functions"]:
            doc_parts.extend(["", "## Functions:"])
            for func in context["functions"][:10]:  # Limit to top 10
                doc_parts.append(f"- {func['name']} ({func['file']}:{func['line']})")
        
        if context["classes"]:
            doc_parts.extend(["", "## Classes:"])
            for cls in context["classes"][:10]:  # Limit to top 10
                doc_parts.append(f"- {cls['name']} ({cls['file']}:{cls['line']})")
        
        return "\n".join(doc_parts)
    
    def enforce_module_boundaries(self, module_name: str, proposed_changes: Dict) -> bool:
        """Enforce module boundaries and separation of concerns."""
        boundaries = self._get_module_boundaries(module_name)
        
        if not boundaries:
            return True  # No boundaries defined, allow changes
        
        # Check if proposed changes violate boundaries
        for file_path in proposed_changes.get("modified_files", []):
            if not self._is_change_allowed(module_name, file_path, boundaries):
                return False
        
        return True
    
    def cleanup_isolated_workspace(self, workspace_id: str):
        """Clean up isolated workspace."""
        query = "UPDATE module_workspaces SET active = FALSE WHERE id = ?"
        self.db.conn.execute(query, [workspace_id])
    
    def get_cross_module_interfaces(self, module_name: str) -> Dict:
        """Get interfaces between modules."""
        query = """
        SELECT from_module, to_module, handoff_context, interface_changes
        FROM module_handoffs 
        WHERE from_module = ? OR to_module = ?
        ORDER BY created_at DESC
        """
        
        results = self.db.conn.execute(query, [module_name, module_name]).fetchall()
        
        interfaces = {}
        for row in results:
            from_mod, to_mod, context, changes = row
            key = f"{from_mod}->{to_mod}"
            interfaces[key] = {
                "context": json.loads(context) if context else {},
                "changes": json.loads(changes) if changes else {}
            }
        
        return interfaces
    
    def define_module_boundaries(self, module_name: str, boundaries: ModuleBoundary):
        """Define boundaries and rules for a module."""
        query = """
        INSERT OR REPLACE INTO module_boundaries (
            module_name, allowed_dependencies, interface_contracts, isolation_rules
        ) VALUES (?, ?, ?, ?)
        """
        
        self.db.conn.execute(query, [
            module_name,
            json.dumps(boundaries.allowed_dependencies),
            json.dumps(boundaries.interface_contracts),
            json.dumps(boundaries.isolation_rules)
        ])
    
    def _find_relevant_files(self, module_name: str, task_scope: str) -> List[str]:
        """Find files relevant to module and task."""
        # Start with module directory
        module_paths = []
        
        # Look for module in common locations
        search_paths = [
            Path(f"projects/tools/{module_name}"),
            Path(f"projects/core/{module_name}"),
            Path(f"projects/parsers/{module_name}"),
            Path(f"src/{module_name}"),
            Path(module_name)
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                # Add Python files from module
                for py_file in search_path.rglob("*.py"):
                    module_paths.append(str(py_file))
                break
        
        # Add related files based on task scope
        if task_scope in ["test", "testing"]:
            for test_path in Path(".").rglob("test*.py"):
                if module_name in str(test_path):
                    module_paths.append(str(test_path))
        
        return module_paths
    
    def _get_module_dependencies(self, module_name: str) -> List[str]:
        """Analyze module dependencies."""
        dependencies = []
        
        # Look for pyproject.toml in module directory
        module_paths = [
            Path(f"projects/tools/{module_name}"),
            Path(f"projects/core/{module_name}"),
            Path(f"projects/parsers/{module_name}")
        ]
        
        for module_path in module_paths:
            pyproject_path = module_path / "pyproject.toml"
            if pyproject_path.exists():
                try:
                    import tomllib
                    with open(pyproject_path, "rb") as f:
                        config = tomllib.load(f)
                    
                    # Extract dependencies
                    deps = config.get("project", {}).get("dependencies", [])
                    dependencies.extend(deps)
                except Exception:
                    pass
                break
        
        return dependencies
    
    def _get_module_boundaries(self, module_name: str) -> Dict:
        """Get module boundaries from database."""
        query = """
        SELECT allowed_dependencies, interface_contracts, isolation_rules
        FROM module_boundaries WHERE module_name = ?
        """
        
        result = self.db.conn.execute(query, [module_name]).fetchone()
        
        if result:
            return {
                "allowed_dependencies": json.loads(result[0]) if result[0] else [],
                "interface_contracts": json.loads(result[1]) if result[1] else {},
                "isolation_rules": json.loads(result[2]) if result[2] else {}
            }
        
        return {}
    
    def _is_file_relevant(self, file_path: str, relevant_files: List[str]) -> bool:
        """Check if file is relevant to current module context."""
        for relevant_file in relevant_files:
            if file_path in relevant_file or relevant_file in file_path:
                return True
        return False
    
    def _is_change_allowed(self, module_name: str, file_path: str, boundaries: Dict) -> bool:
        """Check if change is allowed within module boundaries."""
        isolation_rules = boundaries.get("isolation_rules", {})
        
        # Check if file is within allowed scope
        allowed_patterns = isolation_rules.get("allowed_file_patterns", [])
        if allowed_patterns:
            for pattern in allowed_patterns:
                if pattern in file_path:
                    return True
            return False
        
        return True  # No restrictions defined
    
    def close(self):
        """Close database connection."""
        self.db.close()