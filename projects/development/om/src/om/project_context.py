"""
Project context persistence for tracking project evolution and decisions.
Maintains complete project state and architectural decision records.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from knowledge.db_manager import ContextDB


@dataclass
class ProjectState:
    project_id: str
    state_data: Dict
    architecture_decisions: Dict
    module_structure: Dict
    created_at: datetime
    updated_at: datetime


class ProjectContext:
    """Manages project context persistence and evolution tracking."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db = ContextDB(db_path)
        self._ensure_memory_tables()
    
    def _ensure_memory_tables(self):
        """Ensure memory tables exist in database."""
        try:
            self.db.conn.execute("SELECT 1 FROM project_states LIMIT 1")
        except Exception:
            from knowledge.schema import CREATE_SCHEMA
            self.db.conn.execute(CREATE_SCHEMA)
    
    def save_project_state(self, project_id: str, state: Dict) -> bool:
        """Save complete project state with module structure."""
        # Enhance state with metadata
        enhanced_state = {
            "files": state.get("files", []),
            "active_modules": state.get("active_modules", []),
            "current_tasks": state.get("current_tasks", []),
            "dependencies": state.get("dependencies", {}),
            "architecture_overview": state.get("architecture_overview", ""),
            "last_modified": datetime.now().isoformat()
        }
        
        # Extract module structure
        module_structure = self._analyze_module_structure(state)
        
        # Store or update project state
        query = """
        INSERT OR REPLACE INTO project_states (
            project_id, state_data, module_structure, updated_at
        ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        try:
            self.db.conn.execute(query, [
                project_id,
                json.dumps(enhanced_state),
                json.dumps(module_structure)
            ])
            return True
        except Exception:
            return False
    
    def load_project_state(self, project_id: str) -> Dict:
        """Load complete project state."""
        query = """
        SELECT state_data, architecture_decisions, module_structure, created_at, updated_at
        FROM project_states 
        WHERE project_id = ?
        """
        
        result = self.db.conn.execute(query, [project_id]).fetchone()
        
        if not result:
            return {"status": "not_found", "project_id": project_id}
        
        state_data, arch_decisions, module_structure, created_at, updated_at = result
        
        return {
            "status": "loaded",
            "project_id": project_id,
            "state": json.loads(state_data) if state_data else {},
            "architecture_decisions": json.loads(arch_decisions) if arch_decisions else {},
            "module_structure": json.loads(module_structure) if module_structure else {},
            "created_at": created_at,
            "updated_at": updated_at
        }
    
    def track_project_evolution(self, project_id: str, changes: Dict):
        """Track project evolution and changes over time."""
        # Store evolution data in learning system
        evolution_data = {
            "project_id": project_id,
            "change_type": changes.get("type", "unknown"),
            "modules_affected": changes.get("modules", []),
            "files_changed": changes.get("files", []),
            "impact_level": changes.get("impact", "medium"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in learning_data table for pattern analysis
        query = """
        INSERT INTO learning_data (
            task_type, module_context, input_context, output_result
        ) VALUES (?, ?, ?, ?)
        """
        
        self.db.conn.execute(query, [
            "project_evolution",
            json.dumps(changes.get("modules", [])),
            json.dumps(changes),
            json.dumps(evolution_data)
        ])
    
    def get_project_history(self, project_id: str) -> List[Dict]:
        """Get project evolution history."""
        query = """
        SELECT input_context, output_result, created_at
        FROM learning_data 
        WHERE task_type = 'project_evolution' 
        AND output_result LIKE ?
        ORDER BY created_at DESC
        LIMIT 50
        """
        
        results = self.db.conn.execute(query, [f'%"project_id": "{project_id}"%']).fetchall()
        
        history = []
        for row in results:
            input_context, output_result, created_at = row
            try:
                change_data = json.loads(input_context)
                evolution_data = json.loads(output_result)
                
                history.append({
                    "changes": change_data,
                    "evolution": evolution_data,
                    "timestamp": created_at
                })
            except json.JSONDecodeError:
                continue
        
        return history
    
    def store_architectural_decisions(self, project_id: str, decisions: Dict):
        """Store architectural decision records (ADRs)."""
        # Get current project state
        current_state = self.load_project_state(project_id)
        
        if current_state["status"] == "not_found":
            # Create new project state
            self.save_project_state(project_id, {})
            current_decisions = {}
        else:
            current_decisions = current_state.get("architecture_decisions", {})
        
        # Add new decisions with timestamps
        for decision_id, decision in decisions.items():
            current_decisions[decision_id] = {
                **decision,
                "recorded_at": datetime.now().isoformat(),
                "status": decision.get("status", "proposed")
            }
        
        # Update project state with new decisions
        query = """
        UPDATE project_states 
        SET architecture_decisions = ?, updated_at = CURRENT_TIMESTAMP
        WHERE project_id = ?
        """
        
        self.db.conn.execute(query, [
            json.dumps(current_decisions),
            project_id
        ])
    
    def get_related_projects(self, project_id: str) -> List[str]:
        """Find related projects based on similar patterns."""
        # Get current project's module structure
        current_project = self.load_project_state(project_id)
        if current_project["status"] == "not_found":
            return []
        
        current_modules = set(current_project.get("module_structure", {}).keys())
        
        # Find projects with similar module structures
        query = """
        SELECT project_id, module_structure
        FROM project_states 
        WHERE project_id != ?
        """
        
        results = self.db.conn.execute(query, [project_id]).fetchall()
        
        related_projects = []
        for row in results:
            other_project_id, module_structure_json = row
            
            try:
                other_modules = set(json.loads(module_structure_json).keys())
                
                # Calculate similarity (Jaccard index)
                intersection = len(current_modules & other_modules)
                union = len(current_modules | other_modules)
                
                if union > 0:
                    similarity = intersection / union
                    if similarity > 0.3:  # 30% similarity threshold
                        related_projects.append({
                            "project_id": other_project_id,
                            "similarity": similarity,
                            "common_modules": list(current_modules & other_modules)
                        })
            except json.JSONDecodeError:
                continue
        
        # Sort by similarity
        related_projects.sort(key=lambda x: x["similarity"], reverse=True)
        return related_projects[:10]  # Return top 10
    
    def archive_project(self, project_id: str):
        """Archive project (mark as inactive but keep data)."""
        # Add archive flag to project state
        current_state = self.load_project_state(project_id)
        if current_state["status"] == "loaded":
            state_data = current_state["state"]
            state_data["archived"] = True
            state_data["archived_at"] = datetime.now().isoformat()
            
            self.save_project_state(project_id, state_data)
    
    def get_project_stats(self) -> Dict:
        """Get project statistics."""
        stats = {}
        
        # Total projects
        result = self.db.conn.execute("SELECT COUNT(*) FROM project_states").fetchone()
        stats["total_projects"] = result[0] if result else 0
        
        # Active projects (not archived)
        query = """
        SELECT COUNT(*) FROM project_states 
        WHERE state_data NOT LIKE '%"archived": true%'
        """
        result = self.db.conn.execute(query).fetchone()
        stats["active_projects"] = result[0] if result else 0
        
        # Recent activity
        query = """
        SELECT COUNT(*) FROM project_states 
        WHERE updated_at > (CURRENT_TIMESTAMP - INTERVAL 7 DAY)
        """
        result = self.db.conn.execute(query).fetchone()
        stats["recently_updated"] = result[0] if result else 0
        
        return stats
    
    def _analyze_module_structure(self, state: Dict) -> Dict:
        """Analyze and extract module structure from project state."""
        structure = {}
        
        # Analyze files to determine module structure
        files = state.get("files", [])
        for file_path in files:
            if isinstance(file_path, str) and file_path.endswith(".py"):
                # Extract module path
                parts = file_path.split("/")
                if len(parts) > 1:
                    module_name = parts[-2] if parts[-2] != "src" else parts[-3]
                    
                    if module_name not in structure:
                        structure[module_name] = {
                            "files": [],
                            "type": "unknown"
                        }
                    
                    structure[module_name]["files"].append(file_path)
        
        # Determine module types based on common patterns
        for module_name, module_data in structure.items():
            files = module_data["files"]
            
            if any("test" in f for f in files):
                module_data["type"] = "test"
            elif any("cli" in f for f in files):
                module_data["type"] = "cli"
            elif any("parser" in f for f in files):
                module_data["type"] = "parser"
            elif any("db" in f or "database" in f for f in files):
                module_data["type"] = "database"
            else:
                module_data["type"] = "core"
        
        return structure
    
    def close(self):
        """Close database connection."""
        self.db.close()