"""
Personal preferences storage for AI development.
Stores coding style, architectural preferences, and quality standards.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

from knowledge.db_manager import ContextDB


@dataclass
class Preference:
    category: str
    key: str
    value: Any
    weight: float = 1.0


class PreferenceManager:
    """Manages user preferences for personalized AI development."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db = ContextDB(db_path)
        self._ensure_memory_tables()
    
    def _ensure_memory_tables(self):
        """Ensure memory tables exist in database."""
        try:
            self.db.conn.execute("SELECT 1 FROM preferences LIMIT 1")
        except Exception:
            from knowledge.schema import CREATE_SCHEMA
            self.db.conn.execute(CREATE_SCHEMA)
    
    def store_coding_style(self, language: str, patterns: Dict):
        """Store coding style preferences for specific language."""
        category = f"coding_style_{language}"
        
        for key, value in patterns.items():
            self._store_preference(category, key, value)
    
    def store_architectural_preferences(self, patterns: Dict):
        """Store architectural patterns and design preferences."""
        category = "architecture"
        
        for key, value in patterns.items():
            self._store_preference(category, key, value)
    
    def store_naming_conventions(self, rules: Dict):
        """Store naming convention preferences."""
        category = "naming"
        
        for key, value in rules.items():
            self._store_preference(category, key, value)
    
    def store_quality_standards(self, standards: Dict):
        """Store quality gates and testing standards."""
        category = "quality"
        
        for key, value in standards.items():
            self._store_preference(category, key, value)
    
    def get_user_preferences(self, context: str = None) -> Dict:
        """Get user preferences, optionally filtered by context."""
        if context:
            query = """
            SELECT category, key, value, weight
            FROM preferences 
            WHERE category LIKE ?
            ORDER BY weight DESC
            """
            results = self.db.conn.execute(query, [f"%{context}%"]).fetchall()
        else:
            query = """
            SELECT category, key, value, weight
            FROM preferences 
            ORDER BY category, weight DESC
            """
            results = self.db.conn.execute(query).fetchall()
        
        preferences = {}
        for row in results:
            category, key, value, weight = row
            
            if category not in preferences:
                preferences[category] = {}
            
            try:
                parsed_value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed_value = value
            
            preferences[category][key] = {
                "value": parsed_value,
                "weight": weight
            }
        
        return preferences
    
    def update_preference_weights(self, feedback: Dict):
        """Update preference weights based on user feedback."""
        for category, items in feedback.items():
            for key, adjustment in items.items():
                query = """
                UPDATE preferences 
                SET weight = weight + ?, updated_at = CURRENT_TIMESTAMP
                WHERE category = ? AND key = ?
                """
                self.db.conn.execute(query, [adjustment, category, key])
    
    def export_preferences(self) -> Dict:
        """Export all preferences for backup or sharing."""
        query = """
        SELECT category, key, value, weight, updated_at
        FROM preferences 
        ORDER BY category, key
        """
        
        results = self.db.conn.execute(query).fetchall()
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "preferences": {}
        }
        
        for row in results:
            category, key, value, weight, updated_at = row
            
            if category not in export_data["preferences"]:
                export_data["preferences"][category] = {}
            
            try:
                parsed_value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed_value = value
            
            export_data["preferences"][category][key] = {
                "value": parsed_value,
                "weight": weight,
                "updated_at": updated_at
            }
        
        return export_data
    
    def import_preferences(self, import_data: Dict, merge: bool = True):
        """Import preferences from backup or sharing."""
        preferences = import_data.get("preferences", {})
        
        if not merge:
            # Clear existing preferences
            self.db.conn.execute("DELETE FROM preferences")
        
        for category, items in preferences.items():
            for key, data in items.items():
                value = data.get("value")
                weight = data.get("weight", 1.0)
                
                self._store_preference(category, key, value, weight)
    
    def get_coding_style_for_language(self, language: str) -> Dict:
        """Get coding style preferences for specific language."""
        preferences = self.get_user_preferences(f"coding_style_{language}")
        return preferences.get(f"coding_style_{language}", {})
    
    def get_architectural_patterns(self) -> Dict:
        """Get architectural pattern preferences."""
        preferences = self.get_user_preferences("architecture")
        return preferences.get("architecture", {})
    
    def get_quality_standards(self) -> Dict:
        """Get quality and testing standards."""
        preferences = self.get_user_preferences("quality")
        return preferences.get("quality", {})
    
    def set_preference(self, category: str, key: str, value: Any, weight: float = 1.0):
        """Set a single preference."""
        self._store_preference(category, key, value, weight)
    
    def get_preference(self, category: str, key: str, default: Any = None) -> Any:
        """Get a single preference value."""
        query = """
        SELECT value FROM preferences 
        WHERE category = ? AND key = ?
        """
        
        result = self.db.conn.execute(query, [category, key]).fetchone()
        
        if result:
            try:
                return json.loads(result[0])
            except (json.JSONDecodeError, TypeError):
                return result[0]
        
        return default
    
    def delete_preference(self, category: str, key: str = None):
        """Delete preference(s)."""
        if key:
            query = "DELETE FROM preferences WHERE category = ? AND key = ?"
            self.db.conn.execute(query, [category, key])
        else:
            query = "DELETE FROM preferences WHERE category = ?"
            self.db.conn.execute(query, [category])
    
    def get_preference_stats(self) -> Dict:
        """Get preference statistics."""
        stats = {}
        
        # Total preferences
        result = self.db.conn.execute("SELECT COUNT(*) FROM preferences").fetchone()
        stats["total_preferences"] = result[0] if result else 0
        
        # Categories
        result = self.db.conn.execute("SELECT COUNT(DISTINCT category) FROM preferences").fetchone()
        stats["categories"] = result[0] if result else 0
        
        # Most weighted preferences
        query = """
        SELECT category, key, weight
        FROM preferences 
        ORDER BY weight DESC
        LIMIT 5
        """
        results = self.db.conn.execute(query).fetchall()
        stats["top_preferences"] = [
            {"category": row[0], "key": row[1], "weight": row[2]}
            for row in results
        ]
        
        return stats
    
    def _store_preference(self, category: str, key: str, value: Any, weight: float = 1.0):
        """Store a preference in the database."""
        # Serialize value to JSON if needed
        if isinstance(value, (dict, list)):
            json_value = json.dumps(value)
        else:
            json_value = json.dumps(value)
        
        query = """
        INSERT OR REPLACE INTO preferences (category, key, value, weight)
        VALUES (?, ?, ?, ?)
        """
        
        self.db.conn.execute(query, [category, key, json_value, weight])
    
    def close(self):
        """Close database connection."""
        self.db.close()