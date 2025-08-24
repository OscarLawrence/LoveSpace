"""Task manager for coordinating task workflows."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from .models import Task, TaskStatus, TaskType, TaskPriority, TaskContext, TaskMetrics
from .analyzer import TaskAnalyzer


class TaskManager:
    """Manages tasks with AI-optimized workflows."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(".om_tasks.json")
        self.tasks: Dict[str, Task] = {}
        self.analyzer = TaskAnalyzer()
        self._load_tasks()
    
    def create_task(self, title: str, description: str, **kwargs) -> Task:
        """Create a new task with intelligent analysis."""
        # Analyze task description
        task_type, complexity, scopes = self.analyzer.analyze_task_description(description)
        
        # Create task context
        context = TaskContext(scopes=scopes)
        
        # Create metrics
        effort_points = self.analyzer.estimate_effort(task_type, complexity, description)
        metrics = TaskMetrics(
            complexity_score=complexity,
            effort_points=effort_points
        )
        
        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            task_type=task_type,
            context=context,
            metrics=metrics,
            **kwargs
        )
        
        # Estimate duration (simplified: 30 minutes per effort point)
        task.metrics.estimated_duration = effort_points * 30
        
        # Add suggested dependencies
        suggested_deps = self.analyzer.suggest_dependencies(description)
        task.context.dependencies.extend(suggested_deps)
        
        # Add file patterns
        file_patterns = self.analyzer.extract_file_patterns(description)
        task.context.files.extend(file_patterns)
        
        self.tasks[task.id] = task
        self._save_tasks()
        
        return task
    
    def create_subtask(self, parent_id: str, title: str, description: str = "") -> Task:
        """Create a subtask."""
        parent_task = self.tasks.get(parent_id)
        if not parent_task:
            raise ValueError(f"Parent task {parent_id} not found")
        
        # Inherit properties from parent
        subtask = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description or f"Subtask of: {parent_task.title}",
            task_type=parent_task.task_type,
            priority=parent_task.priority,
            parent_task=parent_id,
            context=TaskContext(scopes=parent_task.context.scopes.copy()),
            metrics=TaskMetrics(
                complexity_score=parent_task.metrics.complexity_score * 0.3,
                effort_points=1
            )
        )
        
        subtask.metrics.estimated_duration = subtask.metrics.effort_points * 30
        
        self.tasks[subtask.id] = subtask
        parent_task.add_subtask(subtask.id)
        self._save_tasks()
        
        return subtask
    
    def update_task(self, task_id: str, **updates) -> Task:
        """Update task properties."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update fields
        for field_name, value in updates.items():
            if hasattr(task, field_name):
                setattr(task, field_name, value)
        
        task.updated_at = datetime.now()
        self._save_tasks()
        
        return task
    
    def start_task(self, task_id: str) -> Task:
        """Start working on a task."""
        task = self.update_task(task_id, status=TaskStatus.IN_PROGRESS)
        task.add_note("Task started")
        return task
    
    def complete_task(self, task_id: str, quality_score: Optional[float] = None) -> Task:
        """Mark task as completed."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Calculate actual duration (simplified)
        if task.status == TaskStatus.IN_PROGRESS:
            task.metrics.actual_duration = task.metrics.estimated_duration
        
        task.status = TaskStatus.COMPLETED
        task.metrics.progress_percentage = 100.0
        
        if quality_score is not None:
            task.metrics.quality_score = quality_score
        
        task.updated_at = datetime.now()
        task.add_note("Task completed")
        
        # Update parent task progress if this is a subtask
        if task.parent_task:
            self._update_parent_progress(task.parent_task)
        
        self._save_tasks()
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None, 
                   task_type: Optional[TaskType] = None,
                   priority: Optional[TaskPriority] = None) -> List[Task]:
        """List tasks with optional filters."""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        # Sort by priority and creation date
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        tasks.sort(key=lambda t: (priority_order.get(t.priority, 2), t.created_at))
        return tasks
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active (non-completed, non-cancelled) tasks."""
        return [
            task for task in self.tasks.values()
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        ]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return [task for task in self.tasks.values() if task.is_overdue()]
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics."""
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return {"total": 0}
        
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        
        total_effort = 0
        completed_effort = 0
        
        for task in self.tasks.values():
            # Status counts
            status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1
            
            # Type counts
            type_counts[task.task_type.value] = type_counts.get(task.task_type.value, 0) + 1
            
            # Priority counts
            priority_counts[task.priority.value] = priority_counts.get(task.priority.value, 0) + 1
            
            # Effort tracking
            total_effort += task.metrics.effort_points
            if task.status == TaskStatus.COMPLETED:
                completed_effort += task.metrics.effort_points
        
        completion_rate = (completed_effort / total_effort * 100) if total_effort > 0 else 0
        
        return {
            "total": total_tasks,
            "by_status": status_counts,
            "by_type": type_counts,
            "by_priority": priority_counts,
            "total_effort_points": total_effort,
            "completed_effort_points": completed_effort,
            "completion_rate": completion_rate,
            "overdue_count": len(self.get_overdue_tasks())
        }
    
    def _update_parent_progress(self, parent_id: str):
        """Update parent task progress based on subtasks."""
        parent = self.tasks.get(parent_id)
        if not parent or not parent.subtasks:
            return
        
        completed_subtasks = 0
        total_subtasks = len(parent.subtasks)
        
        for subtask_id in parent.subtasks:
            subtask = self.tasks.get(subtask_id)
            if subtask and subtask.status == TaskStatus.COMPLETED:
                completed_subtasks += 1
        
        progress = (completed_subtasks / total_subtasks * 100) if total_subtasks > 0 else 0
        parent.update_progress(progress)
        
        # If all subtasks are complete, complete the parent
        if progress >= 100.0:
            parent.status = TaskStatus.COMPLETED
            parent.add_note("All subtasks completed")
    
    def _load_tasks(self):
        """Load tasks from storage."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            for task_data in data.get('tasks', []):
                # Convert datetime strings back to datetime objects
                task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
                task_data['updated_at'] = datetime.fromisoformat(task_data['updated_at'])
                
                if task_data.get('due_date'):
                    task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
                
                # Convert enums
                task_data['status'] = TaskStatus(task_data['status'])
                task_data['priority'] = TaskPriority(task_data['priority'])
                task_data['task_type'] = TaskType(task_data['task_type'])
                
                # Reconstruct nested objects
                task_data['context'] = TaskContext(**task_data['context'])
                task_data['metrics'] = TaskMetrics(**task_data['metrics'])
                
                task = Task(**task_data)
                self.tasks[task.id] = task
                
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def _save_tasks(self):
        """Save tasks to storage."""
        try:
            tasks_data = []
            for task in self.tasks.values():
                task_dict = asdict(task)
                
                # Convert datetime objects to strings
                task_dict['created_at'] = task.created_at.isoformat()
                task_dict['updated_at'] = task.updated_at.isoformat()
                
                if task.due_date:
                    task_dict['due_date'] = task.due_date.isoformat()
                else:
                    task_dict['due_date'] = None
                
                # Convert enums to values
                task_dict['status'] = task.status.value
                task_dict['priority'] = task.priority.value
                task_dict['task_type'] = task.task_type.value
                
                tasks_data.append(task_dict)
            
            data = {'tasks': tasks_data}
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            
            # Remove from parent's subtasks if it's a subtask
            if task.parent_task and task.parent_task in self.tasks:
                parent = self.tasks[task.parent_task]
                if task_id in parent.subtasks:
                    parent.subtasks.remove(task_id)
            
            # Delete all subtasks
            for subtask_id in task.subtasks.copy():
                self.delete_task(subtask_id)
            
            del self.tasks[task_id]
            self._save_tasks()
            return True
        
        return False