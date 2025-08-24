"""
Session management system for AI development continuity.
Stores and restores complete project state across AI instances.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from knowledge.db_manager import ContextDB


@dataclass
class SessionContext:
    id: str
    project_id: str
    module_name: Optional[str]
    context_data: Dict
    isolated_workspace_id: Optional[str]
    created_at: datetime
    last_accessed: datetime


class SessionManager:
    """Manages session persistence and restoration for AI development."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db = ContextDB(db_path)
        self._ensure_memory_tables()
    
    def _ensure_memory_tables(self):
        """Ensure memory tables exist in database."""
        try:
            self.db.conn.execute("SELECT 1 FROM sessions LIMIT 1")
        except Exception:
            from knowledge.schema import CREATE_SCHEMA
            self.db.conn.execute(CREATE_SCHEMA)
    
    def store_session_context(self, project_id: str, context_data: Dict, module_name: str = None) -> str:
        """Store current session context with module isolation."""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        # Include current workspace state
        enhanced_context = {
            "project_state": context_data,
            "active_files": context_data.get("active_files", []),
            "current_task": context_data.get("current_task", ""),
            "decision_history": context_data.get("decision_history", []),
            "module_context": context_data.get("module_context", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        query = """
        INSERT INTO sessions (
            id, project_id, module_name, context_data, isolated_workspace_id
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        workspace_id = context_data.get("isolated_workspace_id")
        
        self.db.conn.execute(query, [
            session_id,
            project_id,
            module_name,
            json.dumps(enhanced_context),
            workspace_id
        ])
        
        return session_id
    
    def restore_session_context(self, project_id: str, module_name: str = None) -> Dict:
        """Restore complete session state for project and module."""
        query = """
        SELECT id, context_data, isolated_workspace_id, created_at, last_accessed
        FROM sessions 
        WHERE project_id = ? AND (module_name = ? OR module_name IS NULL)
        ORDER BY last_accessed DESC
        LIMIT 1
        """
        
        result = self.db.conn.execute(query, [project_id, module_name]).fetchone()
        
        if not result:
            return {"status": "no_session_found", "project_id": project_id}
        
        session_id, context_data, workspace_id, created_at, last_accessed = result
        
        # Update last accessed time
        self.db.conn.execute(
            "UPDATE sessions SET last_accessed = CURRENT_TIMESTAMP WHERE id = ?",
            [session_id]
        )
        
        context = json.loads(context_data) if context_data else {}
        
        return {
            "status": "restored",
            "session_id": session_id,
            "project_id": project_id,
            "module_name": module_name,
            "context": context,
            "workspace_id": workspace_id,
            "created_at": created_at,
            "last_accessed": last_accessed
        }
    
    def track_user_decisions(self, decision_type: str, choice: str, outcome: str, module_name: str = None):
        """Track user decisions and outcomes for learning."""
        query = """
        INSERT INTO decisions (decision_type, module_name, context, choice, outcome)
        VALUES (?, ?, ?, ?, ?)
        """
        
        context = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "module": module_name
        })
        
        self.db.conn.execute(query, [
            decision_type,
            module_name,
            context,
            choice,
            outcome
        ])
    
    def get_decision_patterns(self, decision_type: str, module_name: str = None) -> List[Dict]:
        """Get patterns from past decisions for specific context."""
        query = """
        SELECT choice, outcome, success_rating, created_at
        FROM decisions 
        WHERE decision_type = ? AND (module_name = ? OR module_name IS NULL)
        ORDER BY created_at DESC
        LIMIT 20
        """
        
        results = self.db.conn.execute(query, [decision_type, module_name]).fetchall()
        
        patterns = []
        for row in results:
            choice, outcome, rating, created_at = row
            patterns.append({
                "choice": choice,
                "outcome": outcome,
                "success_rating": rating,
                "created_at": created_at
            })
        
        return patterns
    
    def clear_session(self, project_id: str, module_name: str = None):
        """Clear session data for project/module."""
        if module_name:
            query = "DELETE FROM sessions WHERE project_id = ? AND module_name = ?"
            self.db.conn.execute(query, [project_id, module_name])
        else:
            query = "DELETE FROM sessions WHERE project_id = ?"
            self.db.conn.execute(query, [project_id])
    
    def list_active_sessions(self) -> List[str]:
        """List all active session project IDs."""
        query = """
        SELECT DISTINCT project_id, module_name, last_accessed
        FROM sessions 
        ORDER BY last_accessed DESC
        """
        
        results = self.db.conn.execute(query).fetchall()
        
        sessions = []
        for row in results:
            project_id, module_name, last_accessed = row
            session_key = f"{project_id}:{module_name}" if module_name else project_id
            sessions.append({
                "key": session_key,
                "project_id": project_id,
                "module_name": module_name,
                "last_accessed": last_accessed
            })
        
        return sessions
    
    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        stats = {}
        
        # Total sessions
        result = self.db.conn.execute("SELECT COUNT(*) FROM sessions").fetchone()
        stats["total_sessions"] = result[0] if result else 0
        
        # Active projects
        result = self.db.conn.execute("SELECT COUNT(DISTINCT project_id) FROM sessions").fetchone()
        stats["active_projects"] = result[0] if result else 0
        
        # Decisions tracked
        result = self.db.conn.execute("SELECT COUNT(*) FROM decisions").fetchone()
        stats["decisions_tracked"] = result[0] if result else 0
        
        return stats
    
    def save_session(self, project_id: str, module: str = None) -> Dict:
        """Save session with enhanced context capture."""
        import os
        import time
        from pathlib import Path
        
        # Capture comprehensive workspace state
        context_data = {
            "current_task": f"session_save_{project_id}",
            "active_files": self._get_recent_files(),
            "decision_history": [],
            "module_context": {"module": module} if module else {},
            "workspace_path": os.getcwd(),
            "git_status": self._get_git_status(),
            "handover_files": self._get_handover_files(),
            "timestamp": time.time(),
            "session_metadata": {
                "pid": os.getpid(),
                "auto_save": True
            }
        }
        
        session_id = self.store_session_context(project_id, context_data, module)
        
        return {
            "session_id": session_id,
            "modules_saved": 1 if module else 0,
            "size_mb": len(str(context_data)) / (1024 * 1024)
        }
    
    def restore_session(self, project_id: str, module: str = None) -> Dict:
        """Restore session with enhanced context."""
        result = self.restore_session_context(project_id, module)
        
        if result.get("status") == "restored":
            result.update({
                "modules_restored": 1 if module else 0,
                "timestamp": result.get("created_at", "unknown")
            })
        
        return result
    
    def list_sessions(self) -> List[Dict]:
        """List sessions in expected format."""
        sessions = self.list_active_sessions()
        
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                "project_id": session["project_id"],
                "session_id": session["key"],
                "module_count": 1 if session["module_name"] else 0,
                "created": session["last_accessed"],
                "size_mb": 0.1  # Estimate
            })
        
        return formatted_sessions
    
    def _get_recent_files(self) -> List[str]:
        """Get recently modified files."""
        import time
        recent_files = []
        try:
            for root, dirs, files in os.walk("."):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                for file in files:
                    if file.endswith(('.py', '.json', '.md', '.txt')):
                        file_path = os.path.join(root, file)
                        try:
                            if time.time() - os.path.getmtime(file_path) < 3600:
                                recent_files.append(file_path)
                        except OSError:
                            continue
            return sorted(recent_files, key=lambda x: os.path.getmtime(x), reverse=True)[:10]
        except Exception:
            return []
    
    def _get_git_status(self) -> Dict:
        """Get git status."""
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {"modified_files": result.stdout.strip().split('\n') if result.stdout.strip() else []}
        except Exception:
            pass
        return {"status": "not_available"}
    
    def _get_handover_files(self) -> List[Dict]:
        """Get handover files."""
        import json
        from pathlib import Path
        handover_files = []
        try:
            for file in Path(".").glob("handover_*.json"):
                with open(file, 'r') as f:
                    handover_files.append({"file": str(file), "content": json.load(f)})
        except Exception:
            pass
        return handover_files

    def get_current_session_id(self) -> Optional[str]:
        """Get the current active session ID."""
        query = """
        SELECT id FROM sessions 
        ORDER BY last_accessed DESC 
        LIMIT 1
        """
        result = self.db.conn.execute(query).fetchone()
        return result[0] if result else None
    
    def get_current_session(self) -> Dict:
        """Get current active session data."""
        session_id = self.get_current_session_id()
        if not session_id:
            return {"status": "no_active_session"}
        
        query = """
        SELECT project_id, module_name, context_data, created_at, last_accessed
        FROM sessions WHERE id = ?
        """
        result = self.db.conn.execute(query, [session_id]).fetchone()
        
        if not result:
            return {"status": "session_not_found"}
        
        project_id, module_name, context_data, created_at, last_accessed = result
        context = json.loads(context_data) if context_data else {}
        
        return {
            "status": "active",
            "session_id": session_id,
            "project_id": project_id,
            "module_name": module_name,
            "context": context,
            "created_at": created_at,
            "last_accessed": last_accessed
        }

    def close(self):
        """Close database connection."""
        self.db.close()