"""
Memory integration layer for Om - coordinates all memory systems.
Provides unified interface for module isolation, session management, and learning.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .module_isolation import ModuleIsolation, ModuleBoundary
from .session_manager import SessionManager
from .preferences import PreferenceManager
from .project_context import ProjectContext
from .learning import LearningSystem


class MemoryIntegration:
    """Unified memory integration for AI development with module isolation."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db_path = db_path
        self.module_isolation = ModuleIsolation(db_path)
        self.session_mgr = SessionManager(db_path)
        self.pref_mgr = PreferenceManager(db_path)
        self.project_ctx = ProjectContext(db_path)
        self.learning_sys = LearningSystem(db_path)
    
    def create_focused_work_environment(self, module: str, task: str) -> Dict:
        """Create focused work environment with module isolation."""
        # Create isolated workspace
        workspace_id = self.module_isolation.create_isolated_workspace(module, task)
        
        # Get filtered context
        context = self.module_isolation.filter_relevant_context(module, task)
        
        # Apply user preferences for this module
        preferences = self.pref_mgr.get_user_preferences(module)
        
        # Get learning suggestions
        suggestions = self.learning_sys.suggest_improvements(module, task)
        
        return {
            "workspace_id": workspace_id,
            "module": module,
            "task": task,
            "context": context,
            "preferences": preferences,
            "suggestions": suggestions,
            "created_at": datetime.now().isoformat()
        }
    
    def inject_context_to_command(self, command: str, args: Dict, module: str = None) -> Dict:
        """Inject relevant context to command execution with module focus."""
        enhanced_args = args.copy()
        
        if module:
            # Get module-specific context
            context = self.module_isolation.filter_relevant_context(module, command)
            enhanced_args["module_context"] = context
            
            # Apply module preferences
            preferences = self.pref_mgr.get_user_preferences(module)
            enhanced_args["preferences"] = preferences
        
        # Add general preferences
        general_prefs = self.pref_mgr.get_user_preferences()
        enhanced_args["general_preferences"] = general_prefs
        
        return enhanced_args
    
    def apply_user_preferences(self, task_context: Dict, module: str = None) -> Dict:
        """Apply user preferences to task context within module boundaries."""
        # Get preferences for module or general
        if module:
            preferences = self.pref_mgr.get_user_preferences(module)
        else:
            preferences = self.pref_mgr.get_user_preferences()
        
        # Apply coding style preferences
        if "coding_style" in preferences:
            task_context["coding_style"] = preferences["coding_style"]
        
        # Apply architectural preferences
        if "architecture" in preferences:
            task_context["architecture_patterns"] = preferences["architecture"]
        
        # Apply quality standards
        if "quality" in preferences:
            task_context["quality_standards"] = preferences["quality"]
        
        return task_context
    
    def suggest_context_aware_commands(self, current_state: Dict, module: str = None) -> List[str]:
        """Suggest commands based on current state and module context."""
        suggestions = []
        
        # Get current task type
        task_type = current_state.get("task_type", "general")
        
        # Module-specific suggestions
        if module:
            # Check if module has active workspace
            context = self.module_isolation.filter_relevant_context(module, task_type)
            
            if context["relevant_files"]:
                suggestions.append(f"om focus {module}")
                suggestions.append(f"om context inject {module}")
            
            # Check for module boundaries
            boundaries = self.module_isolation._get_module_boundaries(module)
            if not boundaries:
                suggestions.append(f"om boundaries define {module}")
        
        # Task-specific suggestions
        if task_type == "debugging":
            suggestions.extend([
                "om analyze dependencies",
                "om find function <error_function>",
                "om session save <project_id>"
            ])
        elif task_type == "development":
            suggestions.extend([
                "om code parse --enhanced",
                "om populate_patterns --enhanced",
                "om preferences show"
            ])
        
        # Learning-based suggestions
        learning_suggestions = self.learning_sys.suggest_improvements(
            module or "general", task_type
        )
        suggestions.extend([f"# {s}" for s in learning_suggestions[:2]])
        
        return suggestions[:8]  # Limit to 8 suggestions
    
    def auto_save_session_state(self, project_id: str, state: Dict, module: str = None):
        """Automatically save session state with module context."""
        # Enhance state with current module context
        if module:
            context = self.module_isolation.filter_relevant_context(module, "session_save")
            state["module_context"] = context
        
        # Save session
        session_id = self.session_mgr.store_session_context(project_id, state, module)
        
        # Update project context
        self.project_ctx.save_project_state(project_id, state)
        
        return session_id
    
    def get_contextual_help(self, command: str, module: str = None) -> str:
        """Get contextual help for command within module scope."""
        help_text = f"Help for '{command}'"
        
        if module:
            help_text += f" in module '{module}'"
            
            # Add module-specific context
            context = self.module_isolation.filter_relevant_context(module, "help")
            if context["relevant_files"]:
                help_text += f"\nRelevant files: {len(context['relevant_files'])} files"
            
            # Add module boundaries info
            boundaries = self.module_isolation._get_module_boundaries(module)
            if boundaries:
                help_text += f"\nModule boundaries: {len(boundaries)} rules defined"
        
        # Add learning insights
        performance = self.learning_sys.get_performance_metrics(7)
        if not performance.get("no_data"):
            help_text += f"\nRecent success rate: {performance.get('success_rate', 0)}%"
        
        return help_text
    
    def personalize_output(self, output: str, preferences: Dict, module: str = None) -> str:
        """Personalize output based on user preferences and module context."""
        # Apply output format preferences
        format_prefs = preferences.get("output", {})
        
        if format_prefs.get("dense", {}).get("value", False):
            # Keep dense format
            return output
        
        if format_prefs.get("verbose", {}).get("value", False):
            # Add more context
            if module:
                output = f"[{module}] {output}"
        
        return output
    
    def enforce_separation_of_concerns(self, module: str, changes: Dict) -> bool:
        """Enforce separation of concerns and module boundaries."""
        return self.module_isolation.enforce_module_boundaries(module, changes)
    
    def manage_module_handoffs(self, from_module: str, to_module: str, context: Dict = None) -> Dict:
        """Manage clean handoffs between modules."""
        handoff_context = context or {}
        
        # Get interface information
        from_interfaces = self.module_isolation.get_cross_module_interfaces(from_module)
        to_interfaces = self.module_isolation.get_cross_module_interfaces(to_module)
        
        # Store handoff record
        query = """
        INSERT INTO module_handoffs (from_module, to_module, handoff_context, interface_changes)
        VALUES (?, ?, ?, ?)
        """
        
        interface_changes = {
            "from_interfaces": from_interfaces,
            "to_interfaces": to_interfaces,
            "timestamp": datetime.now().isoformat()
        }
        
        self.module_isolation.db.conn.execute(query, [
            from_module,
            to_module,
            json.dumps(handoff_context),
            json.dumps(interface_changes)
        ])
        
        return {
            "status": "handoff_completed",
            "from_module": from_module,
            "to_module": to_module,
            "context_transferred": handoff_context,
            "interfaces": interface_changes
        }
    
    def get_memory_stats(self) -> Dict:
        """Get comprehensive memory system statistics."""
        stats = {
            "sessions": self.session_mgr.get_session_stats(),
            "preferences": self.pref_mgr.get_preference_stats(),
            "projects": self.project_ctx.get_project_stats(),
            "learning": self.learning_sys.get_learning_stats()
        }
        
        # Add module isolation stats
        try:
            result = self.module_isolation.db.conn.execute(
                "SELECT COUNT(*) FROM module_workspaces WHERE active = TRUE"
            ).fetchone()
            stats["active_workspaces"] = result[0] if result else 0
            
            result = self.module_isolation.db.conn.execute(
                "SELECT COUNT(DISTINCT module_name) FROM module_workspaces"
            ).fetchone()
            stats["modules_with_workspaces"] = result[0] if result else 0
        except Exception:
            stats["active_workspaces"] = 0
            stats["modules_with_workspaces"] = 0
        
        return stats
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old session and workspace data."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Clean old inactive workspaces
        self.module_isolation.db.conn.execute(
            "DELETE FROM module_workspaces WHERE active = FALSE AND created_at < ?",
            [cutoff_date]
        )
        
        # Clean old sessions (keep recent ones)
        self.module_isolation.db.conn.execute(
            "DELETE FROM sessions WHERE last_accessed < ?",
            [cutoff_date]
        )
    
    def get_current_context(self) -> Dict:
        """Get current context for CLI display."""
        try:
            # Get active modules
            active_modules = []
            if hasattr(self.module_isolation, 'get_active_modules'):
                active_modules = self.module_isolation.get_active_modules()
            
            # Get current session info
            session_info = {}
            if hasattr(self.session_mgr, 'get_current_session'):
                session_info = self.session_mgr.get_current_session() or {}
            
            # Get project context
            project_info = {}
            if hasattr(self.project_ctx, 'get_current_project'):
                project_info = self.project_ctx.get_current_project() or {}
            
            return {
                'modules': active_modules,
                'session_id': session_info.get('id', 'none'),
                'scope': session_info.get('scope', 'global'),
                'project': project_info.get('name', 'none'),
                'workspace': project_info.get('path', 'none')
            }
        except Exception as e:
            return {
                'modules': [],
                'session_id': 'error',
                'scope': 'unknown',
                'project': 'error',
                'workspace': str(e)
            }
    
    def close(self):
        """Close all database connections."""
        self.module_isolation.close()
        self.session_mgr.close()
        self.pref_mgr.close()
        self.project_ctx.close()
        self.learning_sys.close()