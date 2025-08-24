"""
Learning system for AI development improvement.
Collects feedback, extracts patterns, and suggests improvements.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from knowledge.db_manager import ContextDB


@dataclass
class FeedbackRecord:
    task: str
    result: str
    rating: int
    feedback: str
    module_context: Optional[str] = None


class LearningSystem:
    """Manages learning from user feedback and performance data."""
    
    def __init__(self, db_path: str = "knowledge/context.db"):
        self.db = ContextDB(db_path)
        self._ensure_memory_tables()
    
    def _ensure_memory_tables(self):
        """Ensure memory tables exist in database."""
        try:
            self.db.conn.execute("SELECT 1 FROM learning_data LIMIT 1")
        except Exception:
            from knowledge.schema import CREATE_SCHEMA
            self.db.conn.execute(CREATE_SCHEMA)
    
    def record_feedback(self, task: str, result: str, rating: int, feedback: str = "", module_context: str = None):
        """Record user feedback on task results."""
        query = """
        INSERT INTO learning_data (
            task_type, module_context, input_context, output_result, user_rating, feedback
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        self.db.conn.execute(query, [
            task,
            module_context,
            json.dumps({"task": task, "timestamp": datetime.now().isoformat()}),
            result,
            rating,
            feedback
        ])
    
    def extract_success_patterns(self, min_rating: int = 4) -> Dict:
        """Extract patterns from successful outcomes."""
        query = """
        SELECT task_type, module_context, output_result, user_rating, COUNT(*) as frequency
        FROM learning_data 
        WHERE user_rating >= ?
        GROUP BY task_type, module_context, output_result
        HAVING COUNT(*) >= 2
        ORDER BY frequency DESC, user_rating DESC
        LIMIT 50
        """
        
        results = self.db.conn.execute(query, [min_rating]).fetchall()
        
        patterns = {
            "high_success_tasks": [],
            "module_specific_patterns": {},
            "general_patterns": []
        }
        
        for row in results:
            task_type, module_context, output_result, avg_rating, frequency = row
            
            pattern = {
                "task_type": task_type,
                "output_pattern": output_result[:200],  # Truncate for pattern matching
                "success_frequency": frequency,
                "average_rating": avg_rating
            }
            
            if module_context:
                if module_context not in patterns["module_specific_patterns"]:
                    patterns["module_specific_patterns"][module_context] = []
                patterns["module_specific_patterns"][module_context].append(pattern)
            else:
                patterns["general_patterns"].append(pattern)
            
            if avg_rating >= 4.5:
                patterns["high_success_tasks"].append(pattern)
        
        return patterns
    
    def update_preference_weights(self, feedback: Dict):
        """Update preference weights based on learning data."""
        # This integrates with the PreferenceManager
        try:
            from .preferences import PreferenceManager
            pref_manager = PreferenceManager(self.db.db_path)
            pref_manager.update_preference_weights(feedback)
            pref_manager.close()
        except ImportError:
            pass  # Preferences not available
    
    def suggest_improvements(self, context: str, task_type: str = None) -> List[str]:
        """Suggest improvements based on past performance."""
        suggestions = []
        
        # Find similar contexts with better outcomes
        query = """
        SELECT output_result, user_rating, feedback
        FROM learning_data 
        WHERE (module_context LIKE ? OR task_type LIKE ?)
        AND user_rating >= 4
        ORDER BY user_rating DESC
        LIMIT 10
        """
        
        search_pattern = f"%{context}%"
        task_pattern = f"%{task_type}%" if task_type else "%"
        
        results = self.db.conn.execute(query, [search_pattern, task_pattern]).fetchall()
        
        # Extract common patterns from high-rated results
        successful_patterns = {}
        for row in results:
            output_result, rating, feedback = row
            
            # Simple pattern extraction (could be enhanced with NLP)
            if feedback:
                words = feedback.lower().split()
                for word in words:
                    if len(word) > 3:  # Skip short words
                        if word not in successful_patterns:
                            successful_patterns[word] = 0
                        successful_patterns[word] += rating
        
        # Generate suggestions based on patterns
        top_patterns = sorted(successful_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for pattern, score in top_patterns:
            if score > 8:  # High confidence threshold
                suggestions.append(f"Consider incorporating '{pattern}' based on past success")
        
        # Add context-specific suggestions
        if task_type == "code_generation":
            suggestions.append("Include comprehensive docstrings and type hints")
            suggestions.append("Follow established coding patterns from the module")
        elif task_type == "debugging":
            suggestions.append("Check module boundaries and dependencies")
            suggestions.append("Review recent changes in related modules")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def get_performance_metrics(self, days: int = 30) -> Dict:
        """Get performance metrics for recent period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            AVG(user_rating) as avg_rating,
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN user_rating >= 4 THEN 1 END) as successful_tasks,
            COUNT(DISTINCT task_type) as task_variety,
            COUNT(DISTINCT module_context) as modules_worked
        FROM learning_data 
        WHERE created_at > ?
        """
        
        result = self.db.conn.execute(query, [cutoff_date.isoformat()]).fetchone()
        
        if result:
            avg_rating, total_tasks, successful_tasks, task_variety, modules_worked = result
            
            success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                "period_days": days,
                "average_rating": round(avg_rating, 2) if avg_rating else 0,
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": round(success_rate, 1),
                "task_variety": task_variety,
                "modules_worked": modules_worked
            }
        
        return {"period_days": days, "no_data": True}
    
    def identify_failure_patterns(self, max_rating: int = 2) -> List[Dict]:
        """Identify patterns in failed or low-rated tasks."""
        query = """
        SELECT task_type, module_context, feedback, COUNT(*) as frequency
        FROM learning_data 
        WHERE user_rating <= ?
        AND feedback IS NOT NULL AND feedback != ''
        GROUP BY task_type, module_context, feedback
        HAVING COUNT(*) >= 2
        ORDER BY frequency DESC
        LIMIT 20
        """
        
        results = self.db.conn.execute(query, [max_rating]).fetchall()
        
        failure_patterns = []
        for row in results:
            task_type, module_context, feedback, frequency = row
            
            failure_patterns.append({
                "task_type": task_type,
                "module_context": module_context,
                "common_issue": feedback,
                "frequency": frequency,
                "impact": "high" if frequency >= 5 else "medium"
            })
        
        return failure_patterns
    
    def recommend_alternatives(self, failed_approach: str, context: str = None) -> List[str]:
        """Recommend alternative approaches based on successful patterns."""
        alternatives = []
        
        # Find successful approaches for similar contexts
        query = """
        SELECT DISTINCT output_result, user_rating
        FROM learning_data 
        WHERE user_rating >= 4
        AND (module_context LIKE ? OR ? IS NULL)
        AND output_result NOT LIKE ?
        ORDER BY user_rating DESC
        LIMIT 10
        """
        
        context_pattern = f"%{context}%" if context else None
        failed_pattern = f"%{failed_approach}%"
        
        results = self.db.conn.execute(query, [context_pattern, context_pattern, failed_pattern]).fetchall()
        
        for row in results:
            output_result, rating = row
            
            # Extract key differences (simplified approach)
            if len(output_result) > 20:
                alternatives.append({
                    "approach": output_result[:100] + "..." if len(output_result) > 100 else output_result,
                    "success_rating": rating,
                    "confidence": "high" if rating >= 4.5 else "medium"
                })
        
        return alternatives[:5]  # Return top 5 alternatives
    
    def get_learning_stats(self) -> Dict:
        """Get learning system statistics."""
        stats = {}
        
        # Total feedback records
        result = self.db.conn.execute("SELECT COUNT(*) FROM learning_data").fetchone()
        stats["total_feedback"] = result[0] if result else 0
        
        # Average rating
        result = self.db.conn.execute("SELECT AVG(user_rating) FROM learning_data WHERE user_rating IS NOT NULL").fetchone()
        stats["average_rating"] = round(result[0], 2) if result and result[0] else 0
        
        # Task types covered
        result = self.db.conn.execute("SELECT COUNT(DISTINCT task_type) FROM learning_data").fetchone()
        stats["task_types"] = result[0] if result else 0
        
        # Modules with feedback
        result = self.db.conn.execute("SELECT COUNT(DISTINCT module_context) FROM learning_data WHERE module_context IS NOT NULL").fetchone()
        stats["modules_with_feedback"] = result[0] if result else 0
        
        # Recent activity (last 7 days)
        result = self.db.conn.execute("SELECT COUNT(*) FROM learning_data WHERE created_at > (CURRENT_TIMESTAMP - INTERVAL 7 DAY)").fetchone()
        stats["recent_feedback"] = result[0] if result else 0
        
        return stats
    
    def close(self):
        """Close database connection."""
        self.db.close()